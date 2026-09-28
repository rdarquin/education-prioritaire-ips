"""Fond de carte partage par toutes les cartes du depot.

Ce module ne produit aucune figure. Il fournit le socle geographique :
telechargement et mise en cache des contours departementaux, et annotation des
territoires ultramarins.

Les contours proviennent de `cartiflette`, package du laboratoire d'innovation
de l'Insee, qui redistribue les fonds de carte IGN ADMIN EXPRESS.

La variante utilisee est « DROM rapproches » : les departements d'outre-mer sont
deplaces et redimensionnes pour figurer aupres de la metropole, selon la
convention des publications de l'Insee. Consequence a ne jamais oublier :
CES CARTES NE PERMETTENT AUCUNE MESURE DE DISTANCE NI DE SURFACE. Elles ne
servent qu'a situer, et chaque figure doit le rappeler dans sa note.

Utilisateurs : `cartographie_score.py` et `ecarts_extremes.py`.
"""

import geopandas as gpd
from cartiflette import carti_download

from src.config import DATA_RAW

PARAMS_CARTI = dict(values=["France"], crs=4326, borders="DEPARTEMENT",
                    vectorfile_format="geojson", simplification=50,
                    source="EXPRESS-COG-CARTO-TERRITOIRE", year=2022)

NOMS_DROM = {"971": "Guadeloupe", "972": "Martinique", "973": "Guyane",
             "974": "La Réunion", "976": "Mayotte"}


def charger_contours(variante: str) -> gpd.GeoDataFrame:
    """Telecharge (ou relit) les contours departementaux.

    Le fichier est mis en cache dans `data/raw/` : le telechargement n'a lieu
    qu'une fois, et les figures se regenerent ensuite sans reseau.

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
