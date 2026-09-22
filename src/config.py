"""Chemins et constantes partages par tous les scripts du projet.

Ce fichier est deja complet : c'est de la plomberie, pas de l'analyse.
Tout script du projet doit importer ses chemins d'ici plutot que d'ecrire
des chemins en dur. Le jour ou tu deplaces le projet, tu ne corriges qu'ici.
"""

from pathlib import Path

# __file__ = chemin de CE fichier (src/config.py)
#   .resolve()  -> chemin absolu, sans raccourci ni ".."
#   .parent     -> le dossier src/
#   .parent     -> la racine du projet
# Consequence : les chemins ci-dessous sont corrects quel que soit le dossier
# depuis lequel tu lances un script. C'est ce qui evite les "fichier introuvable".
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
FIGURES = PROJECT_ROOT / "outputs" / "figures"

# API Opendatasoft du ministere de l'Education nationale.
# Documentation : https://data.education.gouv.fr/api/explore/v2.1/console
API_BASE = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets"

# Identifiants des jeux de donnees (verifies le 2026-09-22).
# ATTENTION : malgre leurs noms, ces fichiers contiennent PLUSIEURS rentrees.
#   ips_ecoles   : 2022-2023, 2023-2024, 2024-2025   (~32 500 ecoles / an)
#   ips_colleges : 2023-2024, 2024-2025, 2025-2026   (~7 000 colleges / an)
DATASETS = {
    "ips_ecoles": "fr-en-ips-ecoles-ap2022",
    "ips_colleges": "fr-en-ips-colleges-ap2023",
    "annuaire": "fr-en-annuaire-education",
}

# Rentree la plus recente presente dans LES DEUX fichiers IPS.
# Toute comparaison ecoles / colleges doit se faire sur cette rentree.
RENTREE_REFERENCE = "2024-2025"
