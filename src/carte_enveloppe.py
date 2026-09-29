"""Carte du ratio d'enveloppe par academie.

QUESTION POSEE

L'enveloppe d'education prioritaire — le nombre de reseaux — est repartie entre
academies au niveau national, sans qu'aucune cle de calcul ait ete publiee. On
peut neanmoins la confronter a un etalon : chaque academie recoit-elle autant de
places qu'elle compte de colleges parmi les plus defavorises du pays ?

    ratio = places recues / colleges de l'academie figurant parmi les n colleges
            d'IPS le plus faible de France, n etant le nombre total de places

    ratio > 1 : l'academie recoit plus de places que ce compte
    ratio < 1 : elle en recoit moins

POURQUOI LA FRANCE VAUT EXACTEMENT 1

Les deux termes du rapport sont, au niveau national, le meme nombre : n places
distribuees et n colleges dans l'ensemble optimal. Le ratio national vaut donc
1 par construction, et la carte se lit comme une redistribution a somme nulle —
ce qu'une academie recoit au-dessus de 1, une autre le perd.

Cette egalite exige que l'ensemble optimal soit defini par le RANG et non par
une inegalite stricte sur le seuil : onze colleges ont exactement l'IPS du
seuil, et les exclure ferait tomber le total national a 1 088 pour 1 094 places.
`score_ecart.py` s'en charge.

POURQUOI UNE ECHELLE LOGARITHMIQUE

Le ratio est multiplicatif : recevoir deux fois trop et deux fois trop peu sont
deux ecarts de meme ampleur, alors qu'en echelle lineaire le premier vaut +1 et
le second -0,5. La couleur suit donc le logarithme en base 2 du ratio, qui
rend ces deux situations symetriques autour de zero. Les bornes affichees sur
la barre restent des ratios, lisibles directement.

RESERVE

L'etalon est l'IPS, qui n'est pas le critere officiel de classement. Un ratio
eloigne de 1 ne prouve pas une erreur de repartition : il mesure un desaccord
entre la cle implicite du ministere et un classement par IPS.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.carte_enveloppe
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

from src.cartographie import charger_contours
from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

ENCRE, ENCRE_2, GRIS_ABSENT = "#0b0b0b", "#52514e", "#e3e3e3"

# Palette divergente aux couleurs du projet, gris neutre au centre. Le bleu
# marque les academies qui recoivent moins que l'etalon, l'orange celles qui
# recoivent plus — meme convention que les autres cartes, ou l'orange signale
# ce qui va dans le sens de la sur-dotation.
DIVERGENTE = LinearSegmentedColormap.from_list(
    "enveloppe", ["#2a78d6", "#9ec4ee", "#d8d7d0", "#f2a888", "#eb6834"])

# Academies nommees sur la carte : les deux extremes de chaque cote. Les
# autres portent leur ratio sans etiquette, faute de place.
ACADEMIES_NOMMEES = ["CORSE", "PARIS", "STRASBOURG", "NICE"]

# `cartographie.annoter_drom` attend un fond indexe par code departement ; ici
# l'index est l'academie. Les cinq academies ultramarines portant le nom de
# leur territoire, la correspondance se reduit a une mise en forme.
DROM_ACADEMIES = {"GUADELOUPE": "Guadeloupe", "MARTINIQUE": "Martinique",
                  "GUYANE": "Guyane", "LA REUNION": "La Réunion",
                  "MAYOTTE": "Mayotte"}


def charger() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lit les ratios par academie et le rattachement departement -> academie."""
    for nom in ("score_ecart_ips.csv", "score_ecart_par_academie.csv"):
        if not (DOSSIER_TABLES / nom).exists():
            raise FileNotFoundError(
                f"{nom} absent. Lance d'abord : uv run python -m src.score_ecart")

    academies = pd.read_csv(DOSSIER_TABLES / "score_ecart_par_academie.csv")
    colleges = pd.read_csv(DOSSIER_TABLES / "score_ecart_ips.csv",
                           dtype={"code_departement": str})

    # Un departement releve d'une seule academie : la correspondance est donc
    # une fonction, et le controle ci-dessous le verifie plutot que de le
    # supposer.
    multiples = colleges.groupby("code_departement")["academie"].nunique()
    if (multiples > 1).any():
        raise ValueError(
            f"{int((multiples > 1).sum())} departements relevent de plusieurs "
            f"academies : la fusion des contours serait fausse.")

    rattachement = (colleges.groupby("code_departement")["academie"]
                    .first().rename("academie"))
    return academies, rattachement


def contours_academiques(rattachement: pd.Series):
    """Fusionne les contours departementaux en contours academiques."""
    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    gdf = contours.join(rattachement, how="inner")
    print(f"  {len(contours)} departements -> {gdf['academie'].nunique()} academies")
    return gdf.dissolve(by="academie")


def classes_ratio(ratios: np.ndarray) -> tuple:
    """Bornes de classes sur le logarithme du ratio, symetriques autour de 1.

    Les bornes interieures sont prises sur les quantiles de |log2(ratio)| puis
    reflechies : un ratio de 2 et un ratio de 0,5 tombent ainsi dans des
    classes symetriques. Sans cette transformation, tout l'ecartement serait du
    cote des ratios superieurs a 1, qui n'ont pas de borne haute.
    """
    logs = np.log2(ratios)
    interieures = np.quantile(np.abs(logs), [0.35, 0.70])
    extreme = np.abs(logs).max()
    bornes = np.concatenate([[-extreme], -interieures[::-1], [0.0],
                             interieures, [extreme]])
    return np.unique(np.round(bornes, 4))


def figure(academies: pd.DataFrame, gdf) -> None:
    """Choroplethe academique du ratio, valeur inscrite sur chaque academie."""
    ratios = academies.set_index("academie")["ratio_enveloppe"]
    gdf = gdf.join(ratios)
    connus = gdf["ratio_enveloppe"].notna()

    bornes = classes_ratio(gdf.loc[connus, "ratio_enveloppe"].to_numpy())
    cmap = DIVERGENTE.resampled(len(bornes) - 1)
    norme = BoundaryNorm(bornes, ncolors=len(bornes) - 1)

    fig, ax = plt.subplots(figsize=(9.5, 10.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.885, bottom=0.185)

    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.5)
    gdf[connus].assign(log=np.log2(gdf.loc[connus, "ratio_enveloppe"])).plot(
        ax=ax, column="log", cmap=cmap, norm=norme,
        edgecolor="white", linewidth=0.5)

    # Liseré blanc autour du texte plutôt qu'une couleur d'encre choisie selon
    # le fond : les académies ultramarines sont trop petites pour contenir leur
    # étiquette, qui déborde sur le blanc de la figure. Un texte clair y
    # deviendrait invisible.
    liec = [pe.withStroke(linewidth=2.2, foreground="white")]

    for nom, ligne in gdf[connus].iterrows():
        point = ligne["geometry"].representative_point()
        ratio = ligne["ratio_enveloppe"]
        ax.annotate(f"{ratio:.2f}".replace(".", ","),
                    xy=(point.x, point.y), ha="center", va="center",
                    fontsize=6.8, fontweight="bold", color=ENCRE,
                    path_effects=liec)
        if nom in ACADEMIES_NOMMEES:
            ax.annotate(nom.title(), xy=(point.x, point.y), xytext=(0, -9),
                        textcoords="offset points", ha="center", va="top",
                        fontsize=6.5, color=ENCRE_2, path_effects=liec)

    for code, etiquette in DROM_ACADEMIES.items():
        if code not in gdf.index:
            continue
        forme = gdf.loc[code, "geometry"]
        ax.annotate(etiquette, xy=(forme.centroid.x, forme.bounds[1] - 0.25),
                    ha="center", va="top", fontsize=6.5, color=ENCRE_2)

    ax.set_axis_off()

    # Barre de couleur graduee en RATIOS et non en logarithmes : le lecteur
    # doit retrouver les valeurs inscrites sur la carte.
    echelle = plt.cm.ScalarMappable(cmap=cmap, norm=norme)
    cax = fig.add_axes([0.28, 0.150, 0.44, 0.014])
    fig.colorbar(echelle, cax=cax, orientation="horizontal",
                 ticks=bornes, spacing="uniform")
    cax.set_xticklabels([f"{2 ** b:.2f}".replace(".", ",") for b in bornes],
                        fontsize=6.5)
    cax.set_xlabel("← reçoit moins que l'étalon        ratio = 1        "
                   "reçoit plus →", fontsize=8, labelpad=4)

    fig.suptitle("Chaque académie reçoit-elle autant de places qu'elle compte\n"
                 "de collèges parmi les plus défavorisés de France ?",
                 fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.918,
             "Ratio entre les places d'éducation prioritaire reçues et le nombre de "
             "collèges de l'académie figurant parmi les 1 094 collèges\n"
             "publics d'IPS le plus faible du pays — soit exactement le nombre de "
             "places distribuées. Le ratio national vaut donc 1 par\n"
             "construction, et la carte se lit comme une redistribution à somme "
             "nulle.",
             fontsize=8.5, va="top", color=ENCRE_2)

    fig.text(0.02, 0.113,
             "L'échelle suit le logarithme du ratio : recevoir deux fois trop et deux "
             "fois trop peu sont deux écarts de même ampleur, ce qu'une échelle "
             "linéaire ne rendrait pas.\n"
             "La barre reste graduée en ratios pour rester lisible. Les classes sont "
             "des quantiles de la distribution observée.\n"
             "La répartition des réseaux entre académies est arrêtée au niveau "
             "national sans clé de calcul publiée : ce ratio mesure une clé implicite, "
             "il n'en reprend aucune.\n"
             "L'IPS n'est pas le critère officiel de classement — un écart à 1 signale "
             "un désaccord entre deux instruments, pas une erreur de répartition.\n"
             "Les ratios de la Corse et de Paris reposent sur un dénominateur "
             "minuscule — 2 et 6 collèges dans l'ensemble optimal : ils sont "
             "instables, un collège de plus ou de moins\n"
             "les déplacerait fortement.\n"
             "Champ : collèges publics, rentrée 2024-2025. Sources : DEPP (IPS), "
             "annuaire de l'éducation, contours Insee/cartiflette.\n"
             "DROM rapprochés, échelles et distances non respectées.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "ratio_enveloppe_academies.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    academies, rattachement = charger()

    total_places = int(academies["classes"].sum())
    total_defavorises = int(academies["defavorises_national"].sum())
    print(f"\n{'=' * 72}")
    print("RATIO D'ENVELOPPE PAR ACADEMIE")
    print("=" * 72)
    print(f"\n  places distribuees {total_places}, colleges dans l'ensemble "
          f"optimal {total_defavorises}")
    print(f"  ratio France : {total_places / total_defavorises:.4f}")

    tri = academies.sort_values("ratio_enveloppe", ascending=False)
    colonnes = ["academie", "colleges", "classes", "defavorises_national",
                "ratio_enveloppe"]
    print("\n" + tri[colonnes].to_string(index=False))

    print("\nContours :")
    gdf = contours_academiques(rattachement)

    print("\nFigure :")
    figure(academies, gdf)


if __name__ == "__main__":
    main()
