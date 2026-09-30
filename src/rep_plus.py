"""Second volet : et si l'on ne regardait que REP+ ?

LA QUESTION

Tout le reste du projet traite l'education prioritaire comme un bloc : 1 094
colleges classes, REP et REP+ confondus. Ce module reduit l'enveloppe au seul
REP+ — 362 places — et repose la meme question : le dispositif retient-il les
362 colleges les plus bas du pays ?

La mecanique ne change pas d'une ligne. Elle est importee de `score_ecart.py`,
qui travaille sur une colonne `classe_ep` : il suffit de la redefinir.

CE QUE LE CHANGEMENT DE PERIMETRE FAIT A LA QUESTION

Il la deplace, et c'est le resultat principal de ce volet.

Sur les 102 colleges que l'IPS designe sans que REP+ les retienne, 91 sont
DEJA CLASSES REP. Onze seulement sont hors education prioritaire. Un "oubli"
ne signifie donc presque jamais que l'Etat n'a rien fait : il signifie qu'il a
mis REP la ou l'IPS dirait REP+.

On passe d'une question de COUVERTURE — qui est aide, qui ne l'est pas — a une
question de GRADUATION — qui est aide au bon niveau. La figure distingue les
deux cas par la couleur, sans quoi le mot "oubli" serait trompeur pour un
lecteur venant de la premiere partie.

POURQUOI PAS DE VARIANTE ACADEMIQUE ICI

Le reste du projet calcule tout deux fois, au seuil national et au seuil
academique. Sur REP+ la seconde n'a pas de sens : onze academies comptent moins
de cinq REP+, et trois n'en comptent qu'UN — Dijon, Rennes, la Corse. Un seuil
budgetaire calcule sur une seule place, et un ratio d'enveloppe qui en decoule,
ne mesureraient que le hasard du college concerne. Ce volet s'en tient donc au
seuil national, et le dit plutot que de produire des chiffres ininterpretables.

Prerequis : `uv run python -m src.preparation`

Lancement (depuis la racine du projet) :
    uv run python -m src.rep_plus
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import matplotlib.patheffects as pe
from matplotlib.colors import BoundaryNorm, ListedColormap

from src.analyse import charger, restreindre_au_public
from src.carte_enveloppe import (DIVERGENTE, DROM_ACADEMIES,
                                 contours_academiques)
from src.cartographie import annoter_drom, charger_contours
from src.config import FIGURES, PROJECT_ROOT
from src.etalons import ETALONS
from src.score_ecart import ajouter_score, controler_identite

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE, ORANGE_CLAIR = "#1f3b73", "#eb6834", "#f2a888"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
GRIS_ABSENT = "#e3e3e3"

# Rampes des cartes, du clair au fonce. Une seule teinte par carte : l'effectif
# est une grandeur d'intensite, une palette categorielle suggererait des
# categories qui n'existent pas.
BLEUS = ["#dce6f5", "#9ec4ee", "#5588cc", "#1f3b73", "#132548"]
ORANGES = ["#fbe3d5", "#f2a888", "#eb6834", "#a8401a", "#6b280f"]

# En dessous de ce nombre de colleges dans l'ensemble optimal, le ratio
# d'enveloppe d'une academie repose sur trop peu d'observations pour etre lu
# comme les autres. Le seuil est plus bas que celui de `carte_enveloppe` — cinq
# contre dix — parce que l'enveloppe entiere est trois fois plus petite : le
# retenir a dix marquerait presque toutes les academies et ne dirait plus rien.
SEUIL_FRAGILE = 5

# Largeur de classe de l'histogramme, par etalon : l'IPS s'etale sur une
# centaine de points, le score de sixieme sur plusieurs centaines.
PAS_PAR_ETALON = {"ips": 1.0, "eval6": 4.0}

# Les trois categories de l'histogramme. L'ordre va du cas le moins grave au
# plus grave : un college deja classe REP a recu quelque chose, un college
# hors education prioritaire n'a rien recu.
CATEGORIES = [
    ("sur-inclus", BLEU, "Sur-inclusions — REP+ au-dessus du seuil"),
    ("oubli REP", ORANGE_CLAIR, "Oublis DÉJÀ classés REP"),
    ("oubli hors EP", ORANGE, "Oublis hors éducation prioritaire"),
]


def preparer(cle: str) -> tuple[pd.DataFrame, dict]:
    """Calcule le score d'ecart sur l'enveloppe REP+, pour un etalon.

    `classe_ep` est redefinie AVANT d'appeler `ajouter_score` : toute la
    mecanique de `score_ecart.py` travaille sur cette colonne, et c'est elle
    seule qui porte le perimetre. Aucune autre ligne du calcul ne change.
    """
    etalon = ETALONS[cle]
    colonne = etalon["colonne"]

    df = restreindre_au_public(charger()).dropna(subset=[colonne]).copy()
    df = df.sort_values("uai").reset_index(drop=True)
    df["classe_ep"] = df["ep"] == "REP+"

    df = ajouter_score(df, [], colonne, "")
    controler_identite(df, [], colonne, "", f"REP+ / {etalon['libelle']}")

    # Le type d'ecart de `score_ecart` ne distingue pas les deux sortes
    # d'oubli. C'est pourtant toute la question ici.
    df["categorie"] = np.select(
        [df["type_ecart"] == "sur-inclus",
         (df["type_ecart"] == "oublie") & (df["ep"] == "REP"),
         (df["type_ecart"] == "oublie")],
        ["sur-inclus", "oubli REP", "oubli hors EP"], default="conforme")

    # Score signe : positif pour un oubli, negatif pour une sur-inclusion.
    df["ecart_signe"] = np.select(
        [df["type_ecart"] == "oublie", df["type_ecart"] == "sur-inclus"],
        [df["score_ecart"], -df["score_ecart"]], default=0.0)

    n = int(df["classe_ep"].sum())
    comptes = df["categorie"].value_counts()
    info = {
        "etalon": etalon, "cle": cle, "n": n, "champ": len(df),
        "seuil": float(df["seuil"].iloc[0]),
        "exaequo": int((df[colonne] == df["seuil"].iloc[0]).sum()),
        "comptes": comptes,
        "bien_places": n - int(comptes.get("sur-inclus", 0)),
    }
    return df, info


def resumer(df: pd.DataFrame, info: dict) -> None:
    """Affiche ce que la figure porte."""
    etalon = info["etalon"]
    print(f"\n{'=' * 78}")
    print(f"PERIMETRE REP+ — ETALON {etalon['libelle_long'].upper()}")
    print("=" * 78)
    print(f"\n  champ {info['champ']} colleges publics, "
          f"{info['n']} places REP+")
    print(f"  seuil {info['seuil']:.2f} ({info['exaequo']} ex aequo)")
    print(f"  bien places {info['bien_places']} "
          f"({100 * info['bien_places'] / info['n']:.1f} % de l'enveloppe)")

    print("\n  composition des ecarts :")
    for nom, _, libelle in CATEGORIES:
        n = int(info["comptes"].get(nom, 0))
        print(f"    {libelle:<44} {n:>4}")

    oublis = df[df["type_ecart"] == "oublie"]
    if len(oublis):
        part = 100 * (oublis["ep"] == "REP").mean()
        print(f"\n  {part:.0f} % des oublis sont DEJA classes REP : "
              f"la question est la graduation, pas la couverture")

    print("\n  les cinq oublis hors EP les plus marques :")
    hors = oublis[oublis["ep"] == "hors EP"].nlargest(5, "score_ecart")
    # La colonne de l'etalon porte son propre nom a ce stade : `valeur` n'est
    # cree que dans le fichier de sortie de `score_ecart`.
    vue = ["nom", "nom_commune", "academie", etalon["colonne"], "score_ecart"]
    print(hors[vue].round(1).to_string(index=False) if len(hors) else "    aucun")


def panneau(ax, df: pd.DataFrame, info: dict) -> None:
    """Histogramme de l'ecart signe pour un etalon, categories empilees."""
    pas = PAS_PAR_ETALON[info["cle"]]
    signe = df["ecart_signe"].to_numpy()
    borne = np.abs(signe).max()
    # Bornes decalees d'un demi-pas pour que zero tombe au centre d'une classe.
    bins = np.arange(-borne - pas, borne + 2 * pas, pas) - pas / 2

    for nom, couleur, libelle in CATEGORIES:
        valeurs = df.loc[df["categorie"] == nom, "ecart_signe"]
        if valeurs.empty:
            continue
        ax.hist(valeurs, bins=bins, color=couleur, alpha=0.85, linewidth=0,
                label=f"{libelle} ({len(valeurs)})")

    # Plafond cale sur la plus haute barre NON nulle : la barre du zero
    # ecraserait tout le reste.
    hors_zero = signe[signe != 0]
    plafond = np.histogram(hors_zero, bins=bins)[0].max() * 1.4
    ax.set_ylim(0, plafond)

    nuls = int((signe == 0).sum())
    ax.bar(0, plafond, width=pas * 0.9, color=MUET, alpha=0.3, linewidth=0,
           zorder=0)
    ax.annotate(f"{nuls:,}".replace(",", " ") + " conformes\nbarre tronquée",
                xy=(0, plafond), xytext=(6, -6), textcoords="offset points",
                ha="left", va="top", fontsize=7.5, color=ENCRE_2)

    seuil_txt = f"{info['seuil']:.{info['etalon']['decimales']}f}".replace(
        ".", ",")
    ax.set_title(f"Étalon {info['etalon']['libelle']} — seuil {seuil_txt}",
                 fontsize=10.5, fontweight="bold", loc="left", color=ENCRE)
    ax.set_xlabel(f"Écart {info['etalon']['de_article']} au seuil REP+\n"
                  "← sur-inclusion          conforme          oubli →",
                  fontsize=9)
    ax.set_ylabel("Nombre de collèges", fontsize=9)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.grid(True, linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)


def figure(donnees: dict) -> None:
    """Les deux etalons cote a cote, sur l'enveloppe REP+."""
    # L'etiquette d'axe tient sur deux lignes : la marge basse doit la loger
    # ENTIEREMENT avant que la note ne commence, sans quoi les deux se
    # chevauchent.
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.9))
    fig.subplots_adjust(left=0.058, right=0.982, top=0.792, bottom=0.330,
                        wspace=0.17)

    for ax, cle in zip(axes, ETALONS):
        df, info = donnees[cle]
        panneau(ax, df, info)

    # Les nombres sont formates AVANT d'entrer dans la chaine : une
    # substitution de virgule sur un bloc de litteraux adjacents toucherait
    # aussi les points de fin de phrase.
    ips = donnees["ips"][1]
    part_rep = 100 * ips["comptes"].get("oubli REP", 0) / max(
        ips["comptes"].get("oubli REP", 0) + ips["comptes"].get("oubli hors EP", 0), 1)
    part_txt = f"{part_rep:.0f}"
    hors_ep = int(ips["comptes"].get("oubli hors EP", 0))

    fig.suptitle("Et si l'on ne regardait que REP+ ?",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.972)
    fig.text(0.02, 0.918,
             f"Même mécanique que le reste du projet, mais l'enveloppe se "
             f"réduit aux {ips['n']} places REP+ au lieu des 1 094 places de "
             f"l'éducation prioritaire entière.\n"
             f"Le seuil devient l'IPS du {ips['n']}ᵉ collège le plus bas du "
             f"pays. Conséquence : les 732 collèges REP deviennent NON CLASSÉS, "
             f"donc candidats à l'oubli.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.212,
             f"Le résultat principal tient dans la couleur des barres de droite. "
             f"Sur l'étalon IPS, {part_txt} % des oublis sont DÉJÀ classés REP — "
             f"seulement {hors_ep} sont hors éducation prioritaire.\n"
             f"Un oubli ne signifie donc presque jamais que l'État n'a rien "
             f"fait : il signifie qu'il a mis REP là où l'IPS dirait REP+. La "
             f"question n'est plus la couverture mais la GRADUATION.\n"
             "Les sur-inclusions, elles, sont toutes des REP+ par construction : "
             "un collège classé REP+ dont la valeur dépasse le seuil.\n"
             "Pas de variante académique sur ce périmètre : onze académies "
             "comptent moins de cinq REP+ et trois n'en comptent qu'un — Dijon, "
             "Rennes, la Corse. Un seuil calculé\n"
             "sur une seule place ne mesurerait que le hasard du collège "
             "concerné.\n"
             "Ni l'IPS ni le score de 6ᵉ n'est le critère officiel de "
             "classement : un écart mesure un désaccord entre deux instruments, "
             "pas une erreur administrative.\n"
             "Champ : collèges publics, rentrée 2024-2025 / évaluations de "
             "septembre 2024. Sources : DEPP (IPS, évaluations nationales de "
             "sixième), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "rep_plus_ecart.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def classes_effectif(maximum: int, teintes: list[str]) -> tuple:
    """Bornes, couleurs et etiquettes d'une echelle de comptage.

    L'effectif est un entier : une rampe continue suggererait des valeurs
    intermediaires qui n'existent pas. Les classes s'arretent au maximum
    OBSERVE, sans quoi la legende annoncerait des categories vides.
    """
    paliers = [0.5, 1.5, 2.5, 3.5, 5.5]
    bornes = np.array([b for b in paliers if b < maximum] + [maximum + 0.5])
    couleurs = teintes[:len(bornes) - 1]

    etiquettes, precedent = [], 1
    for borne in bornes[1:-1]:
        haut = int(borne - 0.5)
        etiquettes.append(f"{precedent}" if haut == precedent
                          else f"{precedent} à {haut}")
        precedent = haut + 1
    etiquettes.append(f"{precedent}" if maximum == precedent
                      else f"{precedent} à {maximum}")
    return bornes, couleurs, [f"{e} collège" + ("s" if e != "1" else "")
                              for e in etiquettes]


def carte(ax, sous: pd.DataFrame, contours, teintes: list[str], titre: str,
          signales=None) -> tuple[int, int]:
    """Choroplethe departementale d'un effectif, chiffre inscrit sur la carte.

    Args:
        signales: sous-ensemble dont les departements recoivent un contour
            appuye. Sert ici a designer les departements comptant au moins un
            oubli HORS education prioritaire — l'information propre a ce volet.

    Returns:
        Le total et le nombre de departements concernes, pour la note.
    """
    par_dep = sous.groupby("code_departement").size().rename("effectif")
    gdf = contours.join(par_dep, how="left")
    gdf["effectif"] = gdf["effectif"].fillna(0)

    concernes = gdf["effectif"] > 0
    maximum = int(gdf["effectif"].max())
    bornes, couleurs, etiquettes = classes_effectif(maximum, teintes)
    cmap = ListedColormap(couleurs)
    norme = BoundaryNorm(bornes, ncolors=cmap.N)

    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.4)
    gdf[concernes].plot(ax=ax, column="effectif", cmap=cmap, norm=norme,
                        edgecolor="white", linewidth=0.4)

    if signales is not None and len(signales):
        marques = gdf.index.isin(signales["code_departement"].unique())
        gdf[marques].plot(ax=ax, facecolor="none", edgecolor=ENCRE,
                          linewidth=1.6, zorder=4)

    # Le chiffre est ecrit sur le departement. Le blanc devient illisible sur
    # les teintes claires : la couleur du texte suit l'intensite du fond.
    seuil_blanc = bornes[max(len(bornes) - 3, 1)]
    for _, ligne in gdf[concernes].iterrows():
        point = ligne["geometry"].representative_point()
        effectif = int(ligne["effectif"])
        ax.annotate(str(effectif), xy=(point.x, point.y), ha="center",
                    va="center", fontsize=7.5, fontweight="bold",
                    color="white" if effectif >= seuil_blanc else ENCRE)

    annoter_drom(ax, contours)
    ax.set_axis_off()
    ax.set_title(titre, fontsize=11.5, fontweight="bold", loc="left",
                 color=ENCRE)

    poignees = [plt.Rectangle((0, 0), 1, 1, color=c) for c in couleurs]
    ax.legend(poignees, etiquettes, loc="upper right", frameon=False,
              fontsize=8, title="Collèges du département", title_fontsize=8)
    return int(gdf["effectif"].sum()), int(concernes.sum())


def figure_cartes(df: pd.DataFrame, info: dict, contours) -> None:
    """Ou se trouvent les ecarts a l'enveloppe REP+ ?"""
    etalon = info["etalon"]
    sur = df[df["categorie"] == "sur-inclus"]
    oublis = df[df["type_ecart"] == "oublie"]
    hors_ep = oublis[oublis["ep"] == "hors EP"]

    fig, axes = plt.subplots(1, 2, figsize=(13, 9.6))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.855, bottom=0.245,
                        wspace=0.02)

    n_sur, dep_sur = carte(axes[0], sur, contours, BLEUS,
                           "Sur-inclusions — REP+ au-dessus du seuil")
    n_oub, dep_oub = carte(axes[1], oublis, contours, ORANGES,
                           "Oublis — sous le seuil sans être REP+",
                           signales=hors_ep)

    # La liste s'allonge avec l'etalon — neuf departements sur l'IPS, bien
    # plus sur le score de sixieme — donc on la replie plutot que de la laisser
    # deborder du cadre.
    # "l'IPS" -> "L'IPS" : `capitalize` minusculerait le reste du mot.
    avec = etalon["avec_article"]
    sujet = avec[0].upper() + avec[1:]

    departements = textwrap.fill(
        "Départements concernés : "
        + ", ".join(sorted(hors_ep["departement"].str.title().unique())) + ".",
        width=150)

    fig.suptitle(f"Où se trouvent les écarts à l'enveloppe REP+ ?\n"
                 f"Étalon {etalon['libelle']}, collèges publics, "
                 f"rentrée 2024-2025",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)

    fig.text(0.02, 0.198,
             f"À gauche, les {n_sur} collèges classés REP+ dont la valeur "
             f"dépasse le seuil, répartis sur {dep_sur} départements. À droite, "
             f"les {n_oub} collèges sous le seuil que REP+ ne retient pas, sur "
             f"{dep_oub} départements.\n"
             f"CONTOUR APPUYÉ à droite : les départements comptant au moins un "
             f"oubli HORS éducation prioritaire — {len(hors_ep)} collèges en "
             f"tout, dans {hors_ep['code_departement'].nunique()} départements. "
             f"Partout ailleurs,\n"
             f"les oublis sont des collèges DÉJÀ classés REP : l'écart porte sur "
             f"le niveau d'aide, pas sur son existence.\n"
             + departements + "\n"
             "Les classes sont des effectifs entiers et non une rampe continue : "
             "un département compte deux collèges ou trois, jamais deux et demi. "
             "En gris, les départements sans aucun cas.\n"
             "Les deux séries ont exactement le même effectif : un collège "
             "sur-inclus prend la place d'un collège qui aurait dû l'être. C'est "
             "une propriété du calcul, pas un résultat.\n"
             f"{sujet} n'est pas le critère officiel de classement : "
             "un écart mesure un désaccord entre deux instruments, pas une erreur "
             "administrative.\n"
             f"Sources : {etalon['source']}, annuaire de l'éducation, contours "
             "Insee/cartiflette. DROM rapprochés, échelles et distances non "
             "respectées.",
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / f"rep_plus_cartes_{info['cle']}.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"[+] {chemin.name}")


def ratios_academiques(df: pd.DataFrame, info: dict) -> pd.DataFrame:
    """Places REP+ recues, rapportees aux colleges dans l'ensemble optimal.

    CE QUE LE RATIO NE DEMANDE PAS

    Il ne demande AUCUN seuil academique — c'est pourquoi il reste calculable
    ici alors que la variante academique du score ne l'est pas. Le denominateur
    est le nombre de colleges de l'academie figurant parmi les n colleges les
    plus bas DU PAYS, n etant le nombre de places. Les deux totaux nationaux
    sont le meme nombre, donc le ratio de la France vaut 1 par construction.

    CE QU'IL DEMANDE EN REVANCHE

    Un denominateur assez grand pour etre lu. Sur l'education prioritaire
    entiere il descendait a deux colleges ; sur REP+ il descend a UN — Paris,
    Bordeaux — et la Corse n'en compte AUCUN au score de sixieme, ce qui rend
    son ratio indefini. La figure porte donc les deux effectifs sous chaque
    ratio : a cette echelle, « 4,00 » seul serait trompeur la ou « 4/1 » est
    honnete.
    """
    n = int(df["classe_ep"].sum())
    colonne = info["etalon"]["colonne"]
    optimal = set(df.nsmallest(n, colonne)["uai"])

    aca = df.assign(dans_optimal=df["uai"].isin(optimal)).groupby(
        ["code_academie", "academie"]).agg(
        colleges=("uai", "size"),
        places=("classe_ep", "sum"),
        optimal=("dans_optimal", "sum"),
    ).reset_index()

    # Division par zero laissee a NaN plutot que comblee : une academie sans
    # aucun college dans l'ensemble optimal n'a pas un ratio infini, elle n'en
    # a pas. La carte la laisse en gris et la note la nomme.
    aca["ratio"] = aca["places"] / aca["optimal"].replace(0, np.nan)
    aca["fragile"] = aca["optimal"] < SEUIL_FRAGILE
    return aca


def classes_ratio_rep_plus(ratios: np.ndarray) -> np.ndarray:
    """Bornes de classes sur le logarithme du ratio, bande centrale symetrique.

    POURQUOI NE PAS REUTILISER CELLE DE `carte_enveloppe`

    Elle prend ses bornes interieures sur les quantiles de |log2(ratio)|, TOUS
    ecarts confondus. Sur REP+ cela echoue : douze academies sur trente ont un
    ratio exactement egal a 1 — avec des effectifs aussi petits, places et
    ensemble optimal coincident souvent — donc les quantiles a 35 % et 70 %
    valent zero, les classes s'effondrent et la barre affiche « 1,00 » trois
    fois de suite.

    Ici les quantiles sont pris sur les seuls ecarts NON NULS, et zero n'est
    pas une borne mais le milieu d'une bande centrale symetrique. Les academies
    a ratio exactement 1 tombent donc dans la classe neutre, ce qui est leur
    place.
    """
    ecarts = np.abs(np.log2(ratios))
    non_nuls = ecarts[ecarts > 1e-9]
    interieures = (np.unique(np.quantile(non_nuls, [0.45, 0.80]))
                   if len(non_nuls) >= 2 else np.array([]))
    extreme = ecarts.max()
    bornes = np.concatenate([[-extreme], -interieures[::-1],
                             interieures, [extreme]])
    return np.unique(np.round(bornes, 4))


def figure_ratio(df: pd.DataFrame, info: dict, aca: pd.DataFrame) -> None:
    """Choroplethe academique du ratio d'enveloppe REP+."""
    etalon = info["etalon"]
    rattachement = (df.groupby("code_departement")["academie"]
                    .first().rename("academie"))
    gdf = contours_academiques(rattachement).join(
        aca.set_index("academie")[["ratio", "places", "optimal", "fragile"]])
    connus = gdf["ratio"].notna()

    bornes = classes_ratio_rep_plus(gdf.loc[connus, "ratio"].to_numpy())
    cmap = DIVERGENTE.resampled(len(bornes) - 1)
    norme = BoundaryNorm(bornes, ncolors=len(bornes) - 1)

    fig, ax = plt.subplots(figsize=(9.5, 11.4))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.876, bottom=0.215)

    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.5)
    gdf[connus].assign(log=np.log2(gdf.loc[connus, "ratio"])).plot(
        ax=ax, column="log", cmap=cmap, norm=norme, edgecolor="white",
        linewidth=0.5)

    contour = [pe.withStroke(linewidth=2.2, foreground="white")]
    for nom, ligne in gdf.iterrows():
        point = ligne["geometry"].representative_point()
        if pd.isna(ligne["ratio"]):
            texte = "—"
        else:
            texte = f"{ligne['ratio']:.2f}".replace(".", ",")
        ax.annotate(texte, xy=(point.x, point.y), ha="center", va="bottom",
                    fontsize=6.8, fontweight="bold", color=ENCRE,
                    path_effects=contour)
        # Les deux effectifs sous le ratio : a ces ordres de grandeur, le
        # rapport seul ne dit pas s'il repose sur un college ou sur trente.
        detail = f"{int(ligne['places'])}/{int(ligne['optimal'])}"
        ax.annotate(detail, xy=(point.x, point.y), xytext=(0, -8),
                    textcoords="offset points", ha="center", va="top",
                    fontsize=5.6, color=ENCRE_2, path_effects=contour)

    for code, etiquette in DROM_ACADEMIES.items():
        if code in gdf.index:
            forme = gdf.loc[code, "geometry"]
            ax.annotate(etiquette, xy=(forme.centroid.x, forme.bounds[1] - 0.3),
                        ha="center", va="top", fontsize=6.5, color=ENCRE_2)
    ax.set_axis_off()

    echelle = plt.cm.ScalarMappable(cmap=cmap, norm=norme)
    cax = fig.add_axes([0.28, 0.178, 0.44, 0.013])
    fig.colorbar(echelle, cax=cax, orientation="horizontal", ticks=bornes,
                 spacing="uniform")
    cax.set_xticklabels([f"{2 ** b:.2f}".replace(".", ",") for b in bornes],
                        fontsize=6.5)
    cax.set_xlabel("← reçoit moins que l'étalon        ratio = 1        "
                   "reçoit plus →", fontsize=8, labelpad=4)

    sans = sorted(a.title() for a in gdf.index[~connus])
    fragiles = sorted(a.title() for a in gdf.index[gdf["fragile"].fillna(False)])

    fig.suptitle(f"Chaque académie reçoit-elle autant de places REP+ qu'elle "
                 f"compte\nde collèges parmi les plus bas de France ? — étalon "
                 f"{etalon['libelle']}",
                 fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.918,
             f"Ratio entre les {info['n']} places REP+ reçues et le nombre de "
             f"collèges de l'académie figurant parmi les {info['n']} collèges "
             f"publics dont\n"
             f"{etalon['avec_article']} est le plus bas du pays — soit exactement "
             f"le nombre de places distribuées. Le ratio national vaut donc 1 "
             f"par\nconstruction. Sous chaque ratio, les deux effectifs dont il "
             f"est le rapport.",
             fontsize=8.5, va="top", color=ENCRE_2)

    avertissement = textwrap.fill(
        f"LIRE AVEC PRUDENCE. Sur l'éducation prioritaire entière, ce ratio "
        f"reposait sur des dénominateurs de deux collèges au minimum ; sur REP+ "
        f"il descend à un. {len(fragiles)} académies en comptent moins de "
        f"{SEUIL_FRAGILE} dans l'ensemble optimal : {', '.join(fragiles)}.", 150)
    if sans:
        avertissement += "\n" + textwrap.fill(
            f"Sans aucun collège dans l'ensemble optimal, donc sans ratio défini "
            f"et laissée en gris : {', '.join(sans)}.", 150)

    fig.text(0.02, 0.148, avertissement + "\n"
             "L'échelle suit le logarithme du ratio, celui-ci étant "
             "multiplicatif : recevoir deux fois trop et deux fois trop peu sont "
             "deux écarts de même ampleur.\n"
             "Les classes sont des quantiles de la distribution observée, et la "
             "barre reste graduée en ratios.\n"
             "La répartition des réseaux entre académies est arrêtée au niveau "
             "national sans clé de calcul publiée : ce ratio mesure une clé "
             "implicite, il n'en reprend aucune.\n"
             f"Champ : collèges publics, rentrée 2024-2025. Sources : "
             f"{etalon['source']}, annuaire de l'éducation, contours "
             "Insee/cartiflette. DROM rapprochés,\n"
             "échelles et distances non respectées.",
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / f"rep_plus_ratio_{info['cle']}.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"[+] {chemin.name}")


def main() -> None:
    donnees = {}
    for cle in ETALONS:
        df, info = preparer(cle)
        resumer(df, info)
        donnees[cle] = (df, info)

    figure(donnees)

    print("\nContours :")
    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    print(f"  {len(contours)} departements")
    for cle, (df, info) in donnees.items():
        figure_cartes(df, info, contours)

    for cle, (df, info) in donnees.items():
        aca = ratios_academiques(df, info)
        figure_ratio(df, info, aca)
        chemin = DOSSIER_TABLES / f"rep_plus_ratio_{cle}.csv"
        aca.round(3).to_csv(chemin, index=False, encoding="utf-8")
        print(f"[+] {chemin.name} ({len(aca)} academies)")

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    for cle, (df, _) in donnees.items():
        colonnes = ["uai", "nom", "ep", "valeur", "seuil", "score_ecart",
                    "type_ecart", "categorie", "nom_commune",
                    "code_departement", "departement", "code_academie",
                    "academie"]
        chemin = DOSSIER_TABLES / f"rep_plus_{cle}.csv"
        df.assign(valeur=df[ETALONS[cle]["colonne"]])[colonnes].to_csv(
            chemin, index=False, encoding="utf-8")
        print(f"[+] {chemin.name} ({len(df)} colleges)")


if __name__ == "__main__":
    main()
