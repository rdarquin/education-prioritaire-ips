"""Les sur-inclusions les plus fortes : ou sont-elles, et de quelle ampleur ?

Champ : colleges publics SUR-INCLUS au seuil budgetaire NATIONAL, c'est-a-dire
classes REP ou REP+ alors que leur IPS depasse l'IPS de l'etablissement qui
ferme l'enveloppe nationale (88,80 points). On ne retient que les ecarts d'au
moins 10 points, soit plus de trois fois le seuil d'interpretabilite de 3 points
recommande par la DEPP : ce sont les cas qu'aucune imprecision de mesure ne peut
expliquer.

Deux figures :

    sur_inclusions_academies.png - barres empilees, un barreau par academie,
                                   decoupe en trois plages d'ecart.
    sur_inclusions_departements.png - carte, effectif inscrit sur chaque
                                   departement concerne.

Les plages sont ORDONNEES (10-15 < 15-20 < 20+), donc rendues par une seule
teinte du clair au fonce, et non par des couleurs distinctes : une palette
categorielle suggererait des categories sans ordre.

RESERVE, valable pour les deux figures. Le seuil est national, or l'enveloppe
d'education prioritaire a ete repartie par academie avant que les recteurs ne
designent les etablissements. Une part de ces sur-inclusions est donc
arithmetiquement forcee : une academie dont peu d'etablissements passent sous
le seuil national ne peut pas remplir son enveloppe autrement. C'est le cas de
Paris. La variante academique du score, disponible dans le meme fichier, neutralise
cet effet.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.sur_inclusions
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap

from src.cartographie import annoter_drom, charger_contours
from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

ECART_MINIMAL = 10.0

# Bornes inferieure et superieure, et libelle. La derniere plage est ouverte.
PLAGES = [(10.0, 15.0, "10 à 15 points"),
          (15.0, 20.0, "15 à 20 points"),
          (20.0, np.inf, "plus de 20 points")]

# Teintes d'une meme couleur, du clair au fonce : la variable est ordinale.
# Le bleu reprend la convention des autres figures, ou il designe la
# sur-inclusion.
TEINTES = ["#a8c4e8", "#5588cc", "#1f3b73"]

ENCRE_2, GRILLE, MUET, GRIS_ABSENT = "#52514e", "#e1e0d9", "#898781", "#eeeeee"


def charger_sur_inclus() -> pd.DataFrame:
    """Colleges sur-inclus d'au moins ECART_MINIMAL points, avec leur plage."""
    fichier = DOSSIER_TABLES / "score_ecart_ips.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.score_ecart")

    df = pd.read_csv(fichier, dtype={"code_departement": str, "code_commune": str})
    sous = df[(df["niveau"] == "college")
              & (df["type_ecart"] == "sur-inclus")
              & (df["score_ecart_ips"] >= ECART_MINIMAL)].copy()

    sous["plage"] = pd.cut(
        sous["score_ecart_ips"],
        bins=[b for b, _, _ in PLAGES] + [np.inf],
        labels=[libelle for _, _, libelle in PLAGES],
        right=False)  # borne basse incluse : 15,0 va dans "15 a 20"
    return sous


def figure_academies(sous: pd.DataFrame) -> None:
    """Barres empilees : effectif par academie, decoupe par plage d'ecart."""
    table = (pd.crosstab(sous["academie"], sous["plage"])
             .reindex(columns=[libelle for _, _, libelle in PLAGES], fill_value=0))
    table["total"] = table.sum(axis=1)
    table = table.sort_values("total")  # barh empile du bas vers le haut

    fig, ax = plt.subplots(figsize=(10, 0.46 * len(table) + 3.0))
    fig.subplots_adjust(left=0.20, right=0.97, top=0.855, bottom=0.185)

    gauche = np.zeros(len(table))
    for (_, _, libelle), couleur in zip(PLAGES, TEINTES):
        ax.barh(table.index, table[libelle], left=gauche, color=couleur,
                height=0.72, label=libelle, linewidth=0)
        gauche += table[libelle].to_numpy()

    for y, total in enumerate(table["total"]):
        ax.annotate(str(int(total)), xy=(total, y), xytext=(5, 0),
                    textcoords="offset points", va="center", fontsize=8.5,
                    color=ENCRE_2, fontweight="bold")

    ax.set_xlim(0, table["total"].max() * 1.18)
    # Marge verticale resserree : la marge par defaut de matplotlib laisse une
    # bande vide au-dessus du premier barreau et sous le dernier.
    ax.set_ylim(-0.75, len(table) - 0.25)
    ax.set_xlabel("Nombre de collèges publics sur-inclus", fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right",
              title="Écart d'IPS au seuil national", title_fontsize=8.5)
    ax.grid(True, axis="x", linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right", "left"]:
        ax.spines[bord].set_visible(False)

    fig.suptitle("Collèges classés dont l'IPS dépasse largement le seuil national",
                 fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.945,
             f"Collèges publics classés REP ou REP+ dont l'IPS dépasse d'au moins "
             f"{ECART_MINIMAL:.0f} points celui de l'établissement qui ferme "
             f"l'enveloppe nationale (88,80 points),\n"
             f"soit plus de trois fois le seuil de 3 points en deçà duquel la DEPP "
             f"recommande de ne pas interpréter une différence d'IPS.",
             fontsize=8.5, va="top", color=ENCRE_2)
    fig.text(0.02, 0.095,
             "L'enveloppe d'éducation prioritaire est répartie par académie avant que "
             "les recteurs ne désignent les établissements : une académie comptant peu "
             "de collèges sous le seuil\n"
             "national ne peut pas remplir son enveloppe autrement, et une part de ces "
             "sur-inclusions est donc arithmétiquement forcée. C'est le cas de Paris.\n"
             "Champ : collèges publics, rentrée 2024-2025. L'IPS n'est pas le critère "
             "officiel de classement : un écart mesure un désaccord entre deux "
             "instruments, pas une erreur administrative.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "sur_inclusions_academies.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def figure_departements(sous: pd.DataFrame, contours) -> None:
    """Carte : effectif inscrit directement sur chaque departement concerne."""
    par_dep = sous.groupby("code_departement").size().rename("effectif")
    gdf = contours.join(par_dep, how="left")
    gdf["effectif"] = gdf["effectif"].fillna(0)

    concernes = gdf["effectif"] > 0
    maximum = int(gdf["effectif"].max())

    # Classes entieres : l'effectif est un comptage, une rampe continue
    # suggererait des valeurs intermediaires qui n'existent pas.
    bornes = np.array([0.5, 1.5, 2.5, 3.5, maximum + 0.5])
    cmap = ListedColormap(TEINTES + ["#0b2350"])
    norme = BoundaryNorm(bornes, ncolors=cmap.N)

    fig, ax = plt.subplots(figsize=(9, 10.2))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.145)

    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.4)
    gdf[concernes].plot(ax=ax, column="effectif", cmap=cmap, norm=norme,
                        edgecolor="white", linewidth=0.4)

    # L'effectif est ecrit sur le departement. Le blanc devient illisible sur
    # les teintes claires : la couleur du texte suit donc l'intensite du fond.
    for code, ligne in gdf[concernes].iterrows():
        point = ligne["geometry"].representative_point()
        effectif = int(ligne["effectif"])
        ax.annotate(str(effectif), xy=(point.x, point.y), ha="center",
                    va="center", fontsize=7.5, fontweight="bold",
                    color="white" if effectif >= 2 else "#0b0b0b")

    annoter_drom(ax, contours)
    ax.set_axis_off()

    # Legende en haut a droite : le coin inferieur droit est occupe par la
    # Corse, dont l'effectif serait masque.
    poignees = [plt.Rectangle((0, 0), 1, 1, color=c) for c in cmap.colors]
    etiquettes = ["1 collège", "2", "3", f"4 à {maximum}"]
    ax.legend(poignees, etiquettes, loc="upper right", frameon=False,
              fontsize=8.5, title="Collèges sur-inclus", title_fontsize=8.5)

    fig.suptitle("Où se trouvent les collèges classés dont l'IPS dépasse\n"
                 "le seuil national de plus de 10 points",
                 fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.10,
             f"{int(gdf['effectif'].sum())} collèges publics dans "
             f"{int(concernes.sum())} départements. En gris, les départements sans "
             f"aucun cas.\n"
             "L'enveloppe étant répartie par académie avant désignation des "
             "établissements, une part de ces sur-inclusions est arithmétiquement "
             "forcée :\n"
             "voir la figure par académie. Champ : collèges publics, rentrée "
             "2024-2025. L'IPS n'est pas le critère officiel de classement.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation, contours "
             "Insee/cartiflette. DROM rapprochés, échelles et distances non "
             "respectées.",
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / "sur_inclusions_departements.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    sous = charger_sur_inclus()
    print(f"{len(sous)} colleges publics sur-inclus d'au moins "
          f"{ECART_MINIMAL:.0f} points")
    print(sous["plage"].value_counts().reindex(
        [libelle for _, _, libelle in PLAGES]).to_string())

    print("\n--- par academie ---")
    table = pd.crosstab(sous["academie"], sous["plage"])
    table["total"] = table.sum(axis=1)
    print(table.sort_values("total", ascending=False).to_string())

    print("\n--- par departement ---")
    dep = (sous.groupby(["code_departement", "departement"]).size()
           .rename("colleges").reset_index().sort_values("colleges",
                                                         ascending=False))
    print(dep.to_string(index=False))

    print("\nContours :")
    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    print(f"  {len(contours)} departements")

    print("\nFigures :")
    figure_academies(sous)
    figure_departements(sous, contours)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    colonnes = ["uai", "nom", "nom_commune", "departement", "academie", "ep",
                "ips", "ips_seuil", "score_ecart_ips", "plage"]
    chemin = DOSSIER_TABLES / "sur_inclusions_fortes.csv"
    sous.sort_values("score_ecart_ips", ascending=False)[colonnes].to_csv(
        chemin, index=False, encoding="utf-8")
    print(f"\n[+] {chemin.name} ({len(sous)} collèges)")


if __name__ == "__main__":
    main()
