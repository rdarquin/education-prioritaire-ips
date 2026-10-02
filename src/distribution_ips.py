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
from src.noms import academie
from src.etalons import (ETALONS, fichier_academies, fichier_scores,
                         nom_figure)

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Largeur de classe, en points d'IPS.
# Le pas d'histogramme depend de l'echelle de l'etalon : il est defini
# dans `etalons.py`, sous la cle `pas_histogramme`.

# Statut, libelle, couleur. L'ordre va du moins au plus intense : c'est une
# variable ordonnee, une palette categorielle suggererait le contraire.
STATUTS = [("hors EP", "Hors éducation prioritaire", "#d8d7d0"),
           ("REP", "REP", "#f2a888"),
           ("REP+", "REP+", "#eb6834")]

# Les academies nommees sur le peigne sont les deux EXTREMES, calculees et non
# ecrites en dur : elles changent d'un etalon a l'autre — Strasbourg et Paris
# bornent les seuils d'IPS, Mayotte et Paris ceux du score de sixieme. Les
# vingt-huit autres figurent sans etiquette, c'est leur dispersion qui importe.

ENCRE, ENCRE_2, GRILLE, MUET = "#0b0b0b", "#52514e", "#e1e0d9", "#898781"


def charger(cle: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lit les scores par college et les seuils par academie, pour un etalon."""
    fichiers = (fichier_scores(cle), fichier_academies(cle))
    for nom in fichiers:
        if not (DOSSIER_TABLES / nom).exists():
            raise FileNotFoundError(
                f"{nom} absent. Lance d'abord : uv run python -m src.score_ecart")

    colleges = pd.read_csv(DOSSIER_TABLES / fichiers[0])
    academies = pd.read_csv(DOSSIER_TABLES / fichiers[1])
    return colleges, academies


def resumer(colleges: pd.DataFrame, academies: pd.DataFrame,
            etalon: dict) -> None:
    """Affiche les reperes que la figure porte."""
    seuil = float(colleges["seuil"].iloc[0])
    classes = int((colleges["ep"] != "hors EP").sum())

    print(f"\n{'=' * 78}")
    print(f"DISTRIBUTION — {etalon['libelle_long'].upper()} — "
          f"{len(colleges)} colleges publics")
    print("=" * 78)
    print(f"\n  {etalon['libelle']} : min {colleges['valeur'].min():.1f}  "
          f"Q1 {colleges['valeur'].quantile(.25):.1f}  "
          f"mediane {colleges['valeur'].median():.1f}  "
          f"Q3 {colleges['valeur'].quantile(.75):.1f}  "
          f"max {colleges['valeur'].max():.1f}")
    print(f"  seuil national : {seuil:.2f}  "
          f"({int((colleges['valeur'] < seuil).sum())} colleges en dessous, "
          f"{classes} classes)")

    # Densite au voisinage du seuil : c'est elle qui rend tout seuil fragile.
    proches = int(((colleges["valeur"] - seuil).abs() <= 2).sum())
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
              f"median {sous['valeur'].median():6.1f}  "
              f"etendue {sous['valeur'].min():.1f} - {sous['valeur'].max():.1f}")


def figure(colleges: pd.DataFrame, academies: pd.DataFrame,
           cle: str, etalon: dict) -> None:
    """Histogramme des IPS empile par statut, avec les seuils en reperes."""
    seuil_national = float(colleges["seuil"].iloc[0])
    seuils = academies.set_index("academie")["seuil_academique"]
    nommees = [seuils.idxmin(), seuils.idxmax()]
    etendue = f"{seuils.max() - seuils.min():.1f}".replace(".", ",")
    bornes = f"{seuils.min():.1f} à {seuils.max():.1f}".replace(".", ",")

    pas = etalon["pas_histogramme"]
    bins = np.arange(np.floor(colleges["valeur"].min()),
                     np.ceil(colleges["valeur"].max()) + pas, pas)

    fig, (ax, peigne) = plt.subplots(
        2, 1, figsize=(11, 7.8), sharex=True,
        gridspec_kw=dict(height_ratios=[9, 1.5], hspace=0.10))
    fig.subplots_adjust(left=0.075, right=0.975, top=0.845, bottom=0.245)

    # ---- bande des seuils academiques, sous l'histogramme ----------------
    ax.axvspan(seuils.min(), seuils.max(), color=GRILLE, alpha=0.7,
               linewidth=0, zorder=0)

    # ---- histogramme empile ----------------------------------------------
    ax.hist([colleges.loc[colleges["ep"] == statut, "valeur"]
             for statut, _, _ in STATUTS],
            bins=bins, stacked=True,
            color=[couleur for _, _, couleur in STATUTS],
            label=[libelle for _, libelle, _ in STATUTS],
            linewidth=0)

    ax.axvline(seuil_national, color=ENCRE, linewidth=1.8, zorder=4)
    hauteur = ax.get_ylim()[1]
    dec = etalon["decimales"]
    ax.annotate(f"Seuil national {seuil_national:.{dec}f}".replace(".", ","),
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
        nomme = nom in nommees
        peigne.plot([valeur, valeur], [0.45, 1.0],
                    color=ENCRE_2 if nomme else MUET,
                    linewidth=1.1 if nomme else 0.7, zorder=2)

    peigne.plot([seuil_national, seuil_national], [0.45, 1.0],
                color=ENCRE, linewidth=1.8, zorder=3)

    # Trois etiquettes seulement, assez espacees pour tenir sur une ligne.
    etiquettes = [(seuils[nom], academie(nom), ENCRE_2, "normal")
                  for nom in nommees]
    etiquettes.append((seuil_national, "National", ENCRE, "bold"))

    for valeur, texte, couleur, graisse in etiquettes:
        peigne.annotate(texte, xy=(valeur, 0.32), xytext=(0, -1),
                        textcoords="offset points", ha="center", va="top",
                        fontsize=7.5, color=couleur, fontweight=graisse)

    peigne.set_xlabel(etalon["axe"], fontsize=9)
    peigne.annotate(f"{len(seuils)} seuils académiques", xy=(0.995, 0.95),
                    xycoords="axes fraction", ha="right", va="top",
                    fontsize=7.5, color=MUET, style="italic")

    ax.set_xlim(bins[0], bins[-1])

    fig.suptitle(f"Où tombent les seuils dans la distribution "
                 f"{etalon['de_article']}",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)
    effectif = f"{len(colleges):,}".replace(",", " ")
    # "l'IPS" -> "L'IPS" : `capitalize` minusculerait le reste du mot.
    sujet = etalon["avec_article"][0].upper() + etalon["avec_article"][1:]
    fig.text(0.02, 0.945,
             f"Les {effectif} collèges publics, empilés selon leur statut. Le "
             f"seuil budgétaire est la valeur {etalon['de_article']} du collège "
             f"qui ferme l'enveloppe :\n"
             "il y a exactement autant de collèges à sa gauche que de collèges "
             "classés. Le peigne du bas donne les 30 seuils académiques.",
             fontsize=8.5, va="top", color=ENCRE_2)

    fig.text(0.02, 0.155,
             "Deux lectures. Le seuil tombe dans une zone DENSE de la distribution : "
             "le déplacer d'un point ferait basculer des dizaines de collèges,\n"
             "ce qui rend fragile toute mesure fondée sur un seuil conventionnel.\n"
             f"L'étendue des seuils académiques atteint {etendue} points : selon "
             f"l'académie, une même valeur {etalon['de_article']} place un collège "
             "d'un côté ou de l'autre de la barre.\n"
             f"Champ : collèges publics, rentrée 2024-2025. {sujet} n'est pas "
             "le critère officiel de classement : le seuil est reconstitué à "
             "partir du nombre\n"
             "de collèges classés.\n"
             f"Sources : {etalon['source']}, annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / nom_figure("distribution_ips", cle)
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def main() -> None:
    for cle, etalon in ETALONS.items():
        colleges, academies = charger(cle)
        resumer(colleges, academies, etalon)
        figure(colleges, academies, cle, etalon)


if __name__ == "__main__":
    main()
