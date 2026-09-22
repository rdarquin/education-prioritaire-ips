"""Telechargement des donnees brutes depuis l'API Opendatasoft.

SQUELETTE A REMPLIR. Les corps de fonction sont vides : a toi de les ecrire.

Objectif du module : rendre `data/raw/` entierement reconstructible.
Quelqu'un qui clone ce depot n'a aucun fichier de donnees ; il doit pouvoir
lancer une seule commande et se retrouver avec les memes donnees que toi.

Lancement (depuis la racine du projet) :
    uv run python -m src.download
"""

from pathlib import Path

import requests

from src.config import API_BASE, DATA_RAW, DATASETS


def build_export_url(dataset_id: str) -> str:
    """Construit l'URL d'export CSV complet d'un jeu de donnees Opendatasoft.

    L'endpoint a utiliser est de la forme :
        {API_BASE}/{dataset_id}/exports/csv

    Contrairement a l'endpoint /records (qui pagine et plafonne le nombre de
    lignes renvoyees), /exports/csv renvoie le fichier entier en une fois.

    Deux parametres de requete comptent ici :

      - `delimiter`   : Opendatasoft exporte en point-virgule par defaut.
                        Choisis explicitement ton separateur plutot que de
                        subir la valeur par defaut.

      - `use_labels`  : decide si l'en-tete du CSV contient les noms
                        TECHNIQUES des colonnes (`code_du_departement`) ou
                        leurs libelles HUMAINS ("Code du departement").
                        Tu veux les noms techniques : ils sont stables dans
                        le temps, sans accent ni espace, donc utilisables
                        directement comme noms de colonnes pandas.
                        A TESTER : verifie la valeur par defaut en ouvrant
                        le fichier telecharge, et force-la si besoin.

    Returns:
        L'URL complete, parametres inclus.
    """
    # TODO (1) : assembler l'URL de base a partir de API_BASE et dataset_id
    # TODO (2) : y ajouter les parametres de requete
    ...


def download_dataset(dataset_id: str, destination: Path, force: bool = False) -> Path:
    """Telecharge un jeu de donnees et l'ecrit sur disque.

    Args:
        dataset_id: identifiant Opendatasoft (voir DATASETS dans config.py).
        destination: chemin du fichier CSV a ecrire.
        force: si False et que le fichier existe deja, ne retelecharge pas.

    Returns:
        Le chemin du fichier ecrit.

    Points d'attention :

      - IDEMPOTENCE. Le parametre `force` n'est pas un gadget. L'annuaire
        pese plusieurs dizaines de Mo ; tu vas relancer ce script des
        dizaines de fois pendant le projet. Un script qui ne retelecharge
        pas ce qu'il a deja est un script qu'on ose relancer.

      - TELECHARGEMENT EN FLUX. `requests.get(url)` charge la reponse
        entiere en memoire avant de te la rendre. Pour un gros fichier, on
        prefere `stream=True` puis une ecriture par morceaux
        (`iter_content`). Regarde la doc de requests sur ce point.

      - ERREURS SILENCIEUSES. Si le serveur repond 404 ou 500, requests ne
        leve PAS d'exception tout seul : tu ecrirais tranquillement une page
        d'erreur HTML dans un fichier .csv, et tu ne t'en apercevrais qu'en
        voyant pandas echouer trois etapes plus loin. Cherche la methode de
        l'objet Response qui transforme un code d'erreur HTTP en exception,
        et appelle-la avant d'ecrire quoi que ce soit.

      - DOSSIER MANQUANT. Assure-toi que le dossier parent existe avant
        d'ecrire (`Path.mkdir` a un argument fait pour ca).
    """
    # TODO (1) : si le fichier existe et force est False -> afficher un
    #            message et retourner destination sans rien telecharger
    # TODO (2) : construire l'URL via build_export_url
    # TODO (3) : lancer la requete en mode flux
    # TODO (4) : verifier le code de reponse HTTP
    # TODO (5) : creer le dossier parent si besoin
    # TODO (6) : ecrire la reponse sur disque par morceaux
    # TODO (7) : afficher un message de confirmation (nom + taille du fichier)
    #            et retourner destination
    ...


def main() -> None:
    """Telecharge les trois jeux de donnees du projet.

    Parcourt DATASETS (defini dans config.py) et telecharge chaque jeu dans
    DATA_RAW sous le nom `<cle>.csv` — par exemple `ips_ecoles.csv`.

    Note : la cle du dictionnaire (`ips_ecoles`) sert de nom de fichier, pas
    l'identifiant Opendatasoft (`fr-en-ips-ecoles-ap2022`). Tes fichiers
    locaux portent ainsi des noms lisibles, independants de la facon dont le
    ministere nomme ses jeux de donnees.
    """
    # TODO : boucler sur DATASETS et appeler download_dataset pour chacun
    ...


if __name__ == "__main__":
    main()
