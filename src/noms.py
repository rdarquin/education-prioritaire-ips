"""Noms d'academies et de departements, correctement accentues.

LE PROBLEME

Les fichiers du ministere donnent les noms en MAJUSCULES NON ACCENTUEES :
« BESANCON », « PUY-DE-DOME », « COTE D'OR ». Un simple `.title()` produit
« Besancon » et « Puy-De-Dome » — majuscules mal placees et accents absents.
Sur une figure destinee a etre lue, c'est une faute visible.

DEUX SOURCES, DEUX TRAITEMENTS

Pour les DEPARTEMENTS, le projet dispose deja d'une source accentuee et
faisant autorite : les contours de `cartiflette`, qui redistribuent IGN ADMIN
EXPRESS, portent un champ `LIBELLE_DEPARTEMENT` correctement ecrit — « Bouches-
du-Rhone » avec son accent circonflexe, « Cote-d'Or » avec le sien. Elle couvre
les 101 departements du champ. On la prefere donc a toute table ecrite a la
main : elle est verifiable, maintenue ailleurs, et deja telechargee.

Pour les ACADEMIES, aucune source accentuee n'existe dans le projet. La table
ci-dessous est donc ecrite a la main — trente entrees, dont quatre seulement
different de ce que `.title()` produirait : Besancon, Creteil, La Reunion et
Orleans-Tours. Les vingt-six autres y figurent quand meme, pour que la table
soit la reference complete plutot qu'une liste d'exceptions dont on devrait
deviner les bornes.
"""

import pandas as pd

# Nom brut du ministere -> nom affichable. Les academies dont le nom ne demande
# aucune correction y figurent aussi : la table doit pouvoir etre lue comme la
# liste complete des academies, et non comme un rattrapage partiel.
NOMS_ACADEMIES = {
    "AIX-MARSEILLE": "Aix-Marseille",
    "AMIENS": "Amiens",
    "BESANCON": "Besançon",
    "BORDEAUX": "Bordeaux",
    "CLERMONT-FERRAND": "Clermont-Ferrand",
    "CORSE": "Corse",
    "CRETEIL": "Créteil",
    "DIJON": "Dijon",
    "GRENOBLE": "Grenoble",
    "GUADELOUPE": "Guadeloupe",
    "GUYANE": "Guyane",
    "LA REUNION": "La Réunion",
    "LILLE": "Lille",
    "LIMOGES": "Limoges",
    "LYON": "Lyon",
    "MARTINIQUE": "Martinique",
    "MAYOTTE": "Mayotte",
    "MONTPELLIER": "Montpellier",
    "NANCY-METZ": "Nancy-Metz",
    "NANTES": "Nantes",
    "NICE": "Nice",
    "NORMANDIE": "Normandie",
    "ORLEANS-TOURS": "Orléans-Tours",
    "PARIS": "Paris",
    "POITIERS": "Poitiers",
    "REIMS": "Reims",
    "RENNES": "Rennes",
    "STRASBOURG": "Strasbourg",
    "TOULOUSE": "Toulouse",
    "VERSAILLES": "Versailles",
}


def academie(brut: str) -> str:
    """Nom affichable d'une academie.

    Le repli sur `.title()` evite qu'une figure echoue parce qu'une academie
    aurait change de nom — mais il produit un nom sans accent, donc visible.
    `academies` ci-dessous le signale a l'execution.
    """
    return NOMS_ACADEMIES.get(str(brut).strip().upper(), str(brut).title())


def academies(valeurs) -> list[str]:
    """Noms affichables d'une suite d'academies, en signalant les inconnues.

    Une academie absente de la table passerait sinon en silence, avec un nom
    mal ecrit sur une figure publiee. Mieux vaut le lire a l'execution.
    """
    inconnues = sorted({str(v).strip().upper() for v in valeurs}
                       - set(NOMS_ACADEMIES))
    if inconnues:
        print(f"  [!] absentes de la table des accents, nom non corrigé : "
              f"{', '.join(inconnues)}")
    return [academie(v) for v in valeurs]


def departements(contours) -> pd.Series:
    """Libelles accentues des departements, indexes par code.

    Args:
        contours: le GeoDataFrame de `cartographie.charger_contours`, indexe
            par code departement et portant `LIBELLE_DEPARTEMENT`.
    """
    if "LIBELLE_DEPARTEMENT" not in contours.columns:
        raise KeyError(
            "les contours ne portent pas `LIBELLE_DEPARTEMENT` : la source "
            "accentuee des noms de departements a change.")
    return contours["LIBELLE_DEPARTEMENT"]
