"""Nettoyage des donnees brutes et construction du fichier d'analyse.

Produit `data/processed/colleges_2024_2025.csv` : une ligne par college, avec
son IPS, sa note moyenne a l'ecrit du DNB, son statut d'education prioritaire
et ses coordonnees geographiques.

Le module affiche ses diagnostics au fur et a mesure. Ce n'est pas du
bavardage : chaque chiffre imprime ici documente une decision de nettoyage,
et devra etre repris dans la section "Limites" du README.

Lancement (depuis la racine du projet) :
    uv run python -m src.preparation
"""

import pandas as pd

from src.config import (DATA_PROCESSED, DATA_RAW, RENTREE_REFERENCE,
                        SESSION_DNB)

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

FICHIER_SORTIE = DATA_PROCESSED / "colleges_2024_2025.csv"


def charger_ips() -> pd.DataFrame:
    """Charge le fichier IPS des colleges et le filtre sur la rentree de reference.

    Returns:
        Un DataFrame d'une ligne par college, colonnes reduites a l'utile.
    """
    df = pd.read_csv(DATA_RAW / "ips_colleges.csv", **LECTURE_CSV)
    total = len(df)

    # Le fichier IPS est un PANEL : une ligne par (college, rentree). Sans ce
    # filtre, chaque college serait compte jusqu'a trois fois.
    df = df[df["rentree_scolaire"] == RENTREE_REFERENCE].copy()

    print(f"  ips_colleges.csv     {total:6d} lignes -> {len(df):6d} "
          f"pour {RENTREE_REFERENCE}")

    colonnes = ["uai", "secteur", "ips", "ecart_type_de_l_ips",
                "code_insee_de_la_commune", "nom_de_la_commune",
                "code_du_departement", "departement", "code_academie", "academie"]
    return df[colonnes]


def charger_annuaire() -> pd.DataFrame:
    """Charge l'annuaire, controle puis supprime les UAI en double.

    L'annuaire n'est pas restreint aux colleges : la jointure se faisant sur
    les UAI du fichier IPS, les autres etablissements ne peuvent pas s'y
    glisser. Les filtrer d'abord ferait courir le risque d'ecarter un college
    type differemment dans l'annuaire — une cite scolaire, par exemple.

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


def charger_ivac() -> pd.DataFrame:
    """Charge les resultats au DNB et les filtre sur la session de reference.

    On retient la NOTE MOYENNE A L'ECRIT de la serie generale, et non le taux
    de reussite. Deux raisons :

      - le taux de reussite est ecrase vers le haut — mediane a 88 %, un tiers
        des colleges au-dessus de 95 % — et ne prend que 53 valeurs distinctes
        sur 5 300 colleges. Il ne distingue plus rien dans le haut de la
        distribution ;
      - la note en prend 102, et se repartit sans butee.

    Serie generale (`_g`) et non professionnelle (`_p`) : cette derniere ne
    concerne au college que les eleves de SEGPA, presents dans une minorite
    d'etablissements. La retenir ferait porter la comparaison sur des
    populations de tailles tres inegales.

    Returns:
        Un DataFrame a une ligne par college : UAI, note, nombre de candidats.
    """
    df = pd.read_csv(DATA_RAW / "ivac_colleges.csv", **LECTURE_CSV)
    total = len(df)

    # Comme le fichier IPS, l'IVAC est un panel : quatre sessions empilees.
    df = df[df["session"] == SESSION_DNB].copy()

    print(f"  ivac_colleges.csv    {total:6d} lignes -> {len(df):6d} "
          f"pour la session {SESSION_DNB}")

    doublons = df["uai"].duplicated().sum()
    if doublons:
        raise ValueError(f"{doublons} UAI en double dans l'IVAC : la jointure "
                         f"dupliquerait des lignes.")

    df = df.rename(columns={"note_a_l_ecrit_g": "note_ecrit_dnb",
                            "nb_candidats_g": "nb_candidats_dnb"})
    return df[["uai", "note_ecrit_dnb", "nb_candidats_dnb"]]


def ajouter_performance(df: pd.DataFrame, ivac: pd.DataFrame) -> pd.DataFrame:
    """Joint les resultats au DNB et mesure ce que la jointure laisse de cote.

    La jointure est volontairement "left" : un college sans resultat au DNB
    reste dans le fichier, avec une note manquante. Il conserve son IPS et son
    statut, et ne sort donc que des analyses qui ont besoin de la note. Le
    supprimer ici reduirait le champ de TOUT le projet pour les besoins d'un
    seul module.

    Args:
        df: la table des colleges, deja jointe a l'annuaire.
        ivac: les resultats au DNB de la session de reference.

    Returns:
        La meme table, augmentee de `note_ecrit_dnb` et `nb_candidats_dnb`.
    """
    df = df.merge(ivac, on="uai", how="left", validate="one_to_one")

    df["note_ecrit_dnb"] = pd.to_numeric(df["note_ecrit_dnb"], errors="coerce")
    df["nb_candidats_dnb"] = pd.to_numeric(df["nb_candidats_dnb"],
                                           errors="coerce")

    sans_note = df["note_ecrit_dnb"].isna()
    print(f"\n  sans resultat au DNB : {sans_note.sum()} "
          f"({100 * sans_note.mean():.1f}%)")

    # Meme verification que pour les IPS non publies : ces colleges sortiront
    # de la comparaison des etalons, et il faut savoir si leur depart la
    # deplace. Un ecart marque signalerait que la note n'est pas absente au
    # hasard — typiquement, de tres petits etablissements.
    if sans_note.any():
        part_ep = 100 * (df.loc[sans_note, "ep"] != "hors EP").mean()
        part_ep_globale = 100 * (df["ep"] != "hors EP").mean()
        ips_absents = df.loc[sans_note, "ips"].mean()
        print(f"    part en education prioritaire : {part_ep:.1f}% "
              f"(contre {part_ep_globale:.1f}% sur l'ensemble)")
        print(f"    IPS moyen : {ips_absents:.1f} "
              f"(contre {df['ips'].mean():.1f} sur l'ensemble)")

    # Une note assise sur une poignee de candidats est volatile : un eleve de
    # plus ou de moins la deplace sensiblement. On mesure combien de colleges
    # sont dans ce cas, pour que les modules en aval puissent en tenir compte.
    petits = df["nb_candidats_dnb"] < 30
    print(f"    moins de 30 candidats : {petits.sum()} colleges")

    return df


def joindre_et_diagnostiquer(ips: pd.DataFrame, annuaire: pd.DataFrame) -> pd.DataFrame:
    """Apparie IPS et annuaire, mesure les pertes, puis applique les exclusions.

    La jointure est d'abord faite en mode "left" — on garde toutes les lignes
    IPS, meme non appariees — afin de pouvoir MESURER ce qu'on s'apprete a
    perdre avant de le perdre. Les exclusions n'interviennent qu'ensuite.

    Args:
        ips: table IPS des colleges, rentree de reference.
        annuaire: annuaire dedoublonne.

    Returns:
        La table finale, sans college non apparie ni IPS non publie.
    """
    df = ips.merge(annuaire, on="uai", how="left", validate="one_to_one")

    # `validate="one_to_one"` fait echouer la jointure si un UAI apparaissait
    # plusieurs fois d'un cote ou de l'autre. C'est une ceinture de securite :
    # mieux vaut une erreur bruyante qu'un fichier silencieusement gonfle.

    # ---- Diagnostic 1 : colleges absents de l'annuaire -------------------
    absents = df["nom_etablissement"].isna()
    print(f"\n  non apparies dans l'annuaire : {absents.sum()} "
          f"({100 * absents.mean():.1f}%)")
    if absents.any():
        print("    top 5 departements :",
              df.loc[absents, "code_du_departement"].value_counts().head(5).to_dict())

    # ---- Diagnostic 2 : IPS non publies ----------------------------------
    # Le fichier laisse la case vide quand l'IPS n'est pas diffuse.
    # `errors="coerce"` transforme ces cases en valeur manquante.
    df["ips"] = pd.to_numeric(df["ips"], errors="coerce")
    df["ecart_type_de_l_ips"] = pd.to_numeric(df["ecart_type_de_l_ips"],
                                              errors="coerce")

    sans_ips = df["ips"].isna()
    print(f"\n  IPS non publie : {sans_ips.sum()} ({100 * sans_ips.mean():.1f}%)")

    # VERIFICATION PROMISE : exclure ces colleges biaise-t-il l'analyse ?
    # Si les colleges sans IPS etaient nettement plus ou moins souvent classes
    # en education prioritaire que les autres, leur exclusion deplacerait le
    # resultat. On le verifie au lieu de le supposer.
    apparies_sans_ips = df[sans_ips & ~absents]
    if len(apparies_sans_ips):
        part_ep = 100 * (apparies_sans_ips["ep"] != "hors EP").mean()
        part_ep_globale = 100 * (df.loc[~absents, "ep"] != "hors EP").mean()
        print(f"    part en education prioritaire : {part_ep:.1f}% "
              f"(contre {part_ep_globale:.1f}% sur l'ensemble)")

    # ---- Exclusions ------------------------------------------------------
    avant = len(df)
    df = df[~absents & ~sans_ips].copy()
    print(f"\n  exclusions : {avant} -> {len(df)} colleges retenus")

    return df


def finaliser(df: pd.DataFrame) -> pd.DataFrame:
    """Convertit les types, renomme, ordonne les colonnes."""
    # Les coordonnees doivent etre numeriques pour toute cartographie.
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    sans_coord = df["latitude"].isna().sum()
    print(f"  sans coordonnees geographiques : {sans_coord}")

    # On prefere le libelle de l'annuaire, accentue et en casse normale
    # ("Collège Jules Vallès"), a celui du fichier IPS, en majuscules non
    # accentuees. Il sera lisible sur une carte.
    df = df.rename(columns={
        "nom_etablissement": "nom",
        "ecart_type_de_l_ips": "ecart_type_ips",
        "code_insee_de_la_commune": "code_commune",
        "nom_de_la_commune": "nom_commune",
        "code_du_departement": "code_departement",
    })

    colonnes = ["uai", "nom", "secteur", "ep", "ips", "ecart_type_ips",
                "note_ecrit_dnb", "nb_candidats_dnb",
                "code_commune", "nom_commune", "code_departement", "departement",
                "code_academie", "academie", "latitude", "longitude"]
    return df[colonnes].sort_values("uai").reset_index(drop=True)


def main() -> None:
    """Construit le fichier d'analyse a partir des trois fichiers bruts."""
    print(f"Rentree de reference : {RENTREE_REFERENCE}\n")

    print("Lecture :")
    ips = charger_ips()
    annuaire = charger_annuaire()
    ivac = charger_ivac()

    df = joindre_et_diagnostiquer(ips, annuaire)
    df = ajouter_performance(df, ivac)
    df = finaliser(df)

    print("\nResultat :")
    print(df.groupby(["secteur", "ep"]).agg(
        effectif=("ips", "size"), ips_moyen=("ips", "mean"),
        note_dnb_moyenne=("note_ecrit_dnb", "mean")
    ).round(1).to_string())

    FICHIER_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FICHIER_SORTIE, index=False, encoding="utf-8")
    print(f"\n[+] {FICHIER_SORTIE.name} ecrit ({len(df)} lignes, "
          f"{FICHIER_SORTIE.stat().st_size / 1_000_000:.1f} Mo)")


if __name__ == "__main__":
    main()
