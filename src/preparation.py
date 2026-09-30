"""Nettoyage des donnees brutes et construction du fichier d'analyse.

Produit `data/processed/colleges_2024_2025.csv` : une ligne par college, avec
son IPS, son score aux evaluations nationales de sixieme, son statut
d'education prioritaire et ses coordonnees geographiques.

Le module affiche ses diagnostics au fur et a mesure. Ce n'est pas du
bavardage : chaque chiffre imprime ici documente une decision de nettoyage,
et devra etre repris dans la section "Limites" du README.

Lancement (depuis la racine du projet) :
    uv run python -m src.preparation
"""

import pandas as pd

from src.config import (ANNEE_EVAL6, DATA_PROCESSED, DATA_RAW,
                        RENTREE_REFERENCE)

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


def charger_eval6() -> pd.DataFrame:
    """Charge les evaluations nationales de debut de sixieme.

    POURQUOI CET INDICATEUR

    Le brevet est concu nationalement mais CORRIGE localement, par des
    commissions d'harmonisation academiques : un 10 a Creteil n'est pas
    necessairement un 10 a Rennes. Les evaluations de sixieme, elles, sont
    passees le meme jour, sur le meme sujet, et corrigees de facon centralisee.
    Aucune marge d'appreciation locale n'intervient.

    La demonstration tient en un cas. Rapporte a ce que leur IPS laisse
    attendre, les colleges de Mayotte font MIEUX que prevu au brevet (+1,6
    ecart-type) et BIEN PIRE a l'evaluation de sixieme (-2,3). Les deux ne
    peuvent pas etre vrais ensemble, et c'est la version brevet qui est
    invraisemblable pour l'academie dont l'IPS est le plus bas de France.

    L'indicateur est aussi plus fin (235 valeurs distinctes contre 101), plus
    stable d'une annee sur l'autre (+0,899 contre +0,848) et mieux couvert
    (5 310 colleges publics sur 5 325).

    CE QU'IL MESURE, ET CE QU'IL NE MESURE PAS

    L'evaluation a lieu en SEPTEMBRE, a l'entree en sixieme. Les eleves n'ont
    encore rien recu du college. Le score mesure donc le niveau a l'ARRIVEE,
    pas ce que le college produit. Comme mesure du besoin, c'est un avantage
    decisif : il n'est pas contamine par les moyens que le college recoit au
    titre de l'education prioritaire. Comme mesure de la performance du
    college, ce n'en est pas une.

    Reserve residuelle : l'evaluation reste en aval de l'ECOLE, qui peut
    elle-meme relever de l'education prioritaire.

    LE SCORE RETENU

    Le fichier donne un score par discipline, sur une echelle standardisee
    centree sur 250. On retient la MOYENNE du francais et des mathematiques :
    les deux disciplines mesurent le meme desavantage et les separer
    dedoublerait l'analyse sans rien apprendre.

    Returns:
        Un DataFrame a une ligne par college : UAI, score moyen, scores par
        discipline, effectif evalue.
    """
    df = pd.read_csv(DATA_RAW / "eval6_colleges.csv", **LECTURE_CSV)
    total = len(df)

    # Le fichier empile neuf millesimes ET trois sous-populations (Ensemble,
    # Fille, Garcon) ET deux disciplines. Sans les deux premiers filtres, un
    # college compterait cinquante-quatre lignes.
    df = df[(df["annee"].str[:4] == ANNEE_EVAL6)
            & (df["caracteristique"] == "Ensemble")].copy()

    print(f"  eval6_colleges.csv   {total:6d} lignes -> {len(df):6d} "
          f"pour l'annee {ANNEE_EVAL6}")

    df["score_moyen"] = pd.to_numeric(df["score_moyen"], errors="coerce")
    df["effectif"] = pd.to_numeric(df["effectif"], errors="coerce")

    # Une ligne par (college, discipline) -> une colonne par discipline.
    scores = df.pivot_table(index="uai", columns="discipline",
                            values="score_moyen", aggfunc="first")
    manquantes = {"Français", "Mathématiques"} - set(scores.columns)
    if manquantes:
        raise ValueError(f"disciplines absentes du fichier : {manquantes}")

    scores = scores.rename(columns={"Français": "eval6_francais",
                                    "Mathématiques": "eval6_maths"})
    scores["eval6"] = scores[["eval6_francais", "eval6_maths"]].mean(axis=1)
    scores["effectif_eval6"] = df.groupby("uai")["effectif"].max()

    return scores.reset_index()


def ajouter_eval6(df: pd.DataFrame, eval6: pd.DataFrame) -> pd.DataFrame:
    """Joint les evaluations de sixieme et mesure ce que la jointure laisse de cote.

    La jointure est volontairement "left" : un college sans evaluation reste
    dans le fichier, avec un score manquant. Il conserve son IPS et son statut,
    et ne sort que des analyses qui ont besoin du score. Le supprimer ici
    reduirait le champ de TOUT le projet pour les besoins d'un seul etalon.

    Args:
        df: la table des colleges, deja jointe a l'annuaire.
        eval6: les evaluations de sixieme de l'annee de reference.

    Returns:
        La meme table, augmentee des colonnes `eval6*`.
    """
    df = df.merge(eval6, on="uai", how="left", validate="one_to_one")

    sans_score = df["eval6"].isna()
    print(f"\n  sans evaluation de sixieme : {sans_score.sum()} "
          f"({100 * sans_score.mean():.1f}%)")

    # Meme verification que pour les IPS non publies : ces colleges sortiront
    # des analyses fondees sur l'evaluation, et il faut savoir si leur depart
    # les deplace. Un ecart marque signalerait une absence non aleatoire.
    if sans_score.any():
        part_ep = 100 * (df.loc[sans_score, "ep"] != "hors EP").mean()
        part_ep_globale = 100 * (df["ep"] != "hors EP").mean()
        ips_absents = df.loc[sans_score, "ips"].mean()
        print(f"    part en education prioritaire : {part_ep:.1f}% "
              f"(contre {part_ep_globale:.1f}% sur l'ensemble)")
        print(f"    IPS moyen : {ips_absents:.1f} "
              f"(contre {df['ips'].mean():.1f} sur l'ensemble)")

    # Un score assis sur une poignee d'eleves est volatile. On mesure combien
    # de colleges sont dans ce cas, pour que les modules en aval le sachent.
    petits = df["effectif_eval6"] < 30
    print(f"    moins de 30 eleves evalues : {petits.sum()} colleges")

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
                "eval6", "eval6_francais", "eval6_maths", "effectif_eval6",
                "code_commune", "nom_commune", "code_departement", "departement",
                "code_academie", "academie", "latitude", "longitude"]
    return df[colonnes].sort_values("uai").reset_index(drop=True)


def main() -> None:
    """Construit le fichier d'analyse a partir des trois fichiers bruts."""
    print(f"Rentree de reference : {RENTREE_REFERENCE}\n")

    print("Lecture :")
    ips = charger_ips()
    annuaire = charger_annuaire()
    eval6 = charger_eval6()

    df = joindre_et_diagnostiquer(ips, annuaire)
    df = ajouter_eval6(df, eval6)
    df = finaliser(df)

    print("\nResultat :")
    print(df.groupby(["secteur", "ep"]).agg(
        effectif=("ips", "size"), ips_moyen=("ips", "mean"),
        eval6_moyen=("eval6", "mean")
    ).round(1).to_string())

    FICHIER_SORTIE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(FICHIER_SORTIE, index=False, encoding="utf-8")
    print(f"\n[+] {FICHIER_SORTIE.name} ecrit ({len(df)} lignes, "
          f"{FICHIER_SORTIE.stat().st_size / 1_000_000:.1f} Mo)")


if __name__ == "__main__":
    main()
