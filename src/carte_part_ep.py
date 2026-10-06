"""Part des colleges publics classes en education prioritaire, par academie.

CE QUE CETTE CARTE N'EST PAS

Le depot contient deja une carte academique : `carte_enveloppe`, qui rapporte
les places RECUES au nombre de colleges que l'etalon DESIGNERAIT. C'est une
mesure de desaccord, centree sur 1.

Celle-ci est beaucoup plus simple, et c'est son interet : elle ne mobilise
aucun etalon. Elle compte, pour chaque academie, la part de ses colleges
publics qui portent le label — rien d'autre. C'est la photographie du
dispositif tel qu'il est, avant toute confrontation.

Elle vient donc AVANT les autres cartes dans la lecture : on regarde d'abord
comment l'education prioritaire est repartie, et seulement ensuite si cette
repartition s'accorde avec la realite sociale mesuree.

CE QU'UNE PART ELEVEE NE SIGNIFIE PAS

Une academie tres couverte n'est pas une academie sur-dotee. La Guyane classe
plus de la moitie de ses colleges parce que la moitie de ses colleges sont
tres defavorises. Lire cette carte comme un palmares serait exactement
l'erreur que le reste du projet s'emploie a eviter : c'est la CONFRONTATION
avec un etalon qui permet de parler de desaccord, pas le taux brut.

La note de la figure le dit explicitement, parce qu'une carte circule seule.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

from src.carte_enveloppe import DROM_ACADEMIES, contours_academiques
from src.config import FIGURES, PROJECT_ROOT
from src.noms import academie, academies as noms_academies

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"
FICHIER = PROJECT_ROOT / "data" / "processed" / "colleges_2024_2025.csv"

ENCRE, ENCRE_2, GRIS_ABSENT = "#0b0b0b", "#52514e", "#e3e3e3"

# Sequentielle et non divergente : une part n'a pas de point neutre autour
# duquel s'ecarter. Les teintes sont celles deja employees pour les oublis,
# pour qu'un lecteur qui enchaine les cartes ne reapprenne pas un code.
SEQUENTIELLE = LinearSegmentedColormap.from_list(
    "part_ep", ["#fdf0e6", "#f6c5ac", "#ee8e56", "#c9551d", "#7a2f0e"])

# En dessous de ce nombre de colleges publics, une part academique repose sur
# trop peu d'etablissements pour se comparer aux autres : un college de plus
# ou de moins y deplace le taux de plusieurs points. Les academies concernees
# restent sur la carte — les masquer donnerait a croire qu'on n'a pas la
# donnee — mais sont nommees dans la note.
SEUIL_COLLEGES = 40


def charger() -> tuple[pd.DataFrame, pd.Series]:
    """Part d'EP par academie, et rattachement departement -> academie."""
    if not FICHIER.exists():
        raise FileNotFoundError(
            f"{FICHIER.name} absent. Lance d'abord : "
            f"uv run python -m src.preparation")

    df = pd.read_csv(FICHIER, dtype={"code_departement": str})
    public = df[df["secteur"] == "public"].copy()
    public["classe"] = public["ep"] != "hors EP"

    parts = (public.groupby("academie")
             .agg(colleges=("uai", "size"), classes=("classe", "sum"))
             .reset_index())
    parts["part_ep"] = 100 * parts["classes"] / parts["colleges"]

    # Un departement releve d'une seule academie : on le verifie plutot que
    # de le supposer, comme ailleurs dans le projet.
    multiples = public.groupby("code_departement")["academie"].nunique()
    if (multiples > 1).any():
        raise ValueError(
            f"{int((multiples > 1).sum())} departements relevent de plusieurs "
            f"academies : la fusion des contours serait fausse.")

    rattachement = (public.groupby("code_departement")["academie"]
                    .first().rename("academie"))
    return parts, rattachement


def classes_part(parts: np.ndarray) -> np.ndarray:
    """Bornes de classes, quantiles de la distribution academique.

    Des classes regulieres placeraient presque toutes les academies dans la
    meme : la distribution est tres asymetrique, quelques academies
    ultramarines valant plusieurs fois la mediane.
    """
    bornes = np.concatenate([[parts.min()],
                             np.quantile(parts, [0.2, 0.4, 0.6, 0.8]),
                             [parts.max()]])
    return np.unique(np.round(bornes, 2))


def figure(parts: pd.DataFrame, gdf, national: float) -> None:
    """Choroplethe academique de la part d'EP, valeur inscrite sur chacune."""
    serie = parts.set_index("academie")["part_ep"]
    tri = serie.sort_values()
    nommees = list(tri.index[:2]) + list(tri.index[-2:])
    gdf = gdf.join(serie).join(parts.set_index("academie")["colleges"])
    connus = gdf["part_ep"].notna()

    bornes = classes_part(gdf.loc[connus, "part_ep"].to_numpy())
    cmap = SEQUENTIELLE.resampled(len(bornes) - 1)
    norme = BoundaryNorm(bornes, ncolors=len(bornes) - 1)

    fig, ax = plt.subplots(figsize=(9.5, 10.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.885, bottom=0.165)

    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.5)
    gdf[connus].plot(ax=ax, column="part_ep", cmap=cmap, norm=norme,
                     edgecolor="white", linewidth=0.5)

    # Liseré blanc autour du texte : les académies ultramarines sont trop
    # petites pour contenir leur étiquette, qui déborde sur le fond clair.
    liec = [pe.withStroke(linewidth=2.2, foreground="white")]

    for nom, ligne in gdf[connus].iterrows():
        point = ligne["geometry"].representative_point()
        ax.annotate(f"{ligne['part_ep']:.0f} %",
                    xy=(point.x, point.y), ha="center", va="center",
                    fontsize=6.8, fontweight="bold", color=ENCRE,
                    path_effects=liec)
        # Les DROM portent deja leur nom sous leur vignette : les deux
        # extremes etant ici Mayotte et la Guyane, les nommer une seconde
        # fois ecrirait le meme mot deux fois l'un sous l'autre.
        if nom in nommees and nom not in DROM_ACADEMIES:
            ax.annotate(academie(nom), xy=(point.x, point.y), xytext=(0, -9),
                        textcoords="offset points", ha="center", va="top",
                        fontsize=6.5, color=ENCRE_2, path_effects=liec)

    for code, etiquette in DROM_ACADEMIES.items():
        if code not in gdf.index:
            continue
        forme = gdf.loc[code, "geometry"]
        ax.annotate(etiquette, xy=(forme.centroid.x, forme.bounds[1] - 0.25),
                    ha="center", va="top", fontsize=6.5, color=ENCRE_2)

    ax.set_axis_off()

    echelle = plt.cm.ScalarMappable(cmap=cmap, norm=norme)
    cax = fig.add_axes([0.28, 0.130, 0.44, 0.014])
    fig.colorbar(echelle, cax=cax, orientation="horizontal",
                 ticks=bornes, spacing="uniform")
    cax.set_xticklabels([f"{b:.0f}" for b in bornes], fontsize=6.5)
    cax.set_xlabel("Part des collèges publics classés REP ou REP+ (%)",
                   fontsize=8, labelpad=4)

    petites = gdf[connus & (gdf["colleges"] < SEUIL_COLLEGES)]
    if petites.empty:
        fragiles = ""
    else:
        noms = ", ".join(
            f"{a} ({int(c)} collèges)" for a, c in
            zip(noms_academies(petites.index), petites["colleges"]))
        fragiles = (f"Part fragile — moins de {SEUIL_COLLEGES} collèges publics, "
                    f"un établissement y déplace le taux de plusieurs points : "
                    f"{noms}.\n")

    # Les nombres sont mis en forme a part : un `.replace` applique en fin de
    # bloc porterait sur TOUTES les chaines adjacentes concatenees, virgules
    # decimales des autres phrases comprises.
    taux = f"{national:.1f}".replace(".", ",")
    extremes = tri.index[[0, -1]]
    bas = f"{tri.iloc[0]:.0f}"
    haut = f"{tri.iloc[-1]:.0f}"

    fig.suptitle("Quelle part des collèges publics est classée\n"
                 "en éducation prioritaire, académie par académie ?",
                 fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.918,
             f"Collèges classés REP ou REP+ rapportés à l'ensemble des collèges "
             f"publics de l'académie, rentrée 2024-2025.\n"
             f"La moyenne nationale vaut {taux} % — 1 094 collèges classés sur "
             f"5 325. L'écart entre académies va de {bas} % "
             f"({academie(extremes[0])})\nà {haut} % "
             f"({academie(extremes[1])}).",
             fontsize=8.5, va="top", color=ENCRE_2)

    fig.text(0.02, 0.098,
             "CETTE CARTE NE MESURE AUCUN DÉSACCORD. Elle décrit la "
             "répartition du dispositif, pas sa justesse : une académie très "
             "couverte\n"
             "peut l'être parce que ses collèges sont effectivement très "
             "défavorisés. C'est la confrontation à un étalon — objet des "
             "autres cartes\n"
             "de ce dépôt — qui permet de parler d'écart, jamais le taux brut.\n"
             "Les classes sont des quantiles de la distribution académique : "
             "des classes régulières rangeraient presque toutes les académies "
             "dans la même.\n"
             f"{fragiles}"
             "Champ : collèges publics, rentrée 2024-2025. Le privé sous "
             "contrat est hors champ du dispositif — aucun de ses collèges "
             "n'est classé.\n"
             "Sources : annuaire de l'éducation, DEPP, contours "
             "Insee/cartiflette. DROM rapprochés, échelles et distances non "
             "respectées.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "part_ep_academies.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    parts, rattachement = charger()
    national = 100 * parts["classes"].sum() / parts["colleges"].sum()

    print(f"\n{'=' * 72}")
    print("PART DES COLLEGES PUBLICS EN EDUCATION PRIORITAIRE, PAR ACADEMIE")
    print("=" * 72)
    print(f"\n  {int(parts['classes'].sum())} classes sur "
          f"{int(parts['colleges'].sum())} colleges publics "
          f"-> {national:.2f} % au national")

    tri = parts.sort_values("part_ep", ascending=False)
    print("\n" + tri[["academie", "colleges", "classes", "part_ep"]]
          .to_string(index=False))

    gdf = contours_academiques(rattachement)
    figure(parts, gdf, national)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_TABLES / "part_ep_par_academie.csv"
    tri.round(2).to_csv(chemin, index=False, encoding="utf-8")
    print(f"\n[+] {chemin.name} ({len(tri)} academies)")


if __name__ == "__main__":
    main()
