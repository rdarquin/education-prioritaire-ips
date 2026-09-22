"""Nettoyage des donnees brutes et construction du fichier d'analyse.

Produit `data/processed/etablissements_2024_2025.csv` : une ligne par
etablissement, avec son IPS, son statut d'education prioritaire et ses
coordonnees geographiques.

Le module affiche ses diagnostics au fur et a mesure. Ce n'est pas du
bavardage : chaque chiffre imprime ici documente une decision de nettoyage,
et devra etre repris dans la section "Limites" du README.

Lancement (depuis la racine du projet) :
    uv run python -m src.preparation
"""

from pathlib import Path

import pandas as pd

from src.config import DATA_PROCESSED, DATA_RAW, RENTREE_REFERENCE

# Parametres de lecture communs aux trois fichiers.
#   sep=";"                 : convention Opendatasoft
#   encoding="utf-8-sig"    : neutralise le BOM en tete de fichier, sans quoi
#                             la premiere colonne s'appellerait "﻿rentree_scolaire"
#   dtype=str               : TOUT est lu en texte. Indispensable ici : les codes
#                             departement ("01", "2A") et commune ("01004")
#                             perdraient leur zero initial en etant lus comme
#                             des nombres, et "2A" echouerait. Les colonnes
#                             reellement numeriques seront converties a la main.
LECTURE_CSV = dict(sep=";", encoding="utf-8-sig", dtype=str)

FICHIER_SORTIE = DATA_PROCESSED / "etablissements_2024_2025.csv"


def charger_ips(nom_fichier: str, niveau: str) -> pd.DataFrame:
    """Charge un fichier IPS, le filtre sur la rentree de reference, harmonise.

    Args:
        nom_fichier: nom du CSV dans data/raw/ (ex. "ips_ecoles.csv").
        niveau: "ecole" ou "college", ajoute en colonne pour pouvoir
            empiler les deux fichiers ensuite.

    Returns:
        Un DataFrame aux colonnes harmonisees entre ecoles et colleges.
    """
    df = pd.read_csv(DATA_RAW / nom_fichier, **LECTURE_CSV)
    total = len(df)

    # Les fichiers IPS sont des PANELS : une ligne par (etablissement, rentree).
    # Sans ce filtre, chaque etablissement serait compte jusqu'a trois fois.
    df = df[df["rentree_scolaire"] == RENTREE_REFERENCE].copy()

    print(f"  {nom_fichier:20s} {total:6d} lignes -> {len(df):6d} pour {RENTREE_REFERENCE}")

    # Les deux fichiers ne nomment pas leurs colonnes de la meme facon :
    # "code_de_l_academie" cote ecoles, "code_academie" cote colleges. On
    # harmonise pour pouvoir les empiler.
    df = df.rename(columns={"code_de_l_academie": "code_academie"})

    # L'ecart-type de l'IPS n'existe que pour les colleges. On cree la colonne
    # vide cote ecoles afin que les deux tables aient la meme structure.
    if "ecart_type_de_l_ips" not in df.columns:
        df["ecart_type_de_l_ips"] = pd.NA

    df["niveau"] = niveau

    colonnes = ["uai", "niveau", "secteur", "ips", "ecart_type_de_l_ips",
                "code_insee_de_la_commune", "nom_de_la_commune",
                "code_du_departement", "departement", "code_academie", "academie"]
    return df[colonnes]


def charger_annuaire() -> pd.DataFrame:
    """Charge l'annuaire, controle puis supprime les UAI en double.

    Returns:
        Un DataFrame indexable par UAI, sans doublon.
    """
    colonnes = ["identifiant_de_l_etablissement", "nom_etablissement",
                "type_etablissement", "latitude", "longitude",
                "precision_localisation", "appartenance_education_prioritaire"]
    ann = pd.read_csv(DATA_RAW / "annuaire.csv", usecols=colonnes, **LECTURE_CSV)
    ann = ann.rename(columns={"identifiant_de_l_etablissement": "uai"})

    # ---- Controle des doublons -------------------------------------------
    # L'annuaire contient des UAI presents deux fois : le meme etablissement
    # sous deux libelles. Une jointure sans dedoublonnage DUPLIQUERAIT les
    # lignes IPS correspondantes, et gonflerait silencieusement tous les
    # comptages.
    doublons = ann[ann["uai"].duplicated(keep=False)]
    n_uai = doublons["uai"].nunique()

    # Avant de garder arbitrairement la premiere ligne, on verifie que les
    # doublons ne se contredisent pas sur ce qui nous interesse. Si deux
    # lignes d'un meme UAI donnaient des coordonnees ou un statut REP
    # differents, le choix ne serait plus anodin et il faudrait trancher.
    desaccords = (doublons.groupby("uai")[
        ["latitude", "longitude", "appartenance_education_prioritaire"]
    ].nunique(dropna=False) > 1).any(axis=1).sum()

    print(f"  annuaire.csv         {len(ann):6d} lignes, {n_uai} UAI en double")
    print(f"      dont en desaccord sur coordonnees ou statut EP : {desaccords}")

    ann = ann.drop_duplicates("uai", keep="first")

    # Le vide de cette colonne ne signifie pas "donnee manquante" mais
    # "hors education prioritaire". On l'ecrit explicitement : une valeur
    # manquante se propage silencieusement dans les groupby, pas une chaine.
    ann["ep"] = ann["appartenance_education_prioritaire"].fillna("hors EP")

    return ann.drop(columns=["appartenance_education_prioritaire"])


def joindre_et_diagnostiquer(ips: pd.DataFrame, annuaire: pd.DataFrame) -> pd.DataFrame:
    """Apparie IPS et annuaire, mesure les pertes, puis applique les exclusions.

    La jointure est d'abord faite en mode "left" — on garde toutes les lignes
    IPS, meme non appariees — afin de pouvoir MESURER ce qu'on s'apprete a
    perdre avant de le perdre. Les exclusions n'interviennent qu'ensuite.

    Args:
        ips: table IPS empilee (ecoles + colleges), rentree de reference.
        annuaire: annuaire dedoublonne.

    Returns:
        La table finale, sans etablissement non apparie ni IPS non publie.
    """
    df = ips.merge(annuaire, on="uai", how="left", validate="one_to_one")

    # `validate="one_to_one"` fait echouer la jointure si un UAI apparaissait
    # plusieurs fois d'un cote ou de l'autre. C'est une ceinture de securite :
    # mieux vaut une erreur bruyante qu'un fichier silencieusement gonfle.

    # ---- Diagnostic 1 : etablissements absents de l'annuaire --------------
    absents = df["nom_etablissement"].isna()
    print(f"\n  non apparies dans l'annuaire : {absents.sum()} "
          f"({100 * absents.mean():.1f}%)")
    if absents.any():
        print("    repartition par niveau :",
              df.loc[absents, "niveau"].value_counts().to_dict())
        print("    top 5 departements    :",
              df.loc[absents, "code_du_departement"].value_counts().head(5).to_dict())

    # ---- Diagnostic 2 : IPS non publies ----------------------------------
    # Les ecoles utilisent le code "NS" (moins de 25 eleves de CM2 sur cinq
    # ans), les colleges laissent la case vide. `errors="coerce"` transforme
    # l'un comme l'autre en valeur manquante.
    df["ips"] = pd.to_numeric(df["ips"], errors="coerce")
    df["ecart_type_de_l_ips"] = pd.to_numeric(df["ecart_type_de_l_ips"], errors="coerce")

    sans_ips = df["ips"].isna()
    print(f"\n  IPS non publie : {sans_ips.sum()} ({100 * sans_ips.mean():.1f}%)")
    print("    repartition par niveau :",
          df.loc[sans_ips, "niveau"].value_counts().to_dict())

    # VERIFICATION PROMISE : exclure ces etablissements biaise-t-il l'analyse ?
    # Ils sont censes etre de petites ecoles rurales, donc peu concernees par
    # l'education prioritaire, plutot urbaine. Si c'est vrai, leur exclusion
    # ne devrait guere affecter la question posee. On le verifie au lieu de
    # le supposer.
    apparies_sans_ips = df[sans_ips & ~absents]
    if len(apparies_sans_ips):
        part_ep = 100 * (apparies_sans_ips["ep"] != "hors EP").mean()
        part_ep_globale = 100 * (df.loc[~absents, "ep"] != "hors EP").mean()
        print(f"    part en education prioritaire : {part_ep:.1f}% "
              f"(contre {part_ep_globale:.1f}% sur l'ensemble)")

    # ---- Exclusions ------------------------------------------------------
    avant = len(df)
    df = df[~absents & ~sans_ips].copy()
    print(f"\n  exclusions : {avant} -> {len(df)} etablissements retenus")

    return df


def finaliser(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit les types, renomme, ordonne les colonnes."""
    # Les coordonnees doivent etre numeriques pour toute cartographie.
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    sans_coord = df["latitude"].isna().sum()
    print(f"  sans coordonnees geographiques : {sans_coord}")

    # On prefere le libelle de l'annuaire, accentue et en casse normale
    # ("Ecole elementaire Jules Valles"), a celui des fichiers IPS, en
    # majuscules non accentuees. Il sera lisible sur une carte.
    df = df.rename(columns={
        "nom_etablissement": "nom",
        "ecart_type_de_l_ips": "ecart_type_ips",
        "code_insee_de_la_commune": "code_commune",
        "nom_de_la_commune": "nom_commune",
        "code_du_departement": "code_departement",
    })

    colonnes = ["uai", "niveau", "nom", "secteur", "ep", "ips", "ecart_type_ips",
                "code_commune", "nom_commune", "code_departement", "departement",
                "code_academie", "academie", "latitude", "longitude",
                "precision_localisation"]
    return df[colonnes].sort_values(["niveau", "uai"]).reset_index(drop=True)


def main() -> None:
    """Construit le fichier d'analyse a partir des trois fichiers bruts."""
    print(f"Rentree de reference : {RENTREE_REFERENCE}\n")

    print("Lecture :")
    ips = pd.concat([
        charger_ips("ips_ecoles.csv", "ecole"),
        charger_ips("ips_colleges.csv", "college"),
    ], ignore_index=True)
    annuaire = charger_annuaire()

    df = joindre_et_diagnostiquer(ips, annuaire)
    df = finaliser(df)

    print("\nResultat :")
    print(df.groupby(["niveau", "ep"]).agg(
        effectif=("ips", "size"), ips_moyen=("ips", "mean")
    ).round(1).to_string())

    FICHIER_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FICHIER_SORTIE, index=False, encoding="utf-8")
    print(f"\n[+] {FICHIER_SORTIE.name} ecrit ({len(df)} lignes, "
          f"{FICHIER_SORTIE.stat().st_size / 1_000_000:.1f} Mo)")


if __name__ == "__main__":
    main()
