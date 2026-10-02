"""Les ratios d'enveloppe des deux etalons, academie par academie.

CE QUE MESURE LE RATIO

Pour chaque academie, le rapport entre les places d'education prioritaire
recues et le nombre de ses colleges figurant parmi les n plus bas du pays, n
etant le nombre total de places. Les deux termes sont, au niveau national, le
meme nombre : le ratio de la France vaut donc 1 PAR CONSTRUCTION, pour les deux
etalons. Chaque carte se lit comme une redistribution a somme nulle.

`carte_enveloppe.py` cartographie ces ratios, un etalon par figure. Ce module
les met face a face, ce qu'une carte ne permet pas : on ne compare pas deux
teintes sur deux fonds distincts, on lit un deplacement.

POURQUOI UN GRAPHE EN HALTERES

Chaque academie est une ligne, chaque etalon un point, et le segment qui les
relie EST l'information : sa longueur donne l'ampleur du desaccord, son sens
donne qui des deux etalons juge l'academie mieux dotee. Un graphe en barres
groupees rendrait la comparaison entre academies facile et la comparaison entre
etalons difficile, alors que c'est cette seconde qui nous interesse.

POURQUOI UNE ECHELLE LOGARITHMIQUE

Le ratio est multiplicatif : recevoir deux fois trop et deux fois trop peu sont
deux ecarts de meme ampleur, alors qu'en echelle lineaire le premier vaut +1 et
le second -0,5. Sans logarithme, la moitie basse du graphe serait ecrasee contre
zero et les segments y paraitraient courts a tort. Les graduations restent
libellees en ratios.

CE QUE LA FIGURE REND VISIBLE

La moitie des academies change de cote. Elles sont surlignees, parce que c'est
le seul fait qui compte vraiment : au-dessus de 1 et en dessous de 1 ne sont pas
deux nuances d'une meme chose, ce sont deux diagnostics opposes.

RESERVE

Aucun des deux etalons n'est le critere officiel de classement. Un ecart a 1
mesure un desaccord entre deux instruments, pas une erreur de repartition. Et le
desaccord entre les deux etalons ne dit pas lequel a raison.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.ratios_enveloppe
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES, PROJECT_ROOT
from src.carte_enveloppe import SEUIL_OPTIMAL, SEUIL_PLACES, ratio_lisible
from src.etalons import ETALONS, fichier_academies
from src.etiquettes import placer_etiquettes
from src.noms import academie, academies

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE = "#1f3b73", "#eb6834"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

# Graduations de l'axe, en ratios. Choisies pour encadrer l'etendue observee
# (0,44 a 5,50) en restant des valeurs qu'un lecteur interprete sans effort.
GRADUATIONS = [0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0]

# Le critere de lisibilite d'un ratio — une double condition portant sur le
# numerateur ET le denominateur — vient de `carte_enveloppe`, ou il est etabli
# et justifie. Les academies qui n'y satisfont pas portent un asterisque.

# Au-dela de ce ratio, une academie sort du cadre du NUAGE. Elle y etirerait
# l'echelle jusqu'a six et tasserait les vingt-huit autres dans un coin. Deux
# academies sont concernees a ce jour — la Corse et Paris, toutes deux autour
# de cinq — et elles sont signalees dans la figure avec leurs valeurs, jamais
# passees sous silence. Le graphe en halteres, lui, les garde : son echelle
# unique les absorbe sans ecraser le reste.
SEUIL_HORS_CADRE = 2.5


def charger() -> pd.DataFrame:
    """Reunit les ratios des deux etalons en une ligne par academie."""
    colonnes = ["academie", "colleges", "classes", "defavorises_national",
                "ratio_enveloppe"]
    tables = {}
    for cle in ETALONS:
        nom = fichier_academies(cle)
        if not (DOSSIER_TABLES / nom).exists():
            raise FileNotFoundError(
                f"{nom} absent. Lance d'abord : uv run python -m src.score_ecart")
        tables[cle] = pd.read_csv(DOSSIER_TABLES / nom)[colonnes]

    cles = list(ETALONS)
    t = tables[cles[0]].merge(tables[cles[1]], on="academie",
                              suffixes=(f"_{cles[0]}", f"_{cles[1]}"),
                              validate="one_to_one")

    # L'enveloppe ne depend d'aucun etalon — c'est le nombre de places
    # reellement allouees. Elle differe pourtant legerement d'une table a
    # l'autre, et la raison doit etre connue plutot que subie : le champ de
    # l'evaluation exclut les colleges sans score, dont trois sont classes EP
    # (un REP a Grenoble, deux REP+ en Guyane). L'ecart est donc de 3 places
    # sur 1 094, et chaque ratio reste calcule sur son propre champ, ou il
    # vaut 1 pour la France par construction.
    #
    # On l'imprime, et on ne s'arrete que si l'ecart devient assez gros pour
    # signaler autre chose qu'une poignee de valeurs manquantes.
    ecarts = (t[f"classes_{cles[0]}"] - t[f"classes_{cles[1]}"]).abs()
    total = t[f"classes_{cles[0]}"].sum()
    if ecarts.sum():
        touchees = t.loc[ecarts > 0, "academie"].tolist()
        print(f"  enveloppes differentes sur {len(touchees)} academies "
              f"({', '.join(touchees)}) : {int(ecarts.sum())} places sur "
              f"{total}, faute de score pour quelques colleges classes")
    if ecarts.sum() > 0.05 * total:
        raise ValueError(
            f"{int(ecarts.sum())} places d'ecart sur {total} entre les deux "
            f"champs : ce n'est plus une poignee de valeurs manquantes, les "
            f"champs ne concordent pas.")

    t["change_de_cote"] = ((t[f"ratio_enveloppe_{cles[0]}"] > 1)
                           != (t[f"ratio_enveloppe_{cles[1]}"] > 1))
    # Un point est marque des que le ratio est illisible pour L'UN des deux
    # etalons : il ne se compare pas a l'autre si l'un des deux est du bruit.
    t["fragile"] = ~(ratio_lisible(t[f"classes_{cles[0]}"],
                                   t[f"defavorises_national_{cles[0]}"])
                     & ratio_lisible(t[f"classes_{cles[1]}"],
                                     t[f"defavorises_national_{cles[1]}"]))
    return t.sort_values(f"ratio_enveloppe_{cles[0]}", ascending=False)


def resumer(t: pd.DataFrame) -> None:
    """Affiche les reperes que la figure porte."""
    a, b = list(ETALONS)
    ra, rb = f"ratio_enveloppe_{a}", f"ratio_enveloppe_{b}"

    print(f"\n{'=' * 78}")
    print("RATIO D'ENVELOPPE : LES DEUX ETALONS FACE A FACE")
    print("=" * 78)
    print(f"\n  {len(t)} academies")
    print(f"  etendue {ETALONS[a]['libelle']:<12} : "
          f"{t[ra].min():.2f} a {t[ra].max():.2f}")
    print(f"  etendue {ETALONS[b]['libelle']:<12} : "
          f"{t[rb].min():.2f} a {t[rb].max():.2f}")

    # La correlation brute est tiree par les deux academies extremes, qui ont
    # le meme ratio dans les deux etalons. On donne les deux chiffres.
    sans = t[t[ra] < 3]
    print(f"\n  correlation des deux ratios : {t[ra].corr(t[rb]):+.3f}")
    print(f"    hors les deux academies au-dela de 3 : "
          f"{sans[ra].corr(sans[rb]):+.3f} (n = {len(sans)})")

    n_change = int(t["change_de_cote"].sum())
    print(f"\n  academies changeant de cote (de part et d'autre de 1) : "
          f"{n_change} sur {len(t)}")

    t = t.assign(ecart=(t[rb] - t[ra]).round(2))
    vue = ["academie", ra, rb, "ecart"]
    print("\n  les plus gros deplacements :")
    print(t.reindex(t["ecart"].abs().sort_values(ascending=False).index)[vue]
          .head(8).to_string(index=False))
    print("\n  inchangees :")
    print(t[t["ecart"].abs() < 0.05][vue].to_string(index=False))



def figure_nuage(t: pd.DataFrame) -> None:
    """Nuage des deux ratios : un point par academie, taille = enveloppe.

    CE QUE LE NUAGE AJOUTE AUX HALTERES

    Deux choses que l'autre figure ne peut pas montrer.

    La DIAGONALE d'abord : un point dessus signifie que les deux etalons
    s'accordent exactement, et la distance a la diagonale mesure le desaccord.
    Les halteres donnaient cette distance mais pas le niveau commun.

    Le POIDS ensuite. Les halteres traitent les trente academies a egalite,
    alors qu'un ratio de 0,75 sur 118 places — Lille — ne pese pas comme un
    ratio de 1,40 sur 7 places — Limoges. La surface du point est donc
    proportionnelle au nombre de places, ce qui remet les petites academies a
    leur place reelle dans la redistribution.

    LES QUATRE QUADRANTS

    Les deux droites a 1 decoupent le plan en quatre. En bas a gauche et en
    haut a droite, les deux etalons s'accordent sur le SENS. Dans les deux
    autres quadrants ils se contredisent, et ce sont les quinze academies
    surlignees de la figure precedente.

    LE CADRAGE

    Deux academies ont un ratio proche de cinq dans les deux etalons — la Corse
    et Paris, dont l'ensemble optimal ne compte que deux et six colleges. Les
    inclure dans le cadre etirait l'echelle jusqu'a six et tassait les
    vingt-huit autres dans le quart inferieur gauche, ou plus rien ne se
    distinguait.

    Elles sont donc HORS CADRE, et signalees comme telles dans le coin
    superieur droit, avec leurs valeurs. Les omettre en silence serait
    malhonnete : le lecteur doit savoir que le nuage n'est pas complet, et que
    ces deux academies sont exactement sur la diagonale — les deux etalons
    s'accordent sur elles.
    """
    a, b = list(ETALONS)
    ra, rb = f"ratio_enveloppe_{a}", f"ratio_enveloppe_{b}"

    # Le cadre est deduit des academies NON extremes, puis les extremes sont
    # renvoyees dans la note du coin. Le critere porte sur la donnee et non sur
    # une liste de noms : si la Corse rentrait dans le rang une annee, le
    # cadrage suivrait sans qu'on y touche.
    extreme = (t[[ra, rb]].max(axis=1) > SEUIL_HORS_CADRE).to_numpy()
    cadrees, hors = t[~extreme], t[extreme]

    x, y = np.log2(t[ra].to_numpy()), np.log2(t[rb].to_numpy())
    places = t[f"classes_{a}"].to_numpy()

    # La SURFACE du point porte l'enveloppe : c'est l'aire que l'oeil compare,
    # pas le rayon. D'ou la racine carree.
    tailles = 22 + 700 * np.sqrt(places / places.max())

    # Un point est colore quand les deux etalons se contredisent sur le sens,
    # gris quand ils s'accordent. Le gris n'est pas un defaut de la palette :
    # c'est le cas sans information.
    couleurs = np.where(
        ~t["change_de_cote"], MUET,
        np.where(t[ra] > 1, BLEU, ORANGE))

    fig, ax = plt.subplots(figsize=(12.8, 12.4))
    fig.subplots_adjust(left=0.075, right=0.978, top=0.878, bottom=0.200)

    # Bornes calees sur les academies cadrees, avec une marge en LOGARITHME :
    # une marge additive en ratio serait asymetrique, large en haut et etroite
    # en bas.
    valeurs = np.log2(cadrees[[ra, rb]].to_numpy().ravel())
    marge = 0.20 * (valeurs.max() - valeurs.min())
    borne = (valeurs.min() - marge, valeurs.max() + marge)

    ax.plot(borne, borne, color=ENCRE_2, linewidth=1.0, linestyle="--",
            zorder=1)
    # L'etiquette de la diagonale se place dans son quart INFERIEUR : le
    # superieur est occupe par la note des academies hors cadre, et le centre
    # par l'amas des academies proches de 1.
    bas_diagonale = borne[0] + 0.16 * (borne[1] - borne[0])
    ax.annotate("les deux étalons s'accordent",
                xy=(bas_diagonale, bas_diagonale),
                xytext=(8, -12), textcoords="offset points", fontsize=8,
                color=ENCRE_2, rotation=45, rotation_mode="anchor",
                ha="left", va="center")

    ax.axvline(0.0, color=ENCRE, linewidth=1.1, zorder=2)
    ax.axhline(0.0, color=ENCRE, linewidth=1.1, zorder=2)

    dedans = ~extreme
    ax.scatter(x[dedans], y[dedans], s=tailles[dedans], c=couleurs[dedans],
               alpha=0.72, linewidths=0.6, edgecolors="white", zorder=3)

    annotations = []
    for xi, yi, nom, frag in zip(x[dedans], y[dedans], cadrees["academie"],
                                 cadrees["fragile"]):
        annotations.append(ax.annotate(
            f"{academie(nom)}{' *' if frag else ''}", xy=(xi, yi),
            xytext=(11, 0), textcoords="offset points", fontsize=7.5,
            color=ENCRE, va="center", ha="left",
            arrowprops=dict(arrowstyle="-", color=MUET, linewidth=0.5,
                            shrinkA=0, shrinkB=2)))

    # ---- les academies hors cadre, signalees et non tues -------------------
    if len(hors):
        lignes = [
            f"{academie(nom)} : {va:.2f} / {vb:.2f}".replace(".", ",")
            for nom, va, vb in zip(hors["academie"], hors[ra], hors[rb])]
        # Une fleche vers le coin dit dans quelle direction elles se trouvent,
        # ce qu'un simple encadre ne dirait pas.
        ax.annotate("Hors cadre, sur la diagonale ↗\n" + "\n".join(lignes),
                    xy=(borne[1], borne[1]),
                    xytext=(-14, -14), textcoords="offset points",
                    fontsize=8, color=ENCRE_2, ha="right", va="top",
                    linespacing=1.5,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                              edgecolor=GRILLE, linewidth=0.6),
                    arrowprops=dict(arrowstyle="->", color=MUET,
                                    linewidth=0.8, shrinkA=4, shrinkB=2))

    restantes = placer_etiquettes(fig, ax, annotations, places[dedans])
    if restantes:
        print(f"  {restantes} etiquettes sans position libre : elles se "
              f"chevauchent peut-etre")

    # Seules les graduations tombant dans le cadre sont tracees : les autres
    # produiraient des libelles hors de l'axe.
    visibles = [g for g in GRADUATIONS if borne[0] <= np.log2(g) <= borne[1]]
    for graduation in (ax.set_xticks, ax.set_yticks):
        graduation([np.log2(g) for g in visibles])
    etiquettes = [f"{g:g}".replace(".", ",") for g in visibles]
    ax.set_xticklabels(etiquettes, fontsize=8.5)
    ax.set_yticklabels(etiquettes, fontsize=8.5)
    ax.set_xlim(*borne)
    ax.set_ylim(*borne)
    ax.set_aspect("equal")  # sans quoi la diagonale ne serait plus a 45°

    ax.set_xlabel(f"Ratio d'enveloppe selon l'{ETALONS[a]['libelle']}",
                  fontsize=10, labelpad=6)
    ax.set_ylabel(f"Ratio d'enveloppe selon le {ETALONS[b]['libelle']}",
                  fontsize=10, labelpad=6)
    ax.grid(True, linewidth=0.5, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)

    # Legende des couleurs, et legende des tailles : deux encodages, deux
    # legendes, sans quoi la surface des points resterait indechiffrable.
    poignees_couleur = [
        plt.Line2D([], [], marker="o", linestyle="", markersize=8,
                   markerfacecolor=MUET, markeredgecolor="white",
                   label="les deux étalons s'accordent sur le sens"),
        plt.Line2D([], [], marker="o", linestyle="", markersize=8,
                   markerfacecolor=BLEU, markeredgecolor="white",
                   label="sur-dotée selon l'IPS, sous-dotée selon le score"),
        plt.Line2D([], [], marker="o", linestyle="", markersize=8,
                   markerfacecolor=ORANGE, markeredgecolor="white",
                   label="sous-dotée selon l'IPS, sur-dotée selon le score"),
    ]
    premiere = ax.legend(handles=poignees_couleur, loc="upper left",
                         fontsize=8.5, frameon=True, framealpha=0.96,
                         edgecolor=GRILLE)
    premiere.get_frame().set_linewidth(0.6)
    ax.add_artist(premiere)

    reperes = [10, 50, 130]
    poignees_taille = [
        plt.Line2D([], [], marker="o", linestyle="", markeredgecolor=MUET,
                   markerfacecolor="white",
                   markersize=np.sqrt(22 + 700 * np.sqrt(n / places.max())) / 2,
                   label=f"{n} places")
        for n in reperes]
    seconde = ax.legend(handles=poignees_taille, loc="lower right",
                        fontsize=8.5, frameon=True, framealpha=0.96,
                        edgecolor=GRILLE, labelspacing=1.5,
                        title="Enveloppe de l'académie", title_fontsize=8.5,
                        borderpad=1.0)
    seconde.get_frame().set_linewidth(0.6)

    n_change = int(t["change_de_cote"].sum())
    corr = f"{cadrees[ra].corr(cadrees[rb]):+.2f}".replace(".", ",")
    noms_hors = " et ".join(academies(hors["academie"]))

    fig.suptitle("Les deux étalons placent-ils les académies au même endroit ?",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.978)
    fig.text(0.02, 0.940,
             "Chaque académie est un point : son ratio d'enveloppe selon l'IPS "
             "en abscisse, selon le score de 6ᵉ en ordonnée. Un point sur la "
             "diagonale signifie\n"
             "que les deux étalons s'accordent exactement ; la distance à la "
             "diagonale mesure leur désaccord. La surface du point est "
             "proportionnelle au nombre\n"
             "de places de l'académie — un ratio de 0,75 sur 118 places ne pèse "
             "pas comme un ratio de 1,40 sur 7 places.\n"
             f"{noms_hors} sont HORS CADRE : leur ratio proche de cinq étirait "
             f"l'échelle et tassait les {len(cadrees)} autres dans un coin. Leurs "
             f"valeurs sont données en haut à droite.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.140,
             f"Les deux droites à 1 découpent le plan en quatre. En bas à gauche "
             f"et en haut à droite, les deux étalons s'accordent sur le sens. "
             f"Dans les deux autres quadrants\n"
             f"ils se contredisent : ce sont les {n_change} académies sur "
             f"{len(t)} qui changent de côté. Sur les {len(cadrees)} académies "
             f"cadrées, les deux ratios ne corrèlent\n"
             f"qu'à {corr}. {noms_hors}, exclues du cadre, sont exactement sur la "
             f"diagonale : les deux étalons s'accordent sur elles, et les inclure "
             f"porterait la corrélation\n"
             f"à +0,95 — un accord qui serait celui de deux points, pas celui des "
             f"trente académies.\n"
             "Les deux échelles sont logarithmiques, le ratio étant "
             "multiplicatif : recevoir deux fois trop et deux fois trop peu sont "
             "deux écarts de même ampleur. Les\n"
             "graduations restent des ratios, et le repère est orthonormé pour que "
             "la diagonale soit bien à 45°.\n"
             f"(*) ratio non lisible pour au moins un des deux étalons — moins "
             f"de {SEUIL_PLACES} places, ou moins de {SEUIL_OPTIMAL} collèges "
             f"dans l'ensemble optimal. Le second seuil vient de la variance\n"
             f"du dénominateur, mesurée à 0,16 fois sa moyenne sur trois "
             f"rentrées ; le premier de la granularité, le ratio ne pouvant "
             f"valoir que places divisées par collèges.\n"
             "Aucun des deux étalons n'est le critère officiel de classement : un "
             "écart à 1 mesure un désaccord entre deux instruments, pas une erreur "
             "de répartition — et\n"
             "le désaccord entre les deux étalons ne dit pas lequel a raison.\n"
             "Champ : collèges publics, rentrée 2024-2025 / évaluations de "
             "septembre 2024. Sources : DEPP (IPS, évaluations nationales de "
             "sixième), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / "nuage_ratios_etalons.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"[+] {chemin.name}")


def main() -> None:
    t = charger()
    resumer(t)
    figure_nuage(t)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_TABLES / "ratios_enveloppe_etalons.csv"
    t.to_csv(chemin, index=False, encoding="utf-8")
    print(f"[+] {chemin.name} ({len(t)} academies)")


if __name__ == "__main__":
    main()
