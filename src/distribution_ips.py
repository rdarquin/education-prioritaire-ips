"""Distribution des IPS des colleges publics, et position des seuils.

La figure repond a une question simple : ou tombent les seuils budgetaires dans
la distribution reelle des IPS ?

    - l'histogramme montre les 5 325 colleges publics, empiles par statut
      (hors education prioritaire, REP, REP+) ;
    - un trait epais marque le SEUIL NATIONAL, c'est-a-dire l'IPS du college
      qui ferme l'enveloppe : il y a autant de colleges sous ce trait que de
      colleges classes ;
    - une bande claire couvre l'etendue des SEUILS ACADEMIQUES, et un peigne
      sous l'axe donne leur position une a une.

CE QUE LA FIGURE REND VISIBLE

Le seuil n'est pas une frontiere nette dans les donnees. La distribution des
IPS est continue et dense a l'endroit ou le seuil tombe : deplacer celui-ci
d'un point fait donc basculer beaucoup de colleges. C'est la raison pour
laquelle ce projet a abandonne les mesures a seuil conventionnel au profit
d'un seuil deduit de l'enveloppe.

L'etendue des seuils academiques est le second enseignement : selon l'academie,
le meme IPS place un college d'un cote ou de l'autre de la barre.

Le statut est une variable ORDONNEE — hors EP, REP, REP+ marquent une
intensite croissante du dispositif — donc rendue par une seule teinte du clair
au fonce, et non par des couleurs distinctes.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.distribution_ips
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Largeur de classe, en points d'IPS.
PAS = 2.0

# Statut, libelle, couleur. L'ordre va du moins au plus intense : c'est une
# variable ordonnee, une palette categorielle suggererait le contraire.
STATUTS = [("hors EP", "Hors éducation prioritaire", "#d8d7d0"),
           ("REP", "REP", "#f2a888"),
           ("REP+", "REP+", "#eb6834")]

# Academies dont le seuil est nomme sur le peigne : les deux extremes, qui
# bornent l'etendue. Les vingt-huit autres y figurent sans etiquette — c'est
# leur nombre et leur dispersion qui importent, pas leur identite.
ACADEMIES_NOMMEES = ["STRASBOURG", "PARIS"]

ENCRE, ENCRE_2, GRILLE, MUET = "#0b0b0b", "#52514e", "#e1e0d9", "#898781"


def charger() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lit les scores par college et les seuils par academie."""
    for nom in ("score_ecart_ips.csv", "score_ecart_par_academie.csv"):
        if not (DOSSIER_TABLES / nom).exists():
            raise FileNotFoundError(
                f"{nom} absent. Lance d'abord : uv run python -m src.score_ecart")

    colleges = pd.read_csv(DOSSIER_TABLES / "score_ecart_ips.csv")
    academies = pd.read_csv(DOSSIER_TABLES / "score_ecart_par_academie.csv")
    return colleges, academies


def resumer(colleges: pd.DataFrame, academies: pd.DataFrame) -> None:
    """Affiche les reperes que la figure porte."""
    seuil = float(colleges["ips_seuil"].iloc[0])
    classes = int((colleges["ep"] != "hors EP").sum())

    print(f"\n{'=' * 78}")
    print(f"DISTRIBUTION DES IPS — {len(colleges)} colleges publics")
    print("=" * 78)
    print(f"\n  IPS : min {colleges['ips'].min():.1f}  "
          f"Q1 {colleges['ips'].quantile(.25):.1f}  "
          f"mediane {colleges['ips'].median():.1f}  "
          f"Q3 {colleges['ips'].quantile(.75):.1f}  "
          f"max {colleges['ips'].max():.1f}")
    print(f"  seuil national : {seuil:.2f}  "
          f"({int((colleges['ips'] < seuil).sum())} colleges en dessous, "
          f"{classes} classes)")

    # Densite au voisinage du seuil : c'est elle qui rend tout seuil fragile.
    proches = int(((colleges["ips"] - seuil).abs() <= 2).sum())
    print(f"  colleges a moins de 2 points du seuil : {proches} "
          f"({100 * proches / len(colleges):.1f} %)")

    s = academies["seuil_academique"]
    bas = academies.loc[s.idxmin(), "academie"]
    haut = academies.loc[s.idxmax(), "academie"]
    print(f"\n  seuils academiques : de {s.min():.1f} ({bas}) "
          f"a {s.max():.1f} ({haut}) — etendue {s.max() - s.min():.1f} points")
    print(f"  {int((s < seuil).sum())} academies sous le seuil national, "
          f"{int((s > seuil).sum())} au-dessus")

    print(f"\n{'-' * 78}")
    print("REPARTITION DES COLLEGES PAR STATUT")
    print("-" * 78)
    for statut, libelle, _ in STATUTS:
        sous = colleges[colleges["ep"] == statut]
        print(f"  {libelle:28s} {len(sous):>5d} colleges  "
              f"IPS median {sous['ips'].median():6.1f}  "
              f"etendue {sous['ips'].min():.1f} - {sous['ips'].max():.1f}")


def figure(colleges: pd.DataFrame, academies: pd.DataFrame) -> None:
    """Histogramme des IPS empile par statut, avec les seuils en reperes."""
    seuil_national = float(colleges["ips_seuil"].iloc[0])
    seuils = academies.set_index("academie")["seuil_academique"]
    etendue = f"{seuils.max() - seuils.min():.1f}".replace(".", ",")
    bornes = f"{seuils.min():.1f} à {seuils.max():.1f}".replace(".", ",")

    bins = np.arange(np.floor(colleges["ips"].min()),
                     np.ceil(colleges["ips"].max()) + PAS, PAS)

    fig, (ax, peigne) = plt.subplots(
        2, 1, figsize=(11, 7.8), sharex=True,
        gridspec_kw=dict(height_ratios=[9, 1.5], hspace=0.10))
    fig.subplots_adjust(left=0.075, right=0.975, top=0.845, bottom=0.245)

    # ---- bande des seuils academiques, sous l'histogramme ----------------
    ax.axvspan(seuils.min(), seuils.max(), color=GRILLE, alpha=0.7,
               linewidth=0, zorder=0)

    # ---- histogramme empile ----------------------------------------------
    ax.hist([colleges.loc[colleges["ep"] == statut, "ips"]
             for statut, _, _ in STATUTS],
            bins=bins, stacked=True,
            color=[couleur for _, _, couleur in STATUTS],
            label=[libelle for _, libelle, _ in STATUTS],
            linewidth=0)

    ax.axvline(seuil_national, color=ENCRE, linewidth=1.8, zorder=4)
    hauteur = ax.get_ylim()[1]
    ax.annotate(f"Seuil national {seuil_national:.2f}".replace(".", ","),
                xy=(seuil_national, hauteur * 0.97), xytext=(-8, 0),
                textcoords="offset points", ha="right", va="top",
                fontsize=8.5, fontweight="bold", color=ENCRE)
    ax.annotate("autant de collèges à gauche\nque de collèges classés",
                xy=(seuil_national, hauteur * 0.86), xytext=(-8, 0),
                textcoords="offset points", ha="right", va="top",
                fontsize=7.5, color=ENCRE_2)

    # Callee en haut du cadre : a mi-hauteur, l'etiquette tomberait dans les
    # barres, la distribution etant encore dense au-dela de 102.
    ax.annotate("étendue des seuils\nacadémiques : " + bornes,
                xy=(seuils.max(), hauteur * 0.97), xytext=(9, 0),
                textcoords="offset points", ha="left", va="top",
                fontsize=7.5, color=ENCRE_2)

    ax.set_ylabel("Nombre de collèges", fontsize=9)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.grid(True, axis="y", linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)

    # ---- peigne des seuils academiques -----------------------------------
    peigne.set_ylim(0, 1)
    peigne.set_yticks([])
    for bord in ["top", "right", "left"]:
        peigne.spines[bord].set_visible(False)
    peigne.spines["bottom"].set_color(MUET)

    for nom, valeur in seuils.items():
        nomme = nom in ACADEMIES_NOMMEES
        peigne.plot([valeur, valeur], [0.45, 1.0],
                    color=ENCRE_2 if nomme else MUET,
                    linewidth=1.1 if nomme else 0.7, zorder=2)

    peigne.plot([seuil_national, seuil_national], [0.45, 1.0],
                color=ENCRE, linewidth=1.8, zorder=3)

    # Trois etiquettes seulement, assez espacees pour tenir sur une ligne.
    etiquettes = [(seuils[nom], nom.title(), ENCRE_2, "normal")
                  for nom in ACADEMIES_NOMMEES]
    etiquettes.append((seuil_national, "National", ENCRE, "bold"))

    for valeur, texte, couleur, graisse in etiquettes:
        peigne.annotate(texte, xy=(valeur, 0.32), xytext=(0, -1),
                        textcoords="offset points", ha="center", va="top",
                        fontsize=7.5, color=couleur, fontweight=graisse)

    peigne.set_xlabel("IPS du collège", fontsize=9)
    peigne.annotate(f"{len(seuils)} seuils académiques", xy=(0.995, 0.95),
                    xycoords="axes fraction", ha="right", va="top",
                    fontsize=7.5, color=MUET, style="italic")

    ax.set_xlim(bins[0], bins[-1])

    fig.suptitle("Où tombent les seuils dans la distribution des IPS",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.945,
             "Les 5 325 collèges publics, empilés selon leur statut. Le seuil "
             "budgétaire est l'IPS du collège qui ferme l'enveloppe : il y a\n"
             "exactement autant de collèges à sa gauche que de collèges classés. "
             "Le peigne du bas donne les 30 seuils académiques.",
             fontsize=8.5, va="top", color=ENCRE_2)

    fig.text(0.02, 0.155,
             "Deux lectures. Le seuil tombe dans une zone DENSE de la distribution : "
             "le déplacer d'un point ferait basculer des dizaines de collèges,\n"
             "ce qui rend fragile toute mesure fondée sur un seuil conventionnel.\n"
             f"L'étendue des seuils académiques atteint {etendue} points : selon "
             "l'académie, un même IPS place un collège d'un côté ou de l'autre "
             "de la barre.\n"
             "Champ : collèges publics, rentrée 2024-2025. L'IPS n'est pas le critère "
             "officiel de classement : le seuil est reconstitué à partir du nombre\n"
             "de collèges classés.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "distribution_ips.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def main() -> None:
    colleges, academies = charger()
    resumer(colleges, academies)
    figure(colleges, academies)


if __name__ == "__main__":
    main()
