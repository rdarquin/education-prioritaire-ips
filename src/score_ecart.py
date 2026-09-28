"""Score d'ecart d'IPS : une variable, une valeur par college.

DEFINITION

Le dispositif classe une part pi des colleges d'un champ. On appelle IPS*
l'IPS du college situe exactement a cette position dans la distribution
croissante des IPS du champ : c'est le seuil qu'appliquerait une regle qui
classerait le meme NOMBRE de colleges, mais uniquement d'apres leur IPS.

Chaque college recoit alors :

    score = 0            si IPS < IPS* et classe EP      -> conforme
    score = 0            si IPS > IPS* et non classe     -> conforme
    score = |IPS - IPS*| sinon                           -> ecart

Les deux cas d'ecart sont de sens oppose, et la colonne `type_ecart` les
distingue :

    "oublie"     : IPS < IPS* mais non classe. Le dispositif ne l'a pas pris
                   alors qu'une regle IPS l'aurait pris.
    "sur-inclus" : IPS > IPS* mais classe. Le dispositif l'a pris alors
                   qu'une regle IPS ne l'aurait pas pris.

DEUX VARIANTES, DEUX QUESTIONS DIFFERENTES

Le seuil depend du champ sur lequel on compte l'enveloppe. Ce module en calcule
deux, cote a cote :

    NATIONAL   - un seuil unique, sur la France entiere.
                 Question : l'education prioritaire cible-t-elle les colleges
                 les plus defavorises DU PAYS ?
                 C'est une question d'equite territoriale.

    ACADEMIQUE - un seuil par academie, chaque academie etant jugee sur sa
                 propre enveloppe et sa propre distribution.
                 Question : chaque academie cible-t-elle bien SES colleges les
                 plus defavorises, a moyens donnes ?
                 C'est une question de qualite de la decision locale.

La seconde variante n'est pas un raffinement de la premiere : elle correspond a
la facon dont la politique a reellement ete conduite. L'enveloppe d'education
prioritaire a ete repartie par academie, puis le recteur a designe les colleges
les plus defavorises de son academie. Un seuil national mesure donc un ecart a
une regle que personne n'a appliquee — ce qui reste une question legitime, mais
pas la meme.

L'ecart entre les deux variantes est le plus spectaculaire a Paris : 24
sur-inclusions au seuil national, dont 24 sont arithmetiquement forcees
(6 colleges parisiens seulement sont sous le seuil national, et 30 sont
classes) ; il n'en reste que 8 au seuil academique.

POURQUOI LE SEUIL N'EST PAS ARBITRAIRE

pi n'est pas choisi : c'est le taux de classement OBSERVE sur le champ. Le
seuil represente donc l'enveloppe reellement allouee, pas une convention.
Consequence algebrique : les colleges sous le seuil et les colleges classes
etant en nombre egal, les deux masses d'erreur se recomposent et le seuil
s'elimine de la somme. `controler_identite` verifie, DANS CHAQUE CHAMP, que

    somme des scores = somme des IPS des classes
                     - somme des IPS des n colleges d'IPS le plus faible

autrement dit que le score total mesure l'ecart de masse d'IPS entre
l'allocation reelle et l'allocation optimale A ENVELOPPE EGALE.

EX AEQUO AU SEUIL

Plusieurs colleges peuvent avoir exactement l'IPS du seuil. La definition les
traite sans cas particulier : leur ecart vaut |IPS* - IPS*| = 0, qu'ils soient
classes ou non. En revanche l'ensemble optimal n'est alors pas unique, et la
liste nominative des colleges en ecart est ambigue pour eux. Ils sont donc
marques "au seuil" plutot que "conforme", pour rester honnete.

RESERVE

L'IPS n'est pas le critere officiel de classement. Un score eleve ne prouve
pas une erreur administrative : il mesure un desaccord entre deux instruments.

Lancement (depuis la racine du projet) :
    uv run python -m src.score_ecart
"""

import numpy as np
import pandas as pd

from src.analyse import charger, restreindre_au_public
from src.config import PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# suffixe de colonne, decoupage definissant l'enveloppe, libelle affiche.
# Une liste vide signifie "un seul champ, la France entiere".
VARIANTES = [
    ("", [], "national"),
    ("_academie", ["code_academie"], "académique"),
]


def noms_colonnes(suffixe: str) -> tuple[str, str, str]:
    """Noms des trois colonnes produites par une variante.

    La variante nationale conserve les noms historiques `ips_seuil`,
    `score_ecart_ips` et `type_ecart`, sur lesquels reposent les modules de
    figures. D'ou cette irregularite : `score_ecart_ips` et non `score_ecart`.
    """
    if suffixe == "":
        return "ips_seuil", "score_ecart_ips", "type_ecart"
    return f"ips_seuil{suffixe}", f"score_ecart{suffixe}", f"type_ecart{suffixe}"


def seuil_budgetaire(sous: pd.DataFrame) -> float:
    """IPS du college qui ferme l'enveloppe du champ.

    Si n colleges du champ sont classes, le seuil est l'IPS du n-ieme le plus
    faible. Defini par EFFECTIF et non par quantile : c'est l'enveloppe qui
    fixe le seuil, et cette formulation garantit que le nombre de colleges
    sous le seuil egale le nombre de classes, condition de l'identite
    verifiee dans `controler_identite`.

    Returns:
        L'IPS seuil, ou NaN si le champ ne compte aucun college classe (il n'y
        a alors pas d'enveloppe, donc pas de seuil).
    """
    n_classes = int(sous["classe_ep"].sum())
    if n_classes == 0:
        return np.nan
    return sous["ips"].nsmallest(n_classes).max()


def ajouter_score(df: pd.DataFrame, groupes: list[str],
                  suffixe: str = "") -> pd.DataFrame:
    """Ajoute le seuil, le score et le type d'ecart pour un decoupage donne.

    Args:
        df: les colleges, avec `ips` et `classe_ep`.
        groupes: colonnes definissant le champ sur lequel l'enveloppe est
            comptee. Liste vide pour la variante nationale,
            ["code_academie"] pour la variante academique.
        suffixe: suffixe des colonnes produites (voir `noms_colonnes`).

    Returns:
        Le tableau d'entree augmente de trois colonnes.
    """
    col_seuil, col_score, col_type = noms_colonnes(suffixe)
    df = df.copy()

    if groupes:
        seuils = df.groupby(groupes, sort=False).apply(
            seuil_budgetaire, include_groups=False)
        # `index.map` accepte indistinctement un Index et un MultiIndex : le
        # meme code sert donc a tous les decoupages.
        df[col_seuil] = df.set_index(groupes).index.map(seuils)
    else:
        df[col_seuil] = seuil_budgetaire(df)

    sous_seuil = df["ips"] < df[col_seuil]
    au_seuil = df["ips"] == df[col_seuil]
    classe = df["classe_ep"]

    # Les deux cas d'ecart. Les ex aequo au seuil n'en font partie ni d'un
    # cote ni de l'autre : leur ecart serait nul de toute facon.
    oublie = sous_seuil & ~classe
    sur_inclus = ~sous_seuil & ~au_seuil & classe & df[col_seuil].notna()

    df[col_score] = 0.0
    df.loc[oublie | sur_inclus, col_score] = (
        df.loc[oublie | sur_inclus, "ips"] - df.loc[oublie | sur_inclus, col_seuil]
    ).abs()

    df[col_type] = "conforme"
    df.loc[au_seuil, col_type] = "au seuil"
    df.loc[oublie, col_type] = "oublie"
    df.loc[sur_inclus, col_type] = "sur-inclus"
    # Un champ sans aucun classe n'a pas de seuil : on ne prononce rien.
    df.loc[df[col_seuil].isna(), col_type] = "sans seuil"

    return df


def controler_identite(df: pd.DataFrame, groupes: list[str],
                       suffixe: str, libelle: str) -> None:
    """Verifie, dans chaque champ, que la somme des scores egale l'ecart de masse.

    Deux calculs independants du meme nombre. S'ils divergent, le score est mal
    calcule et rien ne doit etre publie. La verification porte sur CHAQUE champ
    du decoupage, pas seulement sur le total : une erreur de seuil dans une
    seule academie serait invisible sur l'agregat.
    """
    _, col_score, _ = noms_colonnes(suffixe)
    champs = df.groupby(groupes, sort=False) if groupes else [("France", df)]
    controles = 0

    for cle, sous in champs:
        n_classes = int(sous["classe_ep"].sum())
        if n_classes == 0:
            continue
        total = sous[col_score].sum()
        ecart_masse = (sous.loc[sous["classe_ep"], "ips"].sum()
                       - sous["ips"].nsmallest(n_classes).sum())
        if not np.isclose(total, ecart_masse, rtol=1e-6, atol=1e-6):
            raise ValueError(
                f"variante {libelle}, champ {cle} : somme des scores "
                f"({total:.4f}) et ecart de masse d'IPS ({ecart_masse:.4f}) "
                f"divergent. Le score est faux.")
        controles += 1

    print(f"  {libelle:11s} : identite verifiee sur {controles} champs")


def resumer(df: pd.DataFrame, suffixe: str, libelle: str) -> None:
    """Affiche la distribution de la variable."""
    _, col_score, col_type = noms_colonnes(suffixe)
    n_classes = int(df["classe_ep"].sum())

    print(f"\n{'=' * 78}")
    print(f"SEUIL {libelle.upper()} — DISTRIBUTION DU SCORE")
    print("=" * 78)
    print(f"\n{len(df)} colleges publics, {n_classes} classes "
          f"({100 * n_classes / len(df):.1f} %)")

    for type_ecart in ["oublie", "sur-inclus"]:
        groupe = df[df[col_type] == type_ecart]
        if groupe.empty:
            continue
        scores = groupe[col_score]
        print(f"  {type_ecart:11s} : {len(groupe):>5d} colleges | "
              f"masse {scores.sum():>9.1f} | moyenne {scores.mean():>5.2f} | "
              f"median {scores.median():>5.2f} | max {scores.max():>5.1f}")
    conformes = int(df[col_type].isin(["conforme", "au seuil"]).sum())
    print(f"  {'conforme':11s} : {conformes:>5d} colleges "
          f"(dont {(df[col_type] == 'au seuil').sum()} exactement au seuil)")
    print(f"  score total {df[col_score].sum():>9,.1f} pts, soit "
          f"{df[col_score].sum() / n_classes:.2f} pts par place")


def comparer_academies(df: pd.DataFrame) -> pd.DataFrame:
    """Confronte les deux variantes academie par academie.

    C'est la table qui rend la variante utile : elle montre quelle part des
    sur-inclusions nationales d'une academie est arithmetiquement forcee par
    l'etalon national, et ce qu'il reste une fois l'academie jugee sur
    elle-meme.
    """
    lignes = []
    for (code, nom), g in df.groupby(["code_academie", "academie"], sort=False):
        n_classes = int(g["classe_ep"].sum())
        if n_classes == 0:
            continue
        seuil_nat = g["ips_seuil"].iloc[0]
        sous_seuil_nat = int((g["ips"] < seuil_nat).sum())

        # Recouvrement : combien des classes reels figurent parmi les n
        # colleges les plus defavorises de l'academie ?
        optimal = set(g.nsmallest(n_classes, "ips")["uai"])
        reels = set(g.loc[g["classe_ep"], "uai"])

        lignes.append({
            "code_academie": code,
            "academie": nom,
            "colleges": len(g),
            "classes": n_classes,
            "sous_seuil_national": sous_seuil_nat,
            # Minimum de sur-inclusions impose par l'etalon national : on ne
            # peut pas classer n colleges si moins de n sont sous le seuil.
            "sur_incl_forcees": max(0, n_classes - sous_seuil_nat),
            "sur_incl_national": int((g["type_ecart"] == "sur-inclus").sum()),
            "sur_incl_academique": int((g["type_ecart_academie"] == "sur-inclus").sum()),
            "oublis_academique": int((g["type_ecart_academie"] == "oublie").sum()),
            "seuil_national": round(seuil_nat, 1),
            "seuil_academique": round(g["ips_seuil_academie"].iloc[0], 1),
            "recouvrement_pct": round(100 * len(reels & optimal) / n_classes, 1),
            "score_par_place_national": round(
                g["score_ecart_ips"].sum() / n_classes, 2),
            "score_par_place_academique": round(
                g["score_ecart_academie"].sum() / n_classes, 2),
        })
    return pd.DataFrame(lignes)


def main() -> None:
    df = charger()
    df = restreindre_au_public(df)

    print(f"\n{len(df)} colleges publics analyses")
    print(f"{df['code_academie'].nunique()} academies")
    if df["code_academie"].isna().any():
        print(f"  ATTENTION : {df['code_academie'].isna().sum()} colleges "
              f"sans academie renseignee")

    for suffixe, groupes, libelle in VARIANTES:
        df = ajouter_score(df, groupes, suffixe)

    print("\nControle du calcul :")
    for suffixe, groupes, libelle in VARIANTES:
        controler_identite(df, groupes, suffixe, libelle)

    for suffixe, _, libelle in VARIANTES:
        resumer(df, suffixe, libelle)

    academies = comparer_academies(df)

    print(f"\n{'=' * 78}")
    print("LES DEUX VARIANTES, ACADEMIE PAR ACADEMIE")
    print("=" * 78)
    colonnes = ["academie", "colleges", "classes", "sous_seuil_national",
                "sur_incl_forcees", "sur_incl_national", "sur_incl_academique",
                "seuil_academique", "recouvrement_pct"]
    tri = academies.sort_values("sur_incl_national", ascending=False)
    print(tri[colonnes].to_string(index=False))

    print("\n--- recouvrement le plus FAIBLE (academies de 40+ colleges) ---")
    assez = tri[tri["colleges"] >= 40]
    print(assez.nsmallest(8, "recouvrement_pct")[
        ["academie", "colleges", "classes", "recouvrement_pct",
         "score_par_place_academique"]].to_string(index=False))

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)

    colonnes_sortie = [
        "uai", "nom", "secteur", "ep", "ips",
        "ips_seuil", "score_ecart_ips", "type_ecart",
        "ips_seuil_academie", "score_ecart_academie", "type_ecart_academie",
        "code_commune", "nom_commune", "code_departement", "departement",
        "code_academie", "academie", "latitude", "longitude"]

    chemin = DOSSIER_TABLES / "score_ecart_ips.csv"
    df[colonnes_sortie].to_csv(chemin, index=False, encoding="utf-8")
    print(f"\n[+] {chemin.name} ({len(df)} colleges)")
    print(f"    seuil national   : {(df['score_ecart_ips'] > 0).sum()} a score non nul")
    print(f"    seuil academique : {(df['score_ecart_academie'] > 0).sum()} "
          f"a score non nul")

    chemin = DOSSIER_TABLES / "score_ecart_par_academie.csv"
    academies.to_csv(chemin, index=False, encoding="utf-8")
    print(f"[+] {chemin.name} ({len(academies)} lignes)")


if __name__ == "__main__":
    main()
