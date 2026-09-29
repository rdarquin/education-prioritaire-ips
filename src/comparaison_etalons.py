"""Deux etalons pour la meme carte : l'IPS et les resultats au DNB.

LA QUESTION

Tout le projet repose sur un etalon unique : l'IPS. On reconstitue l'ensemble
des n colleges les plus defavorises, n etant le nombre de places d'education
prioritaire, et on le compare a la carte reelle. Un ecart signale un desaccord
entre deux instruments — la carte du ministere et un classement par IPS.

Ce module en introduit un troisieme : la note moyenne a l'ecrit du DNB. Meme
enveloppe, meme mecanique, autre variable. La question devient : les deux
etalons designent-ils les memes colleges ?

Reponse courte, et c'est tout l'interet du module : NON. Ils se recouvrent aux
deux tiers environ. Un tiers des colleges designes par l'un ne l'est pas par
l'autre, et ce tiers a une geographie.

POURQUOI LA NOTE A L'ECRIT ET NON LE TAUX DE REUSSITE

Le choix est detaille dans `preparation.charger_ivac`. En deux mots : le taux
de reussite ne prend que 53 valeurs distinctes sur 5 300 colleges et sature
vers le haut, la note en prend 102 et se repartit sans butee.

POURQUOI PAS LA VALEUR AJOUTEE

L'IVAC publie aussi une valeur ajoutee — l'ecart entre le resultat observe et
le resultat attendu compte tenu du public accueilli. Elle ne peut PAS servir
d'etalon de besoin, et la raison merite d'etre comprise : elle a deja neutralise
la composition sociale, c'est-a-dire precisement ce que l'education prioritaire
cible. Les REP+ y occupent le 76e percentile — ils font MIEUX qu'attendu.
Classer sur la valeur ajoutee la plus faible en ferait les colleges les moins
eligibles, et l'etude conclurait mecaniquement a un ciblage inverse. Ce serait
un artefact de l'indicateur, pas un resultat.

LA RESERVE QUI COMMANDE TOUTE LA LECTURE

L'IPS se mesure sur les PCS declarees par les familles : il est EN AMONT de la
politique. Les resultats au DNB sont EN AVAL — un college en REP+ dispose de
moyens supplementaires, donc sa note porte deja la trace du traitement. Classer
sur un resultat que la politique elle-meme deplace, c'est boucler. Un college
qui ne se distingue plus par ses resultats peut aussi bien n'avoir jamais eu
besoin d'aide qu'avoir ete aide efficacement ; rien ici ne permet de trancher.
Ce module compare deux instruments, il n'evalue pas la politique.

LES EX AEQUO

L'ensemble optimal est defini par le RANG, comme dans `score_ecart.py`. L'IPS
s'y prete : 746 valeurs distinctes, 11 colleges seulement a la valeur du seuil.
La note du DNB beaucoup moins : 102 valeurs distinctes, et plusieurs dizaines
de colleges exactement a la valeur qui ferme l'enveloppe. Leur presence parmi
les dernieres places tient a l'ordre de tri, pas a la donnee.

On ne les departage pas par l'IPS : ce serait contaminer un etalon par l'autre
et vider la comparaison de son sens. Ils sont marques `frontiere` dans le
fichier de sortie, comptes dans les tableaux, et toute conclusion qui les
concerne est indeterminee. Le tri prealable par UAI rend au moins ce choix
arbitraire REPRODUCTIBLE : deux executions donnent le meme resultat.

Prerequis : `uv run python -m src.preparation`

Lancement (depuis la racine du projet) :
    uv run python -m src.comparaison_etalons
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm

from src.cartographie import annoter_drom, charger_contours
from src.config import DATA_PROCESSED, FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE = "#1f3b73", "#eb6834"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
GRIS_ABSENT = "#e3e3e3"

# Effectif minimal de colleges publics pour qu'une part departementale ait un
# sens, repris de `cartographie_score.py` : en dessous, un seul college
# deplacerait la part de plusieurs points.
MIN_ETABLISSEMENTS = 20

N_CLASSES = 6

# Les quatre verdicts croises. L'ordre est celui des tableaux et de la legende,
# et il va du plus consensuel au plus discutable.
GROUPES = {
    "accord : à classer": {
        "couleur": "#8c3a17",
        "definition": "désigné par les deux étalons"},
    "IPS seul": {
        "couleur": BLEU,
        "definition": "IPS parmi les plus bas, résultats au-dessus du seuil"},
    "note seule": {
        "couleur": ORANGE,
        "definition": "résultats parmi les plus bas, IPS au-dessus du seuil"},
    "accord : hors": {
        "couleur": "#c9c8c1",
        "definition": "désigné par aucun des deux"},
}


def charger() -> pd.DataFrame:
    """Lit le fichier d'analyse et restreint la comparaison a son champ commun.

    Deux restrictions, et chacune retire quelque chose :

      - COLLEGES PUBLICS uniquement. Le prive sous contrat n'est pas eligible a
        l'education prioritaire : l'y inclure ajouterait 1 649 colleges qu'aucun
        etalon ne peut designer, et diluerait tous les pourcentages.

      - COLLEGES AYANT LES DEUX MESURES. Comparer deux etalons sur deux
        populations differentes n'aurait aucun sens : un college absent d'un
        classement y serait compte comme "non designe", ce qui est faux — il
        n'est pas mesure.
    """
    fichier = DATA_PROCESSED / "colleges_2024_2025.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.preparation")

    df = pd.read_csv(fichier, dtype={"code_departement": str,
                                     "code_commune": str})
    public = df[df["secteur"] == "public"]
    complet = public.dropna(subset=["ips", "note_ecrit_dnb"])

    perdus = len(public) - len(complet)
    perdus_ep = int((public.loc[~public.index.isin(complet.index), "ep"]
                     != "hors EP").sum())
    print(f"  colleges publics {len(public)}")
    print(f"  sans resultat au DNB : {perdus}, dont {perdus_ep} classes EP")
    print(f"  champ de la comparaison : {len(complet)} colleges")

    # Le tri par UAI fixe l'ordre d'arrivee des ex aequo. Sans lui, `nsmallest`
    # departagerait selon l'ordre du fichier, qui n'est garanti par rien.
    return complet.sort_values("uai").reset_index(drop=True)


def designer(df: pd.DataFrame, etalon: str, n: int) -> tuple[pd.Series, float, int]:
    """Reconstitue l'ensemble optimal sous un etalon, a enveloppe donnee.

    Args:
        df: le champ de la comparaison.
        etalon: nom de la colonne servant de classement (valeur basse = designe).
        n: nombre de places a pourvoir.

    Returns:
        Un triplet (appartenance booleenne, valeur du seuil, nombre d'ex aequo
        a cette valeur).
    """
    retenus = df.nsmallest(n, etalon)
    seuil = retenus[etalon].max()
    exaequo = int((df[etalon] == seuil).sum())
    return df["uai"].isin(retenus["uai"]), float(seuil), exaequo


def croiser(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Croise les deux etalons et attribue son verdict a chaque college.

    Returns:
        La table augmentee, et un dictionnaire des parametres du calcul
        (enveloppe, seuils, ex aequo) a reutiliser dans les notes de figure.
    """
    # L'enveloppe est le nombre de classes DANS LE CHAMP, et non les 1 094
    # places nationales : quelques colleges classes n'ont pas de resultat au
    # DNB et sortent de la comparaison. Garder 1 094 ferait designer par chaque
    # etalon plus de colleges qu'il n'y a de places reellement observees.
    n = int((df["ep"] != "hors EP").sum())

    df = df.copy()
    df["designe_ips"], seuil_ips, exaequo_ips = designer(df, "ips", n)
    df["designe_note"], seuil_note, exaequo_note = designer(
        df, "note_ecrit_dnb", n)

    # Un college est "a la frontiere" quand sa valeur egale exactement celle
    # qui ferme l'enveloppe : son sort tient alors au tri, pas a la donnee.
    df["frontiere_ips"] = df["ips"] == seuil_ips
    df["frontiere_note"] = df["note_ecrit_dnb"] == seuil_note

    df["verdict"] = np.select(
        [df["designe_ips"] & df["designe_note"],
         df["designe_ips"] & ~df["designe_note"],
         ~df["designe_ips"] & df["designe_note"]],
        ["accord : à classer", "IPS seul", "note seule"],
        default="accord : hors")

    df["classe_ep"] = df["ep"] != "hors EP"

    params = {"n": n, "seuil_ips": seuil_ips, "seuil_note": seuil_note,
              "exaequo_ips": exaequo_ips, "exaequo_note": exaequo_note,
              "communs": int((df["designe_ips"] & df["designe_note"]).sum())}
    return df, params


def resumer(df: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Tableau des quatre verdicts : effectif, classement reel, profil moyen."""
    table = df.groupby("verdict").agg(
        colleges=("uai", "size"),
        classes_ep=("classe_ep", "sum"),
        ips_moyen=("ips", "mean"),
        note_moyenne=("note_ecrit_dnb", "mean"),
        frontiere=("frontiere_note", "sum"),
    )
    table["part_classes"] = 100 * table["classes_ep"] / table["colleges"]
    table["part_colleges"] = 100 * table["colleges"] / len(df)
    return table.reindex(GROUPES.keys())


def agreger(df: pd.DataFrame) -> pd.DataFrame:
    """Part de chaque type de desaccord, par departement."""
    dep = df.groupby(["code_departement", "departement"]).agg(
        colleges=("uai", "size"),
        classes=("classe_ep", "sum"),
        ips_seul=("verdict", lambda s: (s == "IPS seul").sum()),
        note_seule=("verdict", lambda s: (s == "note seule").sum()),
        accord_classer=("verdict", lambda s: (s == "accord : à classer").sum()),
    ).reset_index()

    dep["part_ips_seul"] = 100 * dep["ips_seul"] / dep["colleges"]
    dep["part_note_seule"] = 100 * dep["note_seule"] / dep["colleges"]

    # Parmi les seuls colleges qu'au moins un etalon designe, quelle part fait
    # l'objet d'un desaccord ? C'est la mesure la plus directe de la divergence,
    # debarrassee de la masse des colleges que les deux ignorent.
    designes = dep["ips_seul"] + dep["note_seule"] + dep["accord_classer"]
    dep["part_desaccord"] = 100 * (dep["ips_seul"] + dep["note_seule"]) / \
        designes.replace(0, np.nan)
    return dep


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

def figure_nuage(df: pd.DataFrame, table: pd.DataFrame, params: dict) -> None:
    """Nuage IPS x note du DNB, quadrants, et tableau des quatre verdicts."""
    fig = plt.figure(figsize=(11, 11.0))
    grille = fig.add_gridspec(2, 1, height_ratios=[3.1, 0.82],
                              left=0.075, right=0.975, top=0.858, bottom=0.205,
                              hspace=0.15)
    ax = fig.add_subplot(grille[0])
    axt = fig.add_subplot(grille[1])

    # L'ordre de trace compte : les groupes nombreux d'abord, sans quoi ils
    # recouvriraient les minoritaires, qui sont justement le sujet.
    for nom in ["accord : hors", "accord : à classer", "IPS seul", "note seule"]:
        sous = df[df["verdict"] == nom]
        ax.scatter(sous["ips"], sous["note_ecrit_dnb"], s=5,
                   c=GROUPES[nom]["couleur"], alpha=0.55, linewidths=0,
                   label=f"{nom} ({len(sous)})")

    ax.axvline(params["seuil_ips"], color=ENCRE, linewidth=1.1, zorder=5)
    ax.axhline(params["seuil_note"], color=ENCRE, linewidth=1.1, zorder=5)

    seuil_ips_txt = f"{params['seuil_ips']:.2f}".replace(".", ",")
    seuil_note_txt = f"{params['seuil_note']:.1f}".replace(".", ",")
    ax.annotate(f"seuil IPS {seuil_ips_txt}",
                xy=(params["seuil_ips"], ax.get_ylim()[1]), xytext=(4, -10),
                textcoords="offset points", fontsize=8, color=ENCRE, va="top")
    ax.annotate(f"seuil note {seuil_note_txt}",
                xy=(ax.get_xlim()[1], params["seuil_note"]), xytext=(-4, 4),
                textcoords="offset points", fontsize=8, color=ENCRE,
                ha="right")

    ax.set_xlabel("Indice de position sociale (IPS)", fontsize=9.5)
    ax.set_ylabel("Note moyenne à l'écrit du DNB (sur 20)", fontsize=9.5)
    ax.grid(color=GRILLE, linewidth=0.6)
    ax.set_axisbelow(True)
    for cote in ("top", "right"):
        ax.spines[cote].set_visible(False)
    legende = ax.legend(loc="lower right", fontsize=8.5, frameon=True,
                        framealpha=0.95, edgecolor=GRILLE, markerscale=2.6)
    legende.get_frame().set_linewidth(0.6)

    # ---- tableau ----------------------------------------------------------
    axt.set_axis_off()
    entetes = ["", "collèges", "% du champ", "classés EP", "% classés",
               "IPS moyen", "note moyenne"]
    lignes = []
    for nom in GROUPES:
        ligne = table.loc[nom]
        lignes.append([
            nom,
            f"{int(ligne['colleges'])}",
            f"{ligne['part_colleges']:.1f} %".replace(".", ","),
            f"{int(ligne['classes_ep'])}",
            f"{ligne['part_classes']:.1f} %".replace(".", ","),
            f"{ligne['ips_moyen']:.1f}".replace(".", ","),
            f"{ligne['note_moyenne']:.1f}".replace(".", ","),
        ])

    tab = axt.table(cellText=lignes, colLabels=entetes, loc="upper center",
                    cellLoc="right", colLoc="right")
    tab.auto_set_font_size(False)
    tab.set_fontsize(9)
    tab.scale(1, 1.75)

    for (ligne, colonne), cellule in tab.get_celld().items():
        cellule.set_edgecolor("white")
        cellule.set_linewidth(1.2)
        if ligne == 0:
            cellule.set_facecolor(GRILLE)
            cellule.set_text_props(color=ENCRE, fontweight="bold")
        else:
            cellule.set_facecolor("#f7f6f2" if ligne % 2 else "white")
        if colonne == 0:
            cellule.set_text_props(ha="left")
            cellule.PAD = 0.04
            if ligne > 0:
                # Pastille de couleur : la ligne du tableau et le nuage
                # doivent se lire l'un par l'autre sans effort.
                cellule.set_text_props(
                    color=GROUPES[list(GROUPES)[ligne - 1]]["couleur"],
                    fontweight="bold")

    fig.suptitle("Deux étalons désignent-ils les mêmes collèges ?\n"
                 "IPS et résultats au DNB, à enveloppe identique",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.978)

    n_txt = f"{params['n']:,}".replace(",", " ")
    part_communs = 100 * params["communs"] / params["n"]
    part_txt = f"{part_communs:.1f}".replace(".", ",")
    fig.text(0.02, 0.918,
             f"Chaque étalon désigne les {n_txt} collèges publics les plus bas de "
             f"son classement — le nombre exact de places d'éducation prioritaire "
             f"observées dans le champ.\n"
             f"Les deux ensembles ont donc la même taille et sont directement "
             f"comparables. Ils partagent {params['communs']} collèges, "
             f"soit {part_txt} % : un tiers des désignations change avec l'étalon.",
             fontsize=9, va="top", color=ENCRE_2)

    exa_ips = params["exaequo_ips"]
    exa_note = params["exaequo_note"]
    fig.text(0.02, 0.163,
             "Lecture : en bas à gauche, les collèges que les deux étalons "
             "désignent ; en haut à droite, ceux qu'aucun ne désigne. Les deux "
             "autres quadrants sont les désaccords.\n"
             "En haut à gauche, des collèges socialement défavorisés dont les "
             "résultats tiennent ; en bas à droite, des résultats faibles sans "
             "désavantage social apparent.\n"
             f"Ex æquo à la valeur du seuil : {exa_ips} sur l'IPS, {exa_note} sur "
             "la note. Pour ces derniers, l'appartenance aux dernières places "
             "tient à l'ordre de tri et non à la donnée ;\n"
             "ils ne sont pas départagés par l'autre étalon, ce qui reviendrait à "
             "le contaminer.\n"
             "Réserve décisive : l'IPS se mesure en amont de la politique, les "
             "résultats au DNB en aval. Un collège en REP+ dispose de moyens "
             "supplémentaires, sa note en porte la trace.\n"
             "Ce graphe compare deux instruments de ciblage ; il n'évalue pas "
             "l'efficacité du dispositif.\n"
             "Champ : collèges publics ayant un IPS et un résultat au DNB, "
             "rentrée 2024-2025 / session 2025. Sources : DEPP (IPS, IVAC), "
             "annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "comparaison_etalons.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def figure_cartes(dep: pd.DataFrame, contours) -> None:
    """Les deux desaccords, cartographies cote a cote."""
    gdf = contours.join(dep.set_index("code_departement"), how="left")
    fiable = gdf["colleges"].fillna(0) >= MIN_ETABLISSEMENTS
    n_masques = int((~fiable).sum())

    fig, axes = plt.subplots(1, 2, figsize=(13, 8.8))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.855, bottom=0.235,
                        wspace=0.02)

    cartes = [
        ("part_ips_seul", "Blues",
         "Désignés par l'IPS seul",
         "Part des collèges publics du département (%)"),
        ("part_note_seule", "Oranges",
         "Désignés par les résultats seuls",
         "Part des collèges publics du département (%)"),
    ]

    for ax, (colonne, palette, titre, etiquette), position in zip(
            axes, cartes, ([0.07, 0.185, 0.36, 0.014],
                           [0.57, 0.185, 0.36, 0.014])):
        valeurs = gdf.loc[fiable, colonne].to_numpy()
        bornes = np.unique(np.round(
            np.quantile(valeurs, np.linspace(0, 1, N_CLASSES + 1)), 2))
        cmap = matplotlib.colormaps[palette].resampled(len(bornes) - 1)
        norme = BoundaryNorm(bornes, ncolors=len(bornes) - 1)

        gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.4)
        gdf[fiable].plot(ax=ax, column=colonne, cmap=cmap, norm=norme,
                         edgecolor="white", linewidth=0.4)
        annoter_drom(ax, contours)
        ax.set_axis_off()
        ax.set_title(titre, fontsize=11.5, fontweight="bold", loc="left")

        echelle = plt.cm.ScalarMappable(cmap=cmap, norm=norme)
        cax = fig.add_axes(position)
        fig.colorbar(echelle, cax=cax, orientation="horizontal",
                     ticks=bornes, spacing="uniform")
        cax.set_xticklabels([f"{b:.1f}".replace(".", ",") for b in bornes],
                            fontsize=6.5)
        cax.set_xlabel(etiquette, fontsize=8, labelpad=4)

    fig.suptitle("Où les deux étalons se contredisent-ils ?\n"
                 "Collèges publics, rentrée 2024-2025",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)

    fig.text(0.02, 0.128,
             "À gauche : les collèges que l'IPS désigne et que les résultats au "
             "DNB ne désignent pas — socialement défavorisés, mais dont les "
             "résultats tiennent.\n"
             "À droite : l'inverse — des résultats parmi les plus faibles du pays "
             "sans que l'IPS place l'établissement sous le seuil.\n"
             "Les deux ensembles ont exactement la même taille au niveau "
             "national : ce que l'un des étalons désigne en plus quelque part, il "
             "le désigne en moins ailleurs.\n"
             "Les classes sont des quantiles de la distribution départementale : "
             "quelques départements extrêmes écraseraient sinon tous les autres.\n"
             f"En gris : {n_masques} départements comptant moins de "
             f"{MIN_ETABLISSEMENTS} collèges publics du champ, ou sans donnée.\n"
             "L'IPS se mesure en amont de la politique, les résultats en aval : "
             "un désaccord ne dit pas lequel des deux étalons a raison.\n"
             "Sources : DEPP (IPS, IVAC), annuaire de l'éducation, contours "
             "Insee/cartiflette. DROM rapprochés, échelles et distances non "
             "respectées.",
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / "desaccord_etalons.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    print(f"\n{'=' * 72}")
    print("DEUX ETALONS : IPS ET RESULTATS AU DNB")
    print("=" * 72 + "\n")

    print("Champ :")
    df = charger()

    df, params = croiser(df)

    seuil_ips = f"{params['seuil_ips']:.2f}".replace(".", ",")
    seuil_note = f"{params['seuil_note']:.1f}".replace(".", ",")
    print(f"\n  enveloppe observee : {params['n']} places")
    print(f"  seuil IPS  : {seuil_ips} ({params['exaequo_ips']} ex aequo)")
    print(f"  seuil note : {seuil_note} ({params['exaequo_note']} ex aequo)")
    print(f"  colleges designes par les deux : {params['communs']} "
          f"({100 * params['communs'] / params['n']:.1f} %)")

    table = resumer(df, params)
    print("\nLes quatre verdicts :")
    colonnes = ["colleges", "part_colleges", "classes_ep", "part_classes",
                "ips_moyen", "note_moyenne"]
    print(table[colonnes].round(1).to_string())

    print("\nFigures :")
    figure_nuage(df, table, params)

    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    dep = agreger(df)
    figure_cartes(dep, contours)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    sortie = ["uai", "nom", "ep", "ips", "note_ecrit_dnb", "nb_candidats_dnb",
              "designe_ips", "designe_note", "frontiere_ips", "frontiere_note",
              "verdict", "code_departement", "departement", "code_academie",
              "academie"]
    df[sortie].to_csv(DOSSIER_TABLES / "comparaison_etalons.csv",
                      index=False, encoding="utf-8")
    dep.round(2).to_csv(DOSSIER_TABLES / "comparaison_etalons_par_departement.csv",
                        index=False, encoding="utf-8")

    assez = dep[dep["colleges"] >= MIN_ETABLISSEMENTS]
    vue = ["departement", "colleges", "ips_seul", "part_ips_seul",
           "note_seule", "part_note_seule"]
    print("\n  desaccord le plus marque en faveur de l'IPS :")
    print(assez.nlargest(6, "part_ips_seul")[vue].round(1).to_string(index=False))
    print("\n  desaccord le plus marque en faveur des resultats :")
    print(assez.nlargest(6, "part_note_seule")[vue].round(1).to_string(index=False))

    print(f"\n[+] comparaison_etalons.csv ({len(df)} lignes)")
    print(f"[+] comparaison_etalons_par_departement.csv ({len(dep)} lignes)")


if __name__ == "__main__":
    main()
