"""Analyse centrale : confrontation du classement EP et de la realite sociale.

Question : parmi les colleges les plus defavorises socialement, combien
restent hors education prioritaire, et ou se trouvent-ils ?

Le cadre retenu est celui de l'evaluation d'un dispositif de ciblage. On croise
deux variables binaires :

    - etre parmi les X% de colleges les plus defavorises (mesure : IPS)
    - etre classe REP ou REP+ (decision : classement administratif)

Ce croisement donne quatre cases, dont deux sont des divergences. On en tire
deux taux, empruntes au vocabulaire de l'evaluation :

    COUVERTURE : parmi les plus defavorises, quelle part est classee ?
                 -> repond a "le dispositif rate-t-il des colleges ?"

    CIBLAGE    : parmi les classes, quelle part est parmi les plus defavorises ?
                 -> repond a "le dispositif classe-t-il des colleges qui ne
                    sont pas les plus en difficulte ?"

Les deux ne disent pas la meme chose et peuvent evoluer en sens contraire :
elargir le dispositif ameliore la couverture et degrade le ciblage.

Le CIBLAGE est en outre plafonne par construction : si le dispositif classe
plus de colleges que n'en contient le seuil retenu, il ne peut pas tous les y
loger. Au seuil de 10 %, le maximum atteignable n'est que de 48,7 %. C'est ce
qui a motive la mesure sans seuil de `score_ecart.py`.

RAPPEL : le classement EP ne repose pas sur l'IPS. Une divergence n'est donc
pas une erreur, mais un ecart entre deux instruments de mesure.

Lancement (depuis la racine du projet) :
    uv run python -m src.analyse
"""

import pandas as pd

from src.config import DATA_PROCESSED, PROJECT_ROOT

FICHIER_ENTREE = DATA_PROCESSED / "colleges_2024_2025.csv"
DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Seuil principal : les 10% de colleges au plus faible IPS.
# Ce choix est conventionnel, pas naturel. C'est pourquoi la fonction
# `sensibilite_au_seuil` verifie plus bas que les conclusions ne dependent
# pas de cette valeur precise.
SEUIL = 0.10


def charger() -> pd.DataFrame:
    """Charge le fichier d'analyse et ajoute le rang social."""
    df = pd.read_csv(FICHIER_ENTREE, dtype={"code_departement": str,
                                            "code_commune": str})

    # Rang social : position du college dans la distribution des IPS,
    # exprimee entre 0 (IPS le plus faible) et 1 (le plus eleve).
    df["rang_social"] = df["ips"].rank(pct=True)

    # Variable de decision, ramenee a un booleen : classe ou non.
    df["classe_ep"] = df["ep"] != "hors EP"

    # Outre-mer : les codes departement commencant par 97 (Guadeloupe,
    # Martinique, Guyane, La Reunion, Mayotte) et les collectivites du
    # Pacifique. Distinction utile : ces territoires cumulent des IPS tres
    # bas et des dispositifs specifiques.
    df["zone"] = df["code_departement"].str.startswith(("97", "98")).map(
        {True: "outre-mer", False: "metropole"})

    return df


def matrice_ciblage(df: pd.DataFrame, seuil: float = SEUIL) -> None:
    """Affiche le croisement classement x realite sociale."""
    defavorise = df["rang_social"] < seuil
    classe = df["classe_ep"]

    # Les quatre cases du croisement.
    couverts = int((defavorise & classe).sum())
    rates = int((defavorise & ~classe).sum())
    classes_hors_decile = int((~defavorise & classe).sum())
    hors_champ = int((~defavorise & ~classe).sum())

    couverture = 100 * couverts / defavorise.sum()
    ciblage = 100 * couverts / classe.sum()
    # Plafond du ciblage : on ne peut pas loger plus de colleges dans le
    # decile qu'il n'en contient.
    ciblage_max = 100 * defavorise.sum() / classe.sum()

    print(f"\n{'=' * 70}")
    print(f"CROISEMENT CLASSEMENT x IPS  (seuil : {seuil:.0%} les plus defavorises)")
    print("=" * 70)
    print(f"\n--- {len(df)} colleges publics ---")
    print(f"{'':28s}{'classe EP':>14s}{'hors EP':>14s}")
    print(f"{f'parmi les {seuil:.0%} plus bas':28s}{couverts:>14d}{rates:>14d}")
    print(f"{'au-dessus du seuil':28s}{classes_hors_decile:>14d}{hors_champ:>14d}")
    print()
    print(f"  COUVERTURE : {couverture:5.1f}%  "
          f"({couverts} des {defavorise.sum()} plus defavorises sont classes)")
    print(f"  CIBLAGE    : {ciblage:5.1f}%  "
          f"({couverts} des {classe.sum()} classes sont parmi les plus defavorises)")
    print(f"               plafond atteignable a ce seuil : {ciblage_max:.1f}%")
    print(f"  >> {rates} colleges tres defavorises restent hors dispositif")


def sensibilite_au_seuil(df: pd.DataFrame) -> None:
    """Verifie que les conclusions ne tiennent pas au seuil choisi.

    Un resultat qui bascule quand on passe de 10% a 15% n'est pas un resultat,
    c'est un artefact. Cette verification doit accompagner toute analyse
    reposant sur un seuil arbitraire.
    """
    print(f"\n{'=' * 70}")
    print("SENSIBILITE AU SEUIL")
    print("=" * 70)

    lignes = []
    for seuil in [0.05, 0.10, 0.15, 0.20, 0.25]:
        defavorise = df["rang_social"] < seuil
        classe = df["classe_ep"]
        couverts = (defavorise & classe).sum()
        lignes.append({
            "seuil": f"{seuil:.0%}",
            "effectif_seuil": int(defavorise.sum()),
            "couverture_%": round(100 * couverts / defavorise.sum(), 1),
            "ciblage_%": round(100 * couverts / classe.sum(), 1),
            "ciblage_max_%": round(100 * defavorise.sum() / classe.sum(), 1),
            "non_couverts": int((defavorise & ~classe).sum()),
        })
    print(pd.DataFrame(lignes).to_string(index=False))


def divergences_par_territoire(df: pd.DataFrame, seuil: float = SEUIL) -> pd.DataFrame:
    """Localise les colleges defavorises non classes.

    Returns:
        Un tableau par departement, trie par nombre de colleges non couverts.
    """
    print(f"\n{'=' * 70}")
    print("OU SONT LES COLLEGES DEFAVORISES NON CLASSES ?")
    print("=" * 70)

    df = df.copy()
    df["defavorise"] = df["rang_social"] < seuil
    df["non_couvert"] = df["defavorise"] & ~df["classe_ep"]

    print("\n--- metropole / outre-mer ---")
    print(df.groupby("zone").agg(
        colleges=("uai", "size"),
        defavorises=("defavorise", "sum"),
        non_couverts=("non_couvert", "sum"),
    ).assign(
        part_defavorises_pct=lambda t: (100 * t.defavorises / t.colleges).round(1),
        couverture_pct=lambda t: (100 * (1 - t.non_couverts / t.defavorises)).round(1),
    ).to_string())

    # Tableau departemental complet.
    dep = df.groupby(["code_departement", "departement"]).agg(
        colleges=("uai", "size"),
        defavorises=("defavorise", "sum"),
        non_couverts=("non_couvert", "sum"),
        ips_median=("ips", "median"),
    ).reset_index()

    # Couverture departementale : part des defavorises du departement qui sont
    # classes. Non definie la ou il n'y a aucun college defavorise.
    dep["couverture_pct"] = (100 * (1 - dep.non_couverts / dep.defavorises)).round(1)

    print("\n--- 12 departements comptant le plus de colleges non couverts ---")
    print(dep.nlargest(12, "non_couverts")[
        ["code_departement", "departement", "defavorises", "non_couverts",
         "couverture_pct", "ips_median"]].to_string(index=False))

    # Departements ou la couverture est la plus faible, parmi ceux qui ont
    # assez de colleges defavorises pour que le taux ait un sens.
    assez = dep[dep["defavorises"] >= 10]
    print("\n--- couverture la plus faible (departements a 10+ defavorises) ---")
    print(assez.nsmallest(10, "couverture_pct")[
        ["code_departement", "departement", "defavorises", "non_couverts",
         "couverture_pct"]].to_string(index=False))

    return dep


def restreindre_au_public(df: pd.DataFrame) -> pd.DataFrame:
    """Restreint l'analyse au secteur public, et justifie cette restriction.

    L'education prioritaire est un dispositif de l'enseignement public : aucun
    college prive sous contrat n'est classe REP ou REP+, y compris parmi les
    plus defavorises. Les inclure dans le calcul de la couverture reviendrait
    a compter comme "non couverts" des colleges qui ne peuvent pas l'etre par
    construction, ce qui degraderait mecaniquement le taux sans rien mesurer.

    On les ecarte donc du calcul, apres avoir affiche le constat qui justifie
    cette decision.
    """
    prive = df[df["secteur"] != "public"]
    print("\n--- justification de la restriction au public ---")
    print(f"  colleges prives sous contrat : {len(prive)}")
    print(f"  dont classes REP ou REP+     : {prive['classe_ep'].sum()}")
    print(f"  dont parmi les {SEUIL:.0%} plus defavorises : "
          f"{(prive['rang_social'] < SEUIL).sum()}")
    print("  -> le prive sous contrat est hors champ du dispositif :")
    print("     il est ecarte du calcul de couverture.")

    return df[df["secteur"] == "public"].copy()


def main() -> None:
    df = charger()
    print(f"{len(df)} colleges charges")

    df = restreindre_au_public(df)

    # Le rang social est recalcule sur le champ restreint : etre parmi les 10%
    # les plus defavorises doit se juger par rapport aux colleges susceptibles
    # d'etre classes, pas par rapport a l'ensemble.
    df["rang_social"] = df["ips"].rank(pct=True)
    print(f"\n{len(df)} colleges publics analyses")

    matrice_ciblage(df)
    sensibilite_au_seuil(df)
    dep = divergences_par_territoire(df)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)

    dep.to_csv(DOSSIER_TABLES / "couverture_par_departement.csv",
               index=False, encoding="utf-8")

    # Liste nominative des colleges defavorises non classes.
    non_couverts = df[(df["rang_social"] < SEUIL) & ~df["classe_ep"]]
    non_couverts.to_csv(DOSSIER_TABLES / "defavorises_non_classes.csv",
                        index=False, encoding="utf-8")

    print(f"\n[+] couverture_par_departement.csv ({len(dep)} departements)")
    print(f"[+] defavorises_non_classes.csv ({len(non_couverts)} colleges)")


if __name__ == "__main__":
    main()
