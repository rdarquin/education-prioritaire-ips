"""Les ecarts les plus forts au seuil budgetaire national, des deux cotes.

Champ : colleges publics dont le score d'ecart au seuil NATIONAL (88,80 points)
atteint au moins 10 points, soit plus de trois fois le seuil d'interpretabilite
de 3 points recommande par la DEPP. Ce sont les cas qu'aucune imprecision de
mesure ne peut expliquer.

Deux types d'ecart, traites symetriquement :

    SUR-INCLUSION - college classe REP ou REP+ dont l'IPS DEPASSE le seuil.
    OUBLI         - college non classe dont l'IPS est INFERIEUR au seuil.

Pour chacun, deux figures : barres empilees par academie, decoupees en trois
plages d'ecart, et carte portant l'effectif de chaque departement concerne.

LES TROIS PLAGES SONT COMMUNES AUX DEUX TYPES, et conservees meme lorsqu'elles
sont vides. C'est indispensable : aucun oubli n'atteint 20 points alors que six
sur-inclusions les depassent. Supprimer la tranche vide du cote des oublis
rendrait les deux figures incomparables et effacerait ce constat.

Les plages sont ORDONNEES, donc rendues par une seule teinte du clair au fonce,
et non par des couleurs distinctes. La teinte reprend la convention suivie dans
tout le projet : BLEU pour les sur-inclusions, ORANGE pour les oublis.

RESERVE, valable pour les quatre figures. Le seuil est national, or l'enveloppe
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

ECART_MINIMAL = 10.0
SEUIL_NATIONAL = 88.80

# Bornes inferieure et superieure, et libelle. La derniere plage est ouverte.
PLAGES = [(10.0, 15.0, "10 à 15 points"),
          (15.0, 20.0, "15 à 20 points"),
          (20.0, np.inf, "plus de 20 points")]

# Un reglage par type d'ecart. Les trois teintes servent aux plages du
# diagramme ; la quatrieme, plus sombre, n'apparait que sur la carte, pour la
# classe des departements comptant au moins quatre etablissements.
TYPES = {
    "sur-inclus": dict(
        radical="sur_inclusions",
        teintes=["#a8c4e8", "#5588cc", "#1f3b73"],
        teinte_carte="#0b2350",
        # A partir de cet effectif, le fond est assez sombre pour porter du
        # texte blanc. Les deux rampes ne s'assombrissent pas au meme rythme.
        texte_blanc_des=2,
        titre_barres="Collèges classés dont l'IPS dépasse largement le seuil national",
        sous_titre_barres=(
            "Collèges publics classés REP ou REP+ dont l'IPS dépasse d'au moins "
            "{mini:.0f} points celui de l'établissement qui ferme l'enveloppe "
            "nationale ({seuil} points),\nsoit plus de trois fois le seuil de "
            "3 points en deçà duquel la DEPP recommande de ne pas interpréter une "
            "différence d'IPS."),
        axe_barres="Nombre de collèges publics sur-inclus",
        titre_carte=("Où se trouvent les collèges classés dont l'IPS dépasse\n"
                     "le seuil national de plus de 10 points"),
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
        teintes=["#f6c5ac", "#ee8e56", "#c9551d"],
        teinte_carte="#7a2f0e",
        texte_blanc_des=3,
        titre_barres="Collèges non classés dont l'IPS est très inférieur au seuil national",
        sous_titre_barres=(
            "Collèges publics classés ni REP ni REP+ dont l'IPS est inférieur d'au "
            "moins {mini:.0f} points à celui de l'établissement qui ferme "
            "l'enveloppe nationale ({seuil} points),\nsoit plus de trois fois le "
            "seuil de 3 points en deçà duquel la DEPP recommande de ne pas "
            "interpréter une différence d'IPS."),
        axe_barres="Nombre de collèges publics non classés",
        titre_carte=("Où se trouvent les collèges non classés dont l'IPS est\n"
                     "inférieur au seuil national de plus de 10 points"),
        legende_carte="Collèges oubliés",
        contrainte=(
            "L'enveloppe d'éducation prioritaire est répartie par académie avant que "
            "les recteurs ne désignent les établissements : une académie comptant "
            "plus de collèges sous le seuil\nnational que de places à pourvoir ne "
            "peut pas éviter d'en oublier, et une part de ces cas est donc "
            "arithmétiquement forcée. C'est la situation de Lille."),
    ),
}

ENCRE_2, GRILLE, GRIS_ABSENT = "#52514e", "#e1e0d9", "#eeeeee"

RESERVE = ("Champ : collèges publics, rentrée 2024-2025. L'IPS n'est pas le critère "
           "officiel de classement : un écart mesure un désaccord entre deux "
           "instruments, pas une erreur administrative.\n"
           "Sources : DEPP (IPS), annuaire de l'éducation.")

# Version courte pour les cartes, dont la largeur utile est moindre que celle
# des diagrammes : la ligne complete y deborderait du cadre.
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
    """Colleges d'un type d'ecart donne, au-dela de ECART_MINIMAL, avec leur plage."""
    fichier = DOSSIER_TABLES / "score_ecart_ips.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.score_ecart")

    df = pd.read_csv(fichier, dtype={"code_departement": str, "code_commune": str})
    sous = df[(df["type_ecart"] == type_ecart)
              & (df["score_ecart_ips"] >= ECART_MINIMAL)].copy()

    sous["plage"] = pd.cut(
        sous["score_ecart_ips"],
        bins=[b for b, _, _ in PLAGES] + [np.inf],
        labels=[libelle for _, _, libelle in PLAGES],
        right=False)  # borne basse incluse : 15,0 va dans "15 a 20"
    return sous


def mention_plages_vides(table: pd.DataFrame) -> str:
    """Signale explicitement les plages sans aucun etablissement.

    Une tranche vide se lit mal sur une legende : rien ne distingue "aucun cas"
    de "plage oubliee par l'auteur". On l'ecrit donc en toutes lettres.
    """
    vides = [libelle for _, _, libelle in PLAGES if table[libelle].sum() == 0]
    if not vides:
        return ""
    if len(vides) == 1:
        return (f"Aucun collège n'atteint la tranche « {vides[0]} » : elle figure "
                f"dans la légende mais reste vide.\n")
    return (f"Aucun collège n'atteint ces tranches, qui figurent dans la légende "
            f"mais restent vides : {', '.join(vides)}.\n")


def figure_academies(sous: pd.DataFrame, reglage: dict) -> None:
    """Barres empilees : effectif par academie, decoupe par plage d'ecart."""
    table = (pd.crosstab(sous["academie"], sous["plage"])
             .reindex(columns=[libelle for _, _, libelle in PLAGES], fill_value=0))
    table["total"] = table.sum(axis=1)
    table = table.sort_values("total")  # barh empile du bas vers le haut

    fig, ax = plt.subplots(figsize=(10, 0.46 * len(table) + 3.0))
    fig.subplots_adjust(left=0.20, right=0.97, top=0.855, bottom=0.185)

    gauche = np.zeros(len(table))
    for (_, _, libelle), couleur in zip(PLAGES, reglage["teintes"]):
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
    ax.set_xlabel(reglage["axe_barres"], fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.legend(frameon=False, fontsize=8.5, loc="lower right",
              title="Écart d'IPS au seuil national", title_fontsize=8.5)
    ax.grid(True, axis="x", linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right", "left"]:
        ax.spines[bord].set_visible(False)

    fig.suptitle(reglage["titre_barres"], fontsize=13, fontweight="bold",
                 x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.945,
             reglage["sous_titre_barres"].format(
                 mini=ECART_MINIMAL,
                 # Separateur decimal francais : "88,80" et non "88.80".
                 seuil=f"{SEUIL_NATIONAL:.2f}".replace(".", ",")),
             fontsize=8.5, va="top", color=ENCRE_2)
    fig.text(0.02, 0.098,
             mention_plages_vides(table) + reglage["contrainte"] + "\n" + RESERVE,
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / f"{reglage['radical']}_academies.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def classes_effectif(maximum: int, reglage: dict) -> tuple:
    """Bornes, couleurs et etiquettes d'une echelle de comptage.

    L'effectif est un entier : une rampe continue suggererait des valeurs
    intermediaires qui n'existent pas. Les classes s'arretent au maximum
    observe, sans quoi la legende annoncerait des categories vides — un
    departement a 11 colleges et un autre a 3 n'appellent pas le meme decoupage.
    """
    paliers = [0.5, 1.5, 2.5, 3.5]
    bornes = np.array([b for b in paliers if b < maximum] + [maximum + 0.5])
    couleurs = (reglage["teintes"] + [reglage["teinte_carte"]])[:len(bornes) - 1]

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
        print(f"\n{'=' * 72}\n{type_ecart.upper()} : {len(sous)} colleges "
              f"d'au moins {ECART_MINIMAL:.0f} points\n{'=' * 72}")
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

        print("\nFigures :")
        figure_academies(sous, reglage)
        figure_departements(sous, contours, reglage)

        chemin = DOSSIER_TABLES / f"{reglage['radical']}_forts.csv"
        sous.sort_values("score_ecart_ips", ascending=False)[colonnes].to_csv(
            chemin, index=False, encoding="utf-8")
        print(f"  [+] {chemin.name} ({len(sous)} collèges)")


if __name__ == "__main__":
    main()
