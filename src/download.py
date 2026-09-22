"""Telechargement des donnees brutes depuis l'API Opendatasoft.

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
    return f"{API_BASE}/{dataset_id}/exports/csv?delimiter=;&use_labels=false"


def download_dataset(dataset_id: str, destination: Path, force: bool = False) -> Path:
    """Telecharge un jeu de donnees et l'ecrit sur disque.

    Args:
        dataset_id: identifiant Opendatasoft (voir DATASETS dans config.py).
        destination: chemin du fichier CSV a ecrire.
        force: si False et que le fichier existe deja, ne retelecharge pas.

    Returns:
        Le chemin du fichier ecrit.

    Raises:
        requests.HTTPError: si l'API repond un code d'erreur (404, 500...).
    """
    # (1) Idempotence. Relancer le script ne doit rien couter quand les
    # donnees sont deja la : c'est ce qui permet de l'executer sans hesiter.
    if destination.exists() and not force:
        print(f"[=] {destination.name} deja present, telechargement ignore.")
        return destination

    url = build_export_url(dataset_id)
    print(f"[>] Telechargement de {dataset_id} ...")

    # (2) stream=True : la reponse n'est pas chargee entierement en memoire,
    # on la lira par morceaux. timeout : sans lui, un serveur qui cesse de
    # repondre bloquerait le script indefiniment, sans aucun message.
    response = requests.get(url, stream=True, timeout=60)

    # (3) Sans cet appel, une reponse 404 serait ecrite telle quelle dans le
    # fichier : on croirait avoir des donnees, et l'erreur n'apparaitrait que
    # bien plus tard, sous une forme incomprehensible.
    response.raise_for_status()

    # (4) data/raw/ n'est pas versionne : il peut tres bien ne pas exister
    # sur la machine qui vient de cloner le depot.
    destination.parent.mkdir(parents=True, exist_ok=True)

    # (5) On ecrit d'abord dans un fichier temporaire, renomme seulement une
    # fois le telechargement acheve. Sans cette precaution, une coupure en
    # cours de route laisserait un fichier tronque que le test (1) prendrait
    # ensuite pour un telechargement reussi.
    temporaire = destination.with_name(destination.name + ".part")

    # "wb" = write binary : on ecrit les octets recus tels quels, sans
    # reencodage. Le bloc `with` referme le fichier meme en cas d'erreur.
    with open(temporaire, "wb") as fichier:
        for morceau in response.iter_content(chunk_size=8192):
            fichier.write(morceau)

    temporaire.replace(destination)

    taille_mo = destination.stat().st_size / 1_000_000
    print(f"[+] {destination.name} ecrit ({taille_mo:.1f} Mo)")
    return destination


def main() -> None:
    """Telecharge les trois jeux de donnees du projet.

    Parcourt DATASETS (defini dans config.py) et telecharge chaque jeu dans
    DATA_RAW sous le nom `<cle>.csv` — par exemple `ips_ecoles.csv`.

    Note : la cle du dictionnaire (`ips_ecoles`) sert de nom de fichier, pas
    l'identifiant Opendatasoft (`fr-en-ips-ecoles-ap2022`). Tes fichiers
    locaux portent ainsi des noms lisibles, independants de la facon dont le
    ministere nomme ses jeux de donnees.
    """
    for cle, dataset_id in DATASETS.items():
        download_dataset(dataset_id, DATA_RAW / f"{cle}.csv")

    print(f"\n{len(DATASETS)} jeux de donnees disponibles dans {DATA_RAW}")


if __name__ == "__main__":
    main()
