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

DEUX VARIANTES, ET LA SECONDE N'EST PAS UN RAFFINEMENT

Comme `score_ecart.py`, ce module calcule deux variantes cote a cote : un
classement NATIONAL, et un classement ACADEMIQUE ou chaque academie designe
ses propres colleges les plus bas, sur sa propre enveloppe.

Ici la variante academique repond en plus a une objection precise, et c'est la
raison principale de son existence. Le brevet est corrige par les enseignants,
dans des commissions d'harmonisation ACADEMIQUES. Rien ne garantit qu'un 10 a
Creteil soit un 10 a Rennes — et la mesure montre que non : l'ecart moyen entre
la note observee et celle que l'IPS laisse attendre va de -2,55 point en Guyane
a +2,16 a Mayotte, soit une etendue de 4,71 points, plus de TROIS FOIS
l'ecart-type inter-etablissement (1,39). Recentrer chaque academie sur sa propre
norme ferait changer de statut 208 colleges sur 1 088.

Un classement national de la note melange donc deux choses qu'on ne peut pas
separer : la situation scolaire reelle, et la severite locale de la correction.
La variante academique fait disparaitre le probleme par construction, puisqu'un
college n'y est jamais compare qu'a des colleges corriges par la meme
commission.

LA NOTE EST UN ETALON NETTEMENT MOINS FIABLE QUE L'IPS

Trois mesures, a garder en tete avant d'interpreter quoi que ce soit :

  - STABILITE. D'une session a l'autre, la note d'un college correle a +0,848
    avec elle-meme (72 % de variance partagee), contre +0,993 pour l'IPS
    (99 %). Traduit en designations : 24,7 % de l'ensemble designe par la note
    change selon l'annee retenue, contre 6,0 % pour l'IPS. Le taux de reussite,
    lui, ne correle qu'a +0,657 — d'ou son rejet.

  - BRUIT D'ECHANTILLONNAGE. La note est une moyenne sur environ 108 candidats.
    Avec un ecart-type individuel de l'ordre de 3,5 points, l'erreur-type de
    cette moyenne vaut 0,34 point, soit 24 % de l'ecart-type
    inter-etablissement — et 35 % pour un college du premier decile d'effectif.

  - MAIS LE DESACCORD N'EST PAS DU BRUIT. Lisser la note sur quatre sessions,
    ce qui divise le bruit, ne fait passer le recouvrement avec l'IPS que de
    66,0 % a 71,7 %. Il plafonne. Environ un sixieme du desaccord est
    accidentel ; les cinq sixiemes sont structurels.

Une crainte s'est en revanche revelee infondee : l'exclusion de la serie
professionnelle (SEGPA) ne biaise pas la note. Correlation entre la note en
serie generale et la part de presents en SEGPA : -0,031.

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

# Les deux variantes, dans l'ordre d'affichage. La valeur est la liste des
# colonnes de regroupement : vide pour un classement national, l'academie pour
# un classement recalcule academie par academie.
VARIANTES = {
    "national": [],
    "académique": ["code_academie"],
}

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


def designer(df: pd.DataFrame, etalon: str,
             groupes: list[str]) -> tuple[pd.Series, dict]:
    """Reconstitue l'ensemble optimal sous un etalon, a enveloppe observee.

    Sans `groupes`, l'enveloppe est nationale : on retient les n colleges les
    plus bas du pays, n etant le nombre de classes. Avec `groupes`, le calcul
    est refait A L'INTERIEUR de chaque groupe, sur l'enveloppe de ce groupe.
    Un college n'y est donc jamais compare qu'a ses voisins de groupe.

    L'ensemble est defini par le RANG et non par une inegalite sur le seuil.
    C'est ce qui garantit que les deux etalons designent exactement le meme
    NOMBRE de colleges, condition sans laquelle les recouvrements ne seraient
    pas comparables.

    Args:
        df: le champ de la comparaison, trie par UAI.
        etalon: colonne servant de classement (valeur basse = designe).
        groupes: colonnes de regroupement, vide pour un classement national.

    Returns:
        L'appartenance booleenne, et un dictionnaire {seuils, exaequo} ou les
        seuils sont la liste des valeurs qui ferment chaque enveloppe.
    """
    parts = df.groupby(groupes, sort=False) if groupes else [(None, df)]
    retenus, seuils, exaequo = set(), [], 0

    for _, part in (parts if groupes else parts):
        n = int(part["classe_ep"].sum())
        if not n:
            continue
        choisis = part.nsmallest(n, etalon)
        seuil = float(choisis[etalon].max())
        retenus |= set(choisis["uai"])
        seuils.append(seuil)
        # Ex aequo a la valeur qui ferme CETTE enveloppe : leur presence parmi
        # les dernieres places tient a l'ordre de tri, pas a la donnee.
        exaequo += int((part[etalon] == seuil).sum())

    return df["uai"].isin(retenus), {"seuils": seuils, "exaequo": exaequo}


def croiser(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Croise les deux etalons, dans chacune des deux variantes.

    Returns:
        La table augmentee de deux colonnes `verdict_*`, et un dictionnaire
        des parametres de chaque variante, a reutiliser dans les notes.
    """
    df = df.copy()
    df["classe_ep"] = df["ep"] != "hors EP"

    # L'enveloppe est le nombre de classes DANS LE CHAMP, et non les 1 094
    # places nationales : quelques colleges classes n'ont pas de resultat au
    # DNB et sortent de la comparaison. Garder 1 094 ferait designer par chaque
    # etalon plus de colleges qu'il n'y a de places reellement observees.
    n = int(df["classe_ep"].sum())
    params = {}

    for variante, groupes in VARIANTES.items():
        suffixe = "" if variante == "national" else "_academie"

        ips, info_ips = designer(df, "ips", groupes)
        note, info_note = designer(df, "note_ecrit_dnb", groupes)
        df[f"designe_ips{suffixe}"] = ips
        df[f"designe_note{suffixe}"] = note

        df[f"verdict{suffixe}"] = np.select(
            [ips & note, ips & ~note, ~ips & note],
            ["accord : à classer", "IPS seul", "note seule"],
            default="accord : hors")

        params[variante] = {
            "suffixe": suffixe,
            "n": n,
            "designes": int(ips.sum()),
            "communs": int((ips & note).sum()),
            "seuils_ips": info_ips["seuils"],
            "seuils_note": info_note["seuils"],
            "exaequo_ips": info_ips["exaequo"],
            "exaequo_note": info_note["exaequo"],
        }

    # Marquage des ex aequo de la variante nationale, ou le seuil est unique :
    # c'est la seule variante ou une colonne booleenne a un sens simple.
    df["frontiere_ips"] = df["ips"] == params["national"]["seuils_ips"][0]
    df["frontiere_note"] = (df["note_ecrit_dnb"]
                            == params["national"]["seuils_note"][0])

    # Combien de colleges changent de verdict en passant d'une variante a
    # l'autre ? C'est la mesure de ce que le recentrage academique deplace.
    params["bascules"] = int((df["verdict"] != df["verdict_academie"]).sum())
    return df, params


def resumer(df: pd.DataFrame, suffixe: str) -> pd.DataFrame:
    """Tableau des quatre verdicts d'une variante : effectif, classement, profil."""
    colonne = f"verdict{suffixe}"
    table = df.groupby(colonne).agg(
        colleges=("uai", "size"),
        classes_ep=("classe_ep", "sum"),
        ips_moyen=("ips", "mean"),
        note_moyenne=("note_ecrit_dnb", "mean"),
    )
    table["part_classes"] = 100 * table["classes_ep"] / table["colleges"]
    table["part_colleges"] = 100 * table["colleges"] / len(df)
    return table.reindex(GROUPES.keys())


def agreger(df: pd.DataFrame, suffixe: str) -> pd.DataFrame:
    """Part de chaque type de desaccord, par departement, pour une variante.

    Un departement releve d'une seule academie : agreger des verdicts calcules
    a l'echelle academique au niveau departemental reste donc coherent, chaque
    departement heritant de la norme d'une academie unique.
    """
    colonne = f"verdict{suffixe}"
    dep = df.groupby(["code_departement", "departement"]).agg(
        colleges=("uai", "size"),
        classes=("classe_ep", "sum"),
        ips_seul=(colonne, lambda s: (s == "IPS seul").sum()),
        note_seule=(colonne, lambda s: (s == "note seule").sum()),
        accord_classer=(colonne, lambda s: (s == "accord : à classer").sum()),
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

def figure_nuage(df: pd.DataFrame, tables: dict, params: dict) -> None:
    """Nuage IPS x note du DNB, quadrants, et tableau des deux variantes.

    Le nuage porte les seuils NATIONAUX, les seuls qu'on puisse tracer comme
    deux droites. La variante academique en compte trente de chaque cote : elle
    se lit dans le second bloc du tableau, pas sur le nuage.
    """
    national = params["national"]

    fig = plt.figure(figsize=(11, 12.2))
    grille = fig.add_gridspec(2, 1, height_ratios=[2.7, 1.25],
                              left=0.075, right=0.975, top=0.872, bottom=0.185,
                              hspace=0.14)
    ax = fig.add_subplot(grille[0])
    axt = fig.add_subplot(grille[1])

    # L'ordre de trace compte : les groupes nombreux d'abord, sans quoi ils
    # recouvriraient les minoritaires, qui sont justement le sujet.
    for nom in ["accord : hors", "accord : à classer", "IPS seul", "note seule"]:
        sous = df[df["verdict"] == nom]
        ax.scatter(sous["ips"], sous["note_ecrit_dnb"], s=5,
                   c=GROUPES[nom]["couleur"], alpha=0.55, linewidths=0,
                   label=f"{nom} ({len(sous)})")

    seuil_ips = national["seuils_ips"][0]
    seuil_note = national["seuils_note"][0]
    ax.axvline(seuil_ips, color=ENCRE, linewidth=1.1, zorder=5)
    ax.axhline(seuil_note, color=ENCRE, linewidth=1.1, zorder=5)

    seuil_ips_txt = f"{seuil_ips:.2f}".replace(".", ",")
    seuil_note_txt = f"{seuil_note:.1f}".replace(".", ",")
    ax.annotate(f"seuil IPS {seuil_ips_txt}",
                xy=(seuil_ips, ax.get_ylim()[1]), xytext=(4, -10),
                textcoords="offset points", fontsize=8, color=ENCRE, va="top")
    ax.annotate(f"seuil note {seuil_note_txt}",
                xy=(ax.get_xlim()[1], seuil_note), xytext=(-4, 4),
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

    # ---- tableau : les deux variantes, l'une sous l'autre -----------------
    axt.set_axis_off()
    entetes = ["étalon", "", "collèges", "% du champ", "classés EP",
               "% classés", "IPS moyen", "note moyenne"]
    lignes, couleurs_libelle = [], []
    for variante in VARIANTES:
        table = tables[variante]
        for rang, nom in enumerate(GROUPES):
            ligne = table.loc[nom]
            lignes.append([
                variante if rang == 0 else "",
                nom,
                f"{int(ligne['colleges'])}",
                f"{ligne['part_colleges']:.1f} %".replace(".", ","),
                f"{int(ligne['classes_ep'])}",
                f"{ligne['part_classes']:.1f} %".replace(".", ","),
                f"{ligne['ips_moyen']:.1f}".replace(".", ","),
                f"{ligne['note_moyenne']:.1f}".replace(".", ","),
            ])
            couleurs_libelle.append(GROUPES[nom]["couleur"])

    # Largeurs explicites : laissees a matplotlib, elles sont uniformes et la
    # colonne des verdicts tronque son libelle le plus long.
    tab = axt.table(cellText=lignes, colLabels=entetes, loc="upper center",
                    cellLoc="right", colLoc="right",
                    colWidths=[0.12, 0.20, 0.10, 0.12, 0.12, 0.11, 0.11, 0.12])
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.5)
    tab.scale(1, 1.5)

    bloc = len(GROUPES)
    for (ligne, colonne), cellule in tab.get_celld().items():
        cellule.set_edgecolor("white")
        cellule.set_linewidth(1.2)
        if ligne == 0:
            cellule.set_facecolor(GRILLE)
            cellule.set_text_props(color=ENCRE, fontweight="bold")
        else:
            # Un fond distinct par variante, plutot qu'une alternance : c'est
            # la separation des deux blocs qui doit sauter aux yeux.
            cellule.set_facecolor("white" if ligne <= bloc else "#f5f3ee")
        if colonne == 0:
            cellule.set_text_props(ha="left", color=ENCRE_2,
                                   fontweight="bold")
        if colonne == 1 and ligne > 0:
            # Le libelle reprend la couleur du nuage : la ligne du tableau et
            # le graphe doivent se lire l'un par l'autre sans effort.
            cellule.set_text_props(ha="left",
                                   color=couleurs_libelle[ligne - 1],
                                   fontweight="bold")

    fig.suptitle("Deux étalons désignent-ils les mêmes collèges ?\n"
                 "IPS et résultats au DNB, à enveloppe identique",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.980)

    academique = params["académique"]
    n_txt = f"{national['n']:,}".replace(",", " ")
    part_nat = f"{100 * national['communs'] / national['n']:.1f}".replace(".", ",")
    part_aca = f"{100 * academique['communs'] / academique['n']:.1f}".replace(
        ".", ",")
    fig.text(0.02, 0.930,
             f"Chaque étalon désigne les {n_txt} collèges publics les plus bas de "
             f"son classement — le nombre exact de places d'éducation prioritaire "
             f"observées dans le champ.\n"
             f"Les deux ensembles ont donc la même taille et sont directement "
             f"comparables. Ils ne partagent que {national['communs']} collèges, "
             f"soit {part_nat} % :\n"
             f"un tiers des désignations change avec l'étalon. Recalculé académie "
             f"par académie, le recouvrement monte à {part_aca} % — et c'est cette "
             f"variante qu'il faut lire,\n"
             f"pour la raison exposée sous le tableau.",
             fontsize=9, va="top", color=ENCRE_2)

    exa_ips = national["exaequo_ips"]
    exa_note = national["exaequo_note"]
    fig.text(0.02, 0.157,
             "Lecture : en bas à gauche, les collèges que les deux étalons "
             "désignent ; en haut à droite, ceux qu'aucun ne désigne. Les deux "
             "autres quadrants sont les désaccords.\n"
             "En haut à gauche, des collèges socialement défavorisés dont les "
             "résultats tiennent ; en bas à droite, des résultats faibles sans "
             "désavantage social apparent.\n"
             "Les deux droites sont les seuils NATIONAUX, les seuls qu'on puisse "
             "tracer. La variante académique en compte trente de chaque côté : "
             "elle se lit dans le tableau, pas sur le nuage.\n"
             "Pourquoi elle compte : le brevet est corrigé dans des commissions "
             "académiques, et l'écart entre la note observée et celle que l'IPS "
             "laisse attendre va de −2,6 point en Guyane\n"
             "à +2,2 à Mayotte — plus de trois fois l'écart-type entre "
             "établissements. Un classement national de la note mélange donc la "
             "situation scolaire et la sévérité locale de la correction.\n"
             f"Ex æquo à la valeur du seuil national : {exa_ips} sur l'IPS, "
             f"{exa_note} sur la note. Pour ces derniers, l'appartenance aux "
             "dernières places tient à l'ordre de tri et non à la donnée ; ils ne "
             "sont pas\n"
             "départagés par l'autre étalon, ce qui reviendrait à le contaminer.\n"
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


def figure_cartes(dep: pd.DataFrame, contours, params: dict) -> None:
    """Les deux desaccords, cartographies cote a cote, en variante academique.

    La variante NATIONALE ne serait pas cartographiable honnetement. Les deux
    departements extremes y etaient Mayotte (59,1 % designes par l'IPS seul) et
    la Guadeloupe (54,8 % par la note seule) — c'est-a-dire exactement les deux
    academies dont la note s'ecarte le plus de ce que leur IPS laisse attendre.
    La carte aurait donc affiche un regime de correction en le faisant passer
    pour une difference de situation scolaire.

    En variante academique, chaque college n'est compare qu'a des colleges
    corriges par la meme commission : ce qui reste est un desaccord entre les
    deux etalons a l'interieur d'un meme bareme.
    """
    gdf = contours.join(dep.set_index("code_departement"), how="left")
    fiable = gdf["colleges"].fillna(0) >= MIN_ETABLISSEMENTS
    n_masques = int((~fiable).sum())

    fig, axes = plt.subplots(1, 2, figsize=(13, 9.7))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.868, bottom=0.285,
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
            axes, cartes, ([0.07, 0.232, 0.36, 0.013],
                           [0.57, 0.232, 0.36, 0.013])):
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

    academique = params["académique"]
    part_aca = f"{100 * academique['communs'] / academique['n']:.1f}".replace(
        ".", ",")

    fig.suptitle("Où les deux étalons se contredisent-ils ?\n"
                 "Classement recalculé à l'intérieur de chaque académie — "
                 "collèges publics, rentrée 2024-2025",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)

    fig.text(0.02, 0.183,
             "À gauche : les collèges que l'IPS désigne et que les résultats au "
             "DNB ne désignent pas — socialement défavorisés, mais dont les "
             "résultats tiennent. À droite, l'inverse.\n"
             "Chaque académie désigne ici ses propres collèges les plus bas, sur "
             "sa propre enveloppe : un collège n'est jamais comparé qu'à des "
             "collèges de son académie. C'est indispensable,\n"
             "parce que le brevet est corrigé dans des commissions académiques : "
             "un classement national de la note mélangerait la situation scolaire "
             "et la sévérité locale de la correction, et ses\n"
             "deux départements extrêmes étaient Mayotte et la Guadeloupe — "
             "précisément les deux académies les plus atypiques sur ce point. À "
             f"l'échelle académique, ce biais disparaît par\n"
             f"construction, et le recouvrement entre les deux étalons monte de "
             f"66,0 % à {part_aca} %.\n"
             "Les classes sont des quantiles de la distribution départementale : "
             "quelques départements extrêmes écraseraient sinon tous les autres. "
             f"En gris, {n_masques} départements comptant moins de\n"
             f"{MIN_ETABLISSEMENTS} collèges publics du champ, ou sans donnée.\n"
             "L'IPS se mesure en amont de la politique, les résultats en aval : un "
             "désaccord ne dit pas lequel des deux étalons a raison. La note est "
             "aussi la moins stable des deux — un quart de\n"
             "l'ensemble qu'elle désigne change selon la session retenue, contre "
             "6 % pour l'IPS. Sources : DEPP (IPS, IVAC), annuaire de l'éducation, "
             "contours Insee/cartiflette.\n"
             "DROM rapprochés, échelles et distances non respectées.",
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

    colonnes = ["colleges", "part_colleges", "classes_ep", "part_classes",
                "ips_moyen", "note_moyenne"]
    tables = {}
    for variante, info in ((v, params[v]) for v in VARIANTES):
        seuils_ips, seuils_note = info["seuils_ips"], info["seuils_note"]
        print(f"\n--- variante {variante} ---")
        print(f"  enveloppe observee : {info['n']} places, "
              f"{info['designes']} designes par chaque etalon")
        if len(seuils_ips) == 1:
            print(f"  seuil IPS  : {seuils_ips[0]:.2f} "
                  f"({info['exaequo_ips']} ex aequo)")
            print(f"  seuil note : {seuils_note[0]:.1f} "
                  f"({info['exaequo_note']} ex aequo)")
        else:
            print(f"  {len(seuils_ips)} seuils IPS  : "
                  f"{min(seuils_ips):.1f} a {max(seuils_ips):.1f} "
                  f"({info['exaequo_ips']} ex aequo cumules)")
            print(f"  {len(seuils_note)} seuils note : "
                  f"{min(seuils_note):.1f} a {max(seuils_note):.1f} "
                  f"({info['exaequo_note']} ex aequo cumules)")
        print(f"  designes par les deux : {info['communs']} "
              f"({100 * info['communs'] / info['n']:.1f} %)")

        tables[variante] = resumer(df, info["suffixe"])
        print(tables[variante][colonnes].round(1).to_string())

    print(f"\n{params['bascules']} colleges changent de verdict en passant du "
          f"classement national au classement academique "
          f"({100 * params['bascules'] / len(df):.1f} % du champ)")

    print("\nFigures :")
    figure_nuage(df, tables, params)

    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    # La carte porte la variante ACADEMIQUE : voir la docstring de
    # `figure_cartes` pour la raison, qui n'est pas cosmetique.
    dep = agreger(df, params["académique"]["suffixe"])
    figure_cartes(dep, contours, params)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    sortie = ["uai", "nom", "ep", "ips", "note_ecrit_dnb", "nb_candidats_dnb",
              "designe_ips", "designe_note", "verdict",
              "designe_ips_academie", "designe_note_academie",
              "verdict_academie", "frontiere_ips", "frontiere_note",
              "code_departement", "departement", "code_academie", "academie"]
    df[sortie].to_csv(DOSSIER_TABLES / "comparaison_etalons.csv",
                      index=False, encoding="utf-8")
    dep.round(2).to_csv(DOSSIER_TABLES / "comparaison_etalons_par_departement.csv",
                        index=False, encoding="utf-8")

    assez = dep[dep["colleges"] >= MIN_ETABLISSEMENTS]
    vue = ["departement", "colleges", "ips_seul", "part_ips_seul",
           "note_seule", "part_note_seule"]
    print("\n  (variante academique) desaccord le plus marque en faveur de l'IPS :")
    print(assez.nlargest(6, "part_ips_seul")[vue].round(1).to_string(index=False))
    print("\n  (variante academique) desaccord le plus marque en faveur des "
          "resultats :")
    print(assez.nlargest(6, "part_note_seule")[vue].round(1).to_string(index=False))

    print(f"\n[+] comparaison_etalons.csv ({len(df)} lignes)")
    print(f"[+] comparaison_etalons_par_departement.csv ({len(dep)} lignes)")


if __name__ == "__main__":
    main()
