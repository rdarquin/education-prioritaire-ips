"""Forme de la distribution de l'ecart d'IPS au seuil budgetaire.

La variable est a INFLATION DE ZEROS : neuf colleges sur dix sont conformes et
valent exactement 0. Une distribution brute serait donc un pic unique entoure
de barres invisibles. Deux precautions la rendent lisible sans rien dissimuler :

    - la barre du zero est TRONQUEE, et son effectif reel annote ;
    - les classes sont calees pour que zero tombe AU CENTRE d'une barre. Sans
      cela, les conformes se repartiraient sur deux barres voisines et la masse
      centrale apparaitrait deux fois plus petite qu'elle n'est.

Le score est affiche SIGNE : negatif pour une sur-inclusion, positif pour un
oubli. La couleur reprend la convention du projet — bleu pour les
sur-inclusions, orange pour les oublis — l'axe portant deja le signe, le
redoublement est ici voulu : il relie la figure aux cartes.

Les deux variantes de seuil sont superposees, aplat pour le seuil national et
trait pour le seuil academique. La comparaison montre ou le changement d'etalon
agit : sur la queue, non sur le centre.

UN TABLEAU SOUS LE GRAPHE

Une barre tronquee et une echelle asymetrique se lisent mal au chiffre pres. Le
tableau donne donc la repartition en pourcentage sur cinq plages, pour les deux
variantes de seuil. Les bornes sont SYMETRIQUES autour de zero (+/- 3 et
+/- 10) : la plage centrale reunit les colleges conformes et ceux dont l'ecart
reste sous le seuil d'interpretabilite de la DEPP, et les quatre autres se
repondent deux a deux. Toute asymetrie lue dans le tableau est donc une
propriete des donnees, jamais du decoupage.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.distribution_ecart
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES, PROJECT_ROOT
from src.etalons import ETALONS, fichier_scores, nom_figure

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Seuil d'interpretabilite de l'IPS recommande par la DEPP. Sert ici de repere
# visuel et de borne interieure du tableau, pas de filtre : la figure montre
# toute la distribution.
SEUIL_INTERPRETABLE = 3.0
SEUIL_FORT = 10.0

# Largeur de classe de l'histogramme. L'IPS s'etale sur une centaine de
# points, le score de sixieme sur plusieurs centaines : le pas suit l'echelle
# de l'etalon, sans quoi l'histogramme du score aurait des centaines de barres.
PAS_PAR_ETALON = {"ips": 1.0, "eval6": 4.0}

BLEU, ORANGE = "#1f3b73", "#eb6834"
BLEU_CLAIR, ORANGE_CLAIR = "#5588cc", "#f2a888"
ENCRE, GRILLE, MUET, ENCRE_2 = "#0b0b0b", "#e1e0d9", "#898781", "#52514e"

VARIANTES = [("score_ecart", "type_ecart", "national"),
             ("score_ecart_academie", "type_ecart_academie", "académique")]

# Libelle, couleur de l'en-tete. L'ordre suit l'axe des abscisses, de la
# sur-inclusion la plus forte a l'oubli le plus fort.
PLAGES = [("moins de −10", BLEU),
          ("−10 à −3", BLEU_CLAIR),
          ("−3 à +3", MUET),
          ("+3 à +10", ORANGE_CLAIR),
          ("plus de +10", ORANGE)]


def charger(cle: str) -> pd.DataFrame:
    """Lit le fichier des scores d'un etalon, produit par `score_ecart.py`."""
    fichier = DOSSIER_TABLES / fichier_scores(cle)
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.score_ecart")
    return pd.read_csv(fichier)


def signer(df: pd.DataFrame, col_score: str, col_type: str) -> np.ndarray:
    """Score signe : positif pour un oubli, negatif pour une sur-inclusion.

    Le score brut est une valeur absolue ; c'est la colonne de type qui porte
    le sens de l'ecart. Les reunir en une seule variable signee permet de
    tracer les deux cotes sur un meme axe.
    """
    return np.select(
        [df[col_type] == "oublie", df[col_type] == "sur-inclus"],
        [df[col_score], -df[col_score]], default=0.0)


def repartir(valeurs: np.ndarray) -> np.ndarray:
    """Part de colleges, en %, dans chacune des cinq plages d'ecart.

    Les conditions sont testees dans l'ordre et la plage centrale vient en
    premier : elle est definie par |ecart| <= 3, ce qui la rend exactement
    symetrique. Les quatre autres s'en deduisent par le signe et par le
    franchissement de 10. Aucune borne n'est ainsi attribuee deux fois, et le
    decoupage ne peut pas fabriquer d'asymetrie.
    """
    absolu = np.abs(valeurs)
    indices = np.select(
        [absolu <= SEUIL_INTERPRETABLE,
         (valeurs < 0) & (absolu > SEUIL_FORT),
         valeurs < 0,
         valeurs > SEUIL_FORT],
        [2, 0, 1, 4],
        default=3)
    effectifs = np.bincount(indices, minlength=len(PLAGES))
    return 100 * effectifs / len(valeurs)


def resumer(df: pd.DataFrame) -> None:
    """Affiche la composition de la distribution, par variante."""
    print(f"\n{'=' * 84}")
    print(f"DISTRIBUTION DE L'ECART D'IPS — {len(df)} colleges publics")
    print("=" * 84)

    for col_score, _, libelle in VARIANTES:
        s = df[col_score]
        nul = int((s == 0).sum())
        non_nuls = s[s > 0]
        q = non_nuls.quantile([0.5, 0.75, 0.9, 0.99]).round(2)
        print(f"\n  seuil {libelle:11s} : nul {nul:>5} "
              f"({100 * nul / len(df):>4.1f} %) | non nuls : "
              f"med {q[0.5]:>5.2f}  Q3 {q[0.75]:>5.2f}  D9 {q[0.9]:>5.2f}  "
              f"C99 {q[0.99]:>5.2f}  max {non_nuls.max():>5.1f}")

    print(f"\n{'-' * 84}")
    print("REPARTITION PAR PLAGE D'ECART, EN % DES COLLEGES")
    print("-" * 84)
    entetes = [libelle.replace("−", "-") for libelle, _ in PLAGES]
    print(f"{'seuil':14s}" + "".join(f"{e:>15s}" for e in entetes))
    for col_score, col_type, libelle in VARIANTES:
        parts = repartir(signer(df, col_score, col_type))
        print(f"{libelle:14s}" + "".join(f"{p:>14.1f}%" for p in parts))


def tableau(fig, df: pd.DataFrame, position: list) -> None:
    """Dessine sous le graphe la repartition en % par plage, pour les 2 seuils.

    Le tableau est trace a la main plutot qu'avec `ax.table` : on veut des
    en-tetes colores reprenant la convention de la figure, un filet unique
    sous l'en-tete et aucune bordure, ce que le composant standard ne permet
    pas sans le defaire entierement.
    """
    ax = fig.add_axes(position)
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Colonne de libelles a gauche, puis cinq colonnes de valeurs reparties
    # sur l'espace restant.
    x_libelle = 0.0
    x_colonnes = np.linspace(0.30, 0.96, len(PLAGES))
    y_entete, y_lignes = 0.82, [0.46, 0.14]

    ax.text(x_libelle, y_entete, "Écart d'IPS", fontsize=8,
            fontweight="bold", color=ENCRE_2, va="center")
    for x, (libelle, couleur) in zip(x_colonnes, PLAGES):
        ax.text(x, y_entete, libelle, fontsize=8, fontweight="bold",
                color=couleur, ha="center", va="center")

    ax.plot([0, 1], [0.66, 0.66], color=GRILLE, linewidth=1.2)

    for y, (col_score, col_type, libelle) in zip(y_lignes, VARIANTES):
        parts = repartir(signer(df, col_score, col_type))
        ax.text(x_libelle, y, f"Seuil {libelle}", fontsize=8.5,
                color=ENCRE_2, va="center")
        for x, part, (_, couleur) in zip(x_colonnes, parts, PLAGES):
            # La plage centrale concentre neuf colleges sur dix : elle est mise
            # en gras pour qu'on ne la confonde pas avec les quatre autres.
            centrale = couleur == MUET
            ax.text(x, y, f"{part:.1f} %".replace(".", ","), fontsize=9,
                    fontweight="bold" if centrale else "normal",
                    color=ENCRE if centrale else ENCRE_2,
                    ha="center", va="center")


def figure(df: pd.DataFrame, cle: str, etalon: dict) -> None:
    """Produit l'histogramme de l'ecart signe, et le tableau qui l'accompagne."""
    national = signer(df, "score_ecart", "type_ecart")
    academique = signer(df, "score_ecart_academie", "type_ecart_academie")

    pas = PAS_PAR_ETALON[cle]
    sujet = etalon["avec_article"][0].upper() + etalon["avec_article"][1:]
    seuil_txt = (f"{df['seuil'].iloc[0]:.{etalon['decimales']}f} points"
                 .replace(".", ","))
    justification = etalon["justification_seuil"]
    borne = max(np.abs(national).max(), np.abs(academique).max())
    # Bornes decalees d'un demi-pas pour que zero tombe au centre d'une classe.
    bins = np.arange(-borne - pas, borne + 2 * pas, pas) - pas / 2

    fig, ax = plt.subplots(figsize=(10, 8.0))
    # La marge basse doit loger l'etiquette d'axe sur deux lignes, le tableau
    # et la note : d'ou une valeur inhabituellement grande.
    fig.subplots_adjust(left=0.085, right=0.975, top=0.865, bottom=0.44)

    ax.hist(national[national < 0], bins=bins, color=BLEU, alpha=0.8,
            linewidth=0, label="Sur-inclusions (seuil national)")
    ax.hist(national[national > 0], bins=bins, color=ORANGE, alpha=0.8,
            linewidth=0, label="Oublis (seuil national)")
    ax.hist(academique, bins=bins, histtype="step", color=ENCRE, linewidth=1.1,
            label="Seuil académique")

    # Plafond cale sur la plus haute barre NON nulle : la barre du zero est
    # tronquee, sans quoi elle ecraserait tout le reste.
    hors_zero = national[national != 0]
    plafond = np.histogram(hors_zero, bins=bins)[0].max() * 1.35
    ax.set_ylim(0, plafond)

    n_nuls = int((national == 0).sum())
    ax.bar(0, plafond, width=pas * 0.9, color=MUET, alpha=0.35, linewidth=0,
           zorder=0)
    ax.annotate(f"{n_nuls:,}".replace(",", " ") + " conformes\n"
                f"({100 * n_nuls / len(df):.1f} %)\nbarre tronquée",
                xy=(0, plafond), xytext=(6, -6), textcoords="offset points",
                ha="left", va="top", fontsize=7.5, color=ENCRE_2)

    for borne_seuil in (-SEUIL_INTERPRETABLE, SEUIL_INTERPRETABLE):
        ax.axvline(borne_seuil, color=MUET, linewidth=0.9, linestyle="--")

    ax.set_xlabel(f"Écart {etalon['de_article']} au seuil budgétaire\n"
                  "← sur-inclusion          conforme          oubli →",
                  fontsize=9)
    ax.set_ylabel("Nombre de collèges", fontsize=9)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(True, linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)

    tableau(fig, df, [0.085, 0.250, 0.89, 0.100])

    fig.suptitle(f"Distribution de l'écart {etalon['de_article']} au seuil "
                 f"budgétaire",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.978)
    fig.text(0.02, 0.948,
             "Neuf collèges sur dix sont conformes et valent exactement zéro : la "
             "barre centrale est tronquée pour que le reste de la\n"
             "distribution reste lisible, son effectif étant annoté. Les pointillés "
             f"marquent ± {SEUIL_INTERPRETABLE:.0f} points. {justification}",
             fontsize=8.5, va="top", color=ENCRE_2)

    fig.text(0.02, 0.200,
             "Les plages du tableau sont symétriques autour de zéro : une asymétrie "
             "entre les deux moitiés est une propriété des données,\n"
             "non du découpage. La plage centrale réunit les collèges conformes et "
             "ceux dont l'écart reste sous le seuil d'interprétabilité.\n"
             f"Lecture : le seuil budgétaire est la valeur {etalon['de_article']} "
             f"du collège qui ferme l'enveloppe réellement allouée — "
             f"{seuil_txt} au niveau national.\n"
             "Le trait noir donne la même distribution lorsque le seuil est recalculé "
             "académie par académie.\n"
             f"Champ : collèges publics, rentrée 2024-2025. {sujet} n'est pas le "
             "critère officiel de classement : un écart mesure un\n"
             "désaccord entre deux instruments, pas une erreur administrative.\n"
             f"Sources : {etalon['source']}, annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / nom_figure("distribution_ecart", cle)
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def main() -> None:
    for cle, etalon in ETALONS.items():
        df = charger(cle)
        resumer(df)
        figure(df, cle, etalon)


if __name__ == "__main__":
    main()
