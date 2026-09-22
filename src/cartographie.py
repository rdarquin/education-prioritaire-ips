"""Cartographie des divergences entre classement EP et realite sociale.

Produit deux figures dans outputs/figures/ :

    couverture_departementale.png  - part des etablissements defavorises
                                     NON classes, par departement
    non_classes_points.png         - les etablissements concernes, un point
                                     chacun

Les contours proviennent de `cartiflette`, package du laboratoire d'innovation
de l'Insee, qui redistribue les fonds de carte IGN ADMIN EXPRESS.

Le fond utilise la variante "DROM rapproches" : les departements d'outre-mer
sont deplaces et redimensionnes pour figurer aupres de la metropole, selon la
convention des publications de l'Insee. Consequence a ne jamais oublier :
CES CARTES NE PERMETTENT AUCUNE MESURE DE DISTANCE NI DE SURFACE. Elles ne
servent qu'a situer.

Lancement (depuis la racine du projet) :
    uv run python -m src.cartographie
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from cartiflette import carti_download

from src.config import DATA_PROCESSED, DATA_RAW, FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Nombre minimal d'etablissements defavorises pour qu'un taux departemental
# ait un sens. En dessous, un seul etablissement ferait bouger le taux de
# plusieurs points : on prefere ne rien afficher plutot qu'un chiffre trompeur.
SEUIL_SIGNIFICATIVITE = 20

PARAMS_CARTI = dict(values=["France"], crs=4326, borders="DEPARTEMENT",
                    vectorfile_format="geojson", simplification=50,
                    source="EXPRESS-COG-CARTO-TERRITOIRE", year=2022)


def charger_contours(variante: str) -> gpd.GeoDataFrame:
    """Telecharge (ou relit) les contours departementaux.

    Args:
        variante: "FRANCE_ENTIERE" pour les positions reelles,
            "FRANCE_ENTIERE_DROM_RAPPROCHES" pour l'outre-mer repositionne.

    Returns:
        Un GeoDataFrame indexe par code departement.
    """
    fichier = DATA_RAW / f"departements_{variante.lower()}.geojson"

    if fichier.exists():
        gdf = gpd.read_file(fichier)
    else:
        gdf = carti_download(filter_by=variante, **PARAMS_CARTI)
        fichier.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_file(fichier, driver="GeoJSON")
        print(f"  [+] {fichier.name} telecharge")

    # Un departement peut etre decoupe en plusieurs entites (iles, enclaves).
    # `dissolve` les reunit en une seule geometrie par code.
    return gdf.dissolve(by="INSEE_DEP")


def repositionner_drom(points: gpd.GeoDataFrame, vrais: gpd.GeoDataFrame,
                       rapproches: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Applique aux points ultramarins le meme deplacement qu'aux contours.

    Les coordonnees des etablissements sont reelles ; le fond de carte, lui,
    a deplace et redimensionne les DROM. Sans correction, une ecole de La
    Reunion s'afficherait au milieu de l'ocean Indien, hors du cadre.

    Le deplacement de chaque DROM est deduit de la comparaison entre son
    emprise reelle et son emprise sur le fond rapproche : une mise a
    l'echelle suivie d'une translation. La metropole n'est pas touchee.

    La transformation est VERIFIEE : chaque point deplace doit tomber a
    l'interieur de son departement sur le fond rapproche. Une carte fausse
    est pire qu'une absence de carte.
    """
    points = points.copy()
    drom = [d for d in points["code_departement"].unique() if d.startswith(("97", "98"))]

    for dep in drom:
        if dep not in vrais.index or dep not in rapproches.index:
            continue
        ax0, ay0, ax1, ay1 = vrais.loc[dep, "geometry"].bounds
        bx0, by0, bx1, by1 = rapproches.loc[dep, "geometry"].bounds

        # Facteurs d'echelle, puis translation ramenant le coin inferieur
        # gauche reel sur le coin inferieur gauche rapproche.
        sx, sy = (bx1 - bx0) / (ax1 - ax0), (by1 - by0) / (ay1 - ay0)
        dx, dy = bx0 - ax0 * sx, by0 - ay0 * sy

        masque = points["code_departement"] == dep
        points.loc[masque, "geometry"] = points.loc[masque, "geometry"].affine_transform(
            [sx, 0, 0, sy, dx, dy])

    # ---- Verification ----------------------------------------------------
    dehors = 0
    for dep, groupe in points.groupby("code_departement"):
        if dep not in rapproches.index:
            continue
        contour = rapproches.loc[dep, "geometry"]
        dehors += (~groupe.geometry.within(contour.buffer(0.01))).sum()

    if dehors:
        raise ValueError(
            f"{dehors} etablissements tombent hors de leur departement apres "
            f"repositionnement : la transformation est fausse, la carte ne "
            f"doit pas etre produite.")
    print(f"  verification : {len(points)} points, tous dans leur departement")

    return points


NOMS_DROM = {"971": "Guadeloupe", "972": "Martinique", "973": "Guyane",
             "974": "La Réunion", "976": "Mayotte"}


def annoter_drom(ax, contours: gpd.GeoDataFrame) -> None:
    """Nomme les departements d'outre-mer sur le fond rapproche.

    Sans etiquette, un lecteur ne peut pas savoir quel territoire il regarde :
    les DROM ne sont pas a leur place reelle et n'ont pas leur taille reelle.
    """
    for code, nom in NOMS_DROM.items():
        if code not in contours.index:
            continue
        centre = contours.loc[code, "geometry"].centroid
        bas = contours.loc[code, "geometry"].bounds[1]
        ax.annotate(nom, xy=(centre.x, bas - 0.25), ha="center", va="top",
                    fontsize=6.5, color="#555555")


def carte_couverture(dep_stats: pd.DataFrame, contours: gpd.GeoDataFrame) -> None:
    """Choroplethe : part des etablissements defavorises NON classes."""
    gdf = contours.join(dep_stats.set_index("code_departement"), how="left")

    # On cartographie la NON-couverture : une valeur elevee signale un
    # probleme, et se lit donc naturellement comme une couleur intense.
    gdf["non_couverture"] = 100 - gdf["couverture_pct"]

    # Les departements comptant trop peu d'etablissements defavorises sont
    # laisses en gris : leur taux n'est pas interpretable.
    fiable = gdf["defavorises"] >= SEUIL_SIGNIFICATIVITE
    n_masques = (~fiable).sum()

    fig, ax = plt.subplots(figsize=(9, 10))
    # On reserve le bas de la figure a la legende et aux notes, plutot que de
    # laisser matplotlib les empiler les unes sur les autres.
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.16)

    gdf.plot(ax=ax, color="#e3e3e3", edgecolor="white", linewidth=0.4)
    trace = gdf[fiable].plot(
        ax=ax, column="non_couverture", cmap="YlOrRd", edgecolor="white",
        linewidth=0.4)
    annoter_drom(ax, contours)
    ax.set_axis_off()

    # Barre de couleur placee dans ses propres axes, a une position choisie.
    normalisation = plt.Normalize(vmin=gdf.loc[fiable, "non_couverture"].min(),
                                  vmax=gdf.loc[fiable, "non_couverture"].max())
    echelle = plt.cm.ScalarMappable(cmap="YlOrRd", norm=normalisation)
    cax = fig.add_axes([0.28, 0.115, 0.44, 0.016])
    fig.colorbar(echelle, cax=cax, orientation="horizontal")
    cax.set_xlabel("Part des établissements défavorisés non classés (%)",
                   fontsize=8.5, labelpad=4)
    cax.tick_params(labelsize=7.5)

    fig.suptitle(
        "Éducation prioritaire : les établissements les plus défavorisés\n"
        "qui restent hors du dispositif",
        fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)

    fig.text(0.02, 0.055,
             "Champ : établissements publics, rentrée 2024-2025. Sont dits défavorisés les "
             "10 % au plus faible IPS.\n"
             f"En gris : {n_masques} départements comptant moins de "
             f"{SEUIL_SIGNIFICATIVITE} établissements défavorisés — le taux y serait trop "
             "instable pour être lu.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation, contours Insee/cartiflette. "
             "DROM rapprochés, échelles et distances non respectées.",
             fontsize=7.5, va="top", color="#444444")

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "couverture_departementale.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def carte_non_classes(points: gpd.GeoDataFrame, contours: gpd.GeoDataFrame) -> None:
    """Un point par etablissement defavorise non classe."""
    fig, ax = plt.subplots(figsize=(9, 10))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.10)

    contours.plot(ax=ax, color="#f4f4f4", edgecolor="#cccccc", linewidth=0.4)

    for niveau, couleur, taille, etiquette in [
        ("ecole", "#d62728", 9, "Écoles"),
        ("college", "#1f3b73", 26, "Collèges"),
    ]:
        sous = points[points["niveau"] == niveau]
        sous.plot(ax=ax, color=couleur, markersize=taille, alpha=0.75,
                  linewidth=0, label=f"{etiquette} ({len(sous)})")

    annoter_drom(ax, contours)
    ax.set_axis_off()
    ax.legend(loc="lower right", frameon=False, fontsize=10)

    fig.suptitle(
        f"Les {len(points)} établissements publics parmi les 10 % les plus\n"
        "défavorisés qui ne sont classés ni REP ni REP+",
        fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)

    fig.text(0.02, 0.06,
             "Champ : établissements publics, rentrée 2024-2025. Sont dits défavorisés les "
             "10 % au plus faible IPS.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation, contours Insee/cartiflette. "
             "DROM rapprochés, échelles et distances non respectées.",
             fontsize=7.5, va="top", color="#444444")

    chemin = FIGURES / "non_classes_points.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    print("Contours :")
    rapproches = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    vrais = charger_contours("FRANCE_ENTIERE")
    print(f"  {len(rapproches)} departements")

    dep_stats = pd.read_csv(DOSSIER_TABLES / "couverture_par_departement.csv",
                            dtype={"code_departement": str})

    non_classes = pd.read_csv(DOSSIER_TABLES / "defavorises_non_classes.csv",
                              dtype={"code_departement": str, "code_commune": str})

    print("\nPoints :")
    points = gpd.GeoDataFrame(
        non_classes,
        geometry=gpd.points_from_xy(non_classes["longitude"],
                                    non_classes["latitude"]),
        crs="EPSG:4326")
    points = repositionner_drom(points, vrais, rapproches)

    print("\nFigures :")
    carte_couverture(dep_stats, rapproches)
    carte_non_classes(points, rapproches)


if __name__ == "__main__":
    main()
