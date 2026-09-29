"""Les ecarts les plus forts au seuil budgetaire national, des deux cotes.

Champ : les CINQUANTE plus gros ecarts de chaque type, au seuil NATIONAL
(88,80 points). Le classement se fait sur l'ampleur de l'ecart, non sur un
seuil fixe.

Consequence a connaitre : les deux tops ne couvrent pas la meme etendue. Du
cote des sur-inclusions, le cinquantieme s'ecarte de 7,7 points ; du cote des
oublis, de 5,7 points seulement. Un effectif constant des deux cotes impose
donc d'aller chercher des ecarts plus faibles chez les oublis — c'est une
autre facon de constater que les sur-inclusions sont plus amples.

Deux types d'ecart, traites symetriquement :

    SUR-INCLUSION - college classe REP ou REP+ dont l'IPS DEPASSE le seuil.
    OUBLI         - college non classe dont l'IPS est INFERIEUR au seuil.

Pour chacun, une carte portant l'effectif de chaque departement concerne. Les
repartitions par academie et par plage d'ecart restent imprimees dans la
console et exportees en CSV : elles nourrissent le commentaire du README sans
qu'une figure leur soit consacree.

La teinte des cartes reprend la convention suivie dans tout le projet : BLEU
pour les sur-inclusions, ORANGE pour les oublis. L'effectif etant un comptage,
l'echelle est decoupee en classes entieres et non en rampe continue.

RESERVE, valable pour les deux cartes. Le seuil est national, or l'enveloppe
d'education prioritaire a ete repartie par academie avant que les recteurs ne
designent les etablissements. Une part de ces ecarts est donc arithmetiquement
forcee, dans les deux sens : une academie comptant moins de colleges sous le
seuil national que de places a pourvoir ne peut pas eviter de sur-inclure
(Paris), et celle qui en compte davantage ne peut pas eviter d'oublier (Lille).
La variante academique du score, produite par `score_ecart.py` dans le meme
fichier, neutralise cet effet.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.ecarts_extremes
"""

import textwrap

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap

from src.cartographie import annoter_drom, charger_contours
from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

TOP_N = 50
SEUIL_NATIONAL = 88.80

# Bornes inferieure et superieure, et libelle. La derniere plage est ouverte.
# Les plages ne sont plus tracees ; elles restent utilisees par le recapitulatif
# imprime en console et par la colonne `plage` du CSV exporte.
PLAGES = [(0.0, 10.0, "moins de 10 points"),
          (10.0, 15.0, "10 à 15 points"),
          (15.0, 20.0, "15 à 20 points"),
          (20.0, np.inf, "plus de 20 points")]

# Un reglage par type d'ecart. `teintes_carte` donne les classes d'effectif de
# la carte, du clair au fonce : l'effectif est une grandeur ordonnee.
TYPES = {
    "sur-inclus": dict(
        radical="sur_inclusions",
        teintes_carte=["#a8c4e8", "#5588cc", "#1f3b73", "#0b2350"],
        # A partir de cet effectif, le fond est assez sombre pour porter du
        # texte blanc. Les deux rampes ne s'assombrissent pas au meme rythme.
        texte_blanc_des=2,
        titre_carte=("Où se trouvent les 50 collèges classés dont l'IPS\n"
                     "dépasse le plus le seuil national"),
        legende_carte="Collèges sur-inclus",
        contrainte=(
            "L'enveloppe d'éducation prioritaire est répartie par académie avant que "
            "les recteurs ne désignent les établissements : une académie comptant "
            "moins de collèges sous le seuil\nnational que de places à pourvoir ne "
            "peut pas éviter de sur-inclure, et une part de ces cas est donc "
            "arithmétiquement forcée. C'est la situation de Paris."),
    ),
    "oublie": dict(
        radical="oublis",
        teintes_carte=["#f6c5ac", "#ee8e56", "#c9551d", "#7a2f0e"],
        texte_blanc_des=3,
        titre_carte=("Où se trouvent les 50 collèges non classés dont l'IPS\n"
                     "est le plus sous le seuil national"),
        legende_carte="Collèges oubliés",
        contrainte=(
            "L'enveloppe d'éducation prioritaire est répartie par académie avant que "
            "les recteurs ne désignent les établissements : une académie comptant "
            "plus de collèges sous le seuil\nnational que de places à pourvoir ne "
            "peut pas éviter d'en oublier, et une part de ces cas est donc "
            "arithmétiquement forcée. C'est la situation de Lille."),
    ),
}

ENCRE_2, GRIS_ABSENT = "#52514e", "#eeeeee"

RESERVE_CARTE = ("Champ : collèges publics, rentrée 2024-2025. L'IPS n'est pas le "
                 "critère officiel de classement.\n"
                 "Sources : DEPP (IPS), annuaire de l'éducation, contours "
                 "Insee/cartiflette. DROM rapprochés, échelles et distances non "
                 "respectées.")

# Largeur de ligne des notes de carte, en caracteres. Les coupures ecrites a
# la main dans les textes sont calees sur la largeur des diagrammes (10 pouces)
# et debordent des cartes (9 pouces) : on les recalcule.
LARGEUR_NOTE_CARTE = 125


def replier(texte: str, largeur: int = LARGEUR_NOTE_CARTE) -> str:
    """Reenveloppe un texte a une largeur donnee, coupures existantes ignorees."""
    return textwrap.fill(" ".join(texte.split()), width=largeur)


def charger(type_ecart: str) -> pd.DataFrame:
    """Les TOP_N plus gros ecarts d'un type donne, avec leur plage.

    La selection se fait sur le RANG et non sur un seuil : les deux types sont
    ainsi representes par un effectif identique, ce qui rend les cartes
    directement comparables. En contrepartie, les deux tops ne couvrent pas la
    meme etendue d'ecart — c'est la rancon d'un effectif constant, et le
    sous-titre de chaque figure le precise.
    """
    fichier = DOSSIER_TABLES / "score_ecart_ips.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.score_ecart")

    df = pd.read_csv(fichier, dtype={"code_departement": str, "code_commune": str})
    sous = df[df["type_ecart"] == type_ecart].nlargest(
        TOP_N, "score_ecart_ips").copy()

    sous["plage"] = pd.cut(
        sous["score_ecart_ips"],
        bins=[b for b, _, _ in PLAGES] + [np.inf],
        labels=[libelle for _, _, libelle in PLAGES],
        right=False)  # borne basse incluse : 15,0 va dans "15 a 20"
    return sous


def classes_effectif(maximum: int, reglage: dict) -> tuple:
    """Bornes, couleurs et etiquettes d'une echelle de comptage.

    L'effectif est un entier : une rampe continue suggererait des valeurs
    intermediaires qui n'existent pas. Les classes s'arretent au maximum
    observe, sans quoi la legende annoncerait des categories vides — un
    departement a 11 colleges et un autre a 3 n'appellent pas le meme decoupage.
    """
    paliers = [0.5, 1.5, 2.5, 3.5]
    bornes = np.array([b for b in paliers if b < maximum] + [maximum + 0.5])
    couleurs = reglage["teintes_carte"][:len(bornes) - 1]

    etiquettes = [f"{n} collège" + ("s" if n > 1 else "")
                  for n in range(1, len(bornes) - 1)]
    dernier = len(bornes) - 1
    etiquettes.append(f"{dernier} à {maximum} collèges" if maximum > dernier
                      else f"{maximum} collèges")
    return bornes, couleurs, etiquettes


def figure_departements(sous: pd.DataFrame, contours, reglage: dict) -> None:
    """Carte : effectif inscrit directement sur chaque departement concerne."""
    par_dep = sous.groupby("code_departement").size().rename("effectif")
    gdf = contours.join(par_dep, how="left")
    gdf["effectif"] = gdf["effectif"].fillna(0)

    concernes = gdf["effectif"] > 0
    maximum = int(gdf["effectif"].max())
    bornes, couleurs, etiquettes = classes_effectif(maximum, reglage)
    cmap = ListedColormap(couleurs)
    norme = BoundaryNorm(bornes, ncolors=cmap.N)

    fig, ax = plt.subplots(figsize=(9, 10.2))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.165)

    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.4)
    gdf[concernes].plot(ax=ax, column="effectif", cmap=cmap, norm=norme,
                        edgecolor="white", linewidth=0.4)

    # L'effectif est ecrit sur le departement. Le blanc devient illisible sur
    # les teintes claires : la couleur du texte suit donc l'intensite du fond.
    for _, ligne in gdf[concernes].iterrows():
        point = ligne["geometry"].representative_point()
        effectif = int(ligne["effectif"])
        ax.annotate(str(effectif), xy=(point.x, point.y), ha="center",
                    va="center", fontsize=7.5, fontweight="bold",
                    color="white" if effectif >= reglage["texte_blanc_des"]
                    else "#0b0b0b")

    annoter_drom(ax, contours)
    ax.set_axis_off()

    # Legende en haut a droite : le coin inferieur droit est occupe par la
    # Corse, dont l'effectif serait masque.
    poignees = [plt.Rectangle((0, 0), 1, 1, color=c) for c in couleurs]
    ax.legend(poignees, etiquettes, loc="upper right", frameon=False,
              fontsize=8.5, title=reglage["legende_carte"], title_fontsize=8.5)

    fig.suptitle(reglage["titre_carte"], fontsize=13, fontweight="bold",
                 x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.10,
             f"{int(gdf['effectif'].sum())} collèges publics dans "
             f"{int(concernes.sum())} départements. En gris, les départements sans "
             f"aucun cas.\n"
             + replier(reglage["contrainte"]) + "\n" + RESERVE_CARTE,
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / f"{reglage['radical']}_departements.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    print("Contours :")
    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    print(f"  {len(contours)} departements")

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    colonnes = ["uai", "nom", "nom_commune", "departement", "academie", "ep",
                "ips", "ips_seuil", "score_ecart_ips", "plage"]

    for type_ecart, reglage in TYPES.items():
        sous = charger(type_ecart)
        q = sous["score_ecart_ips"]
        print(f"\n{'=' * 72}\n{type_ecart.upper()} : top {len(sous)}, "
              f"de {q.min():.1f} a {q.max():.1f} points d'ecart\n{'=' * 72}")
        print(sous["plage"].value_counts().reindex(
            [libelle for _, _, libelle in PLAGES]).to_string())

        table = pd.crosstab(sous["academie"], sous["plage"])
        table["total"] = table.sum(axis=1)
        print("\n--- par academie ---")
        print(table.sort_values("total", ascending=False).to_string())

        dep = (sous.groupby(["code_departement", "departement"]).size()
               .rename("colleges").reset_index()
               .sort_values("colleges", ascending=False))
        print("\n--- par departement ---")
        print(dep.to_string(index=False))

        print("\nFigure :")
        figure_departements(sous, contours, reglage)

        chemin = DOSSIER_TABLES / f"{reglage['radical']}_forts.csv"
        sous.sort_values("score_ecart_ips", ascending=False)[colonnes].to_csv(
            chemin, index=False, encoding="utf-8")
        print(f"  [+] {chemin.name} ({len(sous)} collèges)")


if __name__ == "__main__":
    main()
