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
from src.etalons import ETALONS, fichier_academies

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE = "#1f3b73", "#eb6834"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

# Graduations de l'axe, en ratios. Choisies pour encadrer l'etendue observee
# (0,44 a 5,50) en restant des valeurs qu'un lecteur interprete sans effort.
GRADUATIONS = [0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0, 5.0]

# En dessous de ce nombre de colleges dans l'ensemble optimal, le ratio repose
# sur trop peu d'observations : l'academie est signalee d'un asterisque.
SEUIL_FRAGILE = 10


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
    t["fragile"] = ((t[f"defavorises_national_{cles[0]}"] < SEUIL_FRAGILE)
                    | (t[f"defavorises_national_{cles[1]}"] < SEUIL_FRAGILE))
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


def figure(t: pd.DataFrame) -> None:
    """Graphe en halteres : une ligne par academie, un point par etalon."""
    a, b = list(ETALONS)
    ra, rb = f"ratio_enveloppe_{a}", f"ratio_enveloppe_{b}"

    # L'axe travaille en logarithme ; les graduations restent des ratios.
    x_a, x_b = np.log2(t[ra].to_numpy()), np.log2(t[rb].to_numpy())
    y = np.arange(len(t))[::-1]  # premiere ligne en haut

    fig, ax = plt.subplots(figsize=(10.5, 12.4))
    fig.subplots_adjust(left=0.235, right=0.865, top=0.855, bottom=0.165)

    ax.axvline(0.0, color=ENCRE, linewidth=1.3, zorder=2)

    for xa, xb, yy, change in zip(x_a, x_b, y, t["change_de_cote"]):
        # Le segment porte l'information : il est appuye quand il franchit 1,
        # c'est-a-dire quand les deux etalons se contredisent sur le sens.
        ax.plot([xa, xb], [yy, yy],
                color=ENCRE_2 if change else GRILLE,
                linewidth=2.0 if change else 1.6,
                solid_capstyle="round", zorder=1)

    # Quand les deux etalons donnent la meme valeur — Corse, Paris, Bordeaux,
    # Rennes, Orleans-Tours — les deux points se superposent exactement et le
    # second masque le premier : on croirait une valeur manquante. Ces points
    # sont donc traces en deux DEMI-DISQUES accoles, un par etalon.
    confondus = np.isclose(x_a, x_b, atol=1e-9)
    for gauche, couleur, cle in ((True, BLEU, a), (False, ORANGE, b)):
        style = matplotlib.markers.MarkerStyle(
            "o", fillstyle="left" if gauche else "right")
        ax.scatter(x_a[confondus], y[confondus], s=70, color=couleur,
                   marker=style, zorder=3, linewidths=0)

    distincts = ~confondus
    ax.scatter(x_a[distincts], y[distincts], s=46, color=BLEU, zorder=3,
               linewidths=0)
    ax.scatter(x_b[distincts], y[distincts], s=46, color=ORANGE, zorder=3,
               linewidths=0)

    # Poignees de legende tracees hors du champ visible : elles doivent porter
    # le marqueur plein, pas le demi-disque des points confondus.
    for couleur, cle in ((BLEU, a), (ORANGE, b)):
        ax.scatter([], [], s=46, color=couleur, linewidths=0,
                   label=f"Étalon {ETALONS[cle]['libelle']}")

    etiquettes = [f"{nom.title()}{' *' if frag else ''}"
                  for nom, frag in zip(t["academie"], t["fragile"])]
    ax.set_yticks(y)
    ax.set_yticklabels(etiquettes, fontsize=8.5)
    for tick, change in zip(ax.get_yticklabels(), t["change_de_cote"]):
        tick.set_color(ENCRE if change else ENCRE_2)
        tick.set_fontweight("bold" if change else "normal")

    ax.set_xticks([np.log2(g) for g in GRADUATIONS])
    ax.set_xticklabels([f"{g:g}".replace(".", ",") for g in GRADUATIONS],
                       fontsize=8.5)
    ax.set_xlim(np.log2(0.40), np.log2(6.2))
    ax.set_ylim(-0.8, len(t) + 1.9)
    ax.set_xlabel("← reçoit moins que l'étalon        ratio = 1        "
                  "reçoit plus →", fontsize=9.5, labelpad=4)

    ax.grid(True, axis="x", linewidth=0.5, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right", "left"]:
        ax.spines[bord].set_visible(False)
    ax.spines["bottom"].set_color(MUET)
    ax.tick_params(axis="y", length=0)

    # En haut a gauche : c'est la seule zone vide du champ, les ratios eleves
    # etant tous a droite.
    legende = ax.legend(loc="upper left", fontsize=9, frameon=True,
                        framealpha=0.96, edgecolor=GRILLE, markerscale=1.1)
    legende.get_frame().set_linewidth(0.6)

    # Colonne de valeurs a droite : le graphe donne la position, le chiffre
    # donne la valeur exacte, qu'on ne lit pas sur une echelle logarithmique.
    x_texte = ax.get_xlim()[1] + 0.12
    ax.annotate(ETALONS[a]["libelle"], xy=(x_texte, len(t) + 0.45),
                xycoords=("data", "data"), ha="right", va="center",
                fontsize=8, fontweight="bold", color=BLEU,
                annotation_clip=False)
    ax.annotate(ETALONS[b]["libelle"], xy=(x_texte + 0.62, len(t) + 0.45),
                ha="right", va="center", fontsize=8, fontweight="bold",
                color=ORANGE, annotation_clip=False)
    for va, vb, yy in zip(t[ra], t[rb], y):
        ax.annotate(f"{va:.2f}".replace(".", ","), xy=(x_texte, yy),
                    ha="right", va="center", fontsize=8, color=ENCRE_2,
                    annotation_clip=False)
        ax.annotate(f"{vb:.2f}".replace(".", ","), xy=(x_texte + 0.62, yy),
                    ha="right", va="center", fontsize=8, color=ENCRE_2,
                    annotation_clip=False)

    n_change = int(t["change_de_cote"].sum())
    places = f"{int(t[f'classes_{a}'].sum()):,}".replace(",", " ")
    places_b = f"{int(t[f'classes_{b}'].sum()):,}".replace(",", " ")
    sans = t[t[ra] < 3]
    corr = f"{sans[ra].corr(sans[rb]):+.2f}".replace(".", ",")

    fig.suptitle("Le même diagnostic ? Ratio d'enveloppe de chaque académie,\n"
                 "sous les deux étalons",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.978)
    fig.text(0.02, 0.930,
             f"Pour chaque académie, les places d'éducation prioritaire reçues "
             f"rapportées au nombre de ses collèges figurant parmi les plus bas "
             f"du pays. Les deux\n"
             f"termes étant le même nombre au niveau national — {places} places "
             f"pour l'IPS, {places_b} pour le score de 6ᵉ, trois collèges classés "
             f"n'ayant pas de score —,\n"
             f"le ratio de la France vaut 1 par construction, pour les deux "
             f"étalons. Chaque colonne se lit donc comme une redistribution à "
             f"somme nulle : ce qu'une\n"
             f"académie reçoit au-dessus de 1, une autre le perd.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.118,
             f"En gras et relié d'un trait sombre : les {n_change} académies sur "
             f"{len(t)} qui CHANGENT DE CÔTÉ. Au-dessus et en dessous de 1 ne sont "
             "pas deux nuances d'une même chose,\n"
             "mais deux diagnostics opposés — l'académie paraît sur-dotée selon un "
             f"étalon et sous-dotée selon l'autre. Hors les deux académies au-delà "
             f"de 3, les deux ratios\n"
             f"corrèlent à {corr} : le désaccord n'est pas marginal.\n"
             "L'échelle est logarithmique, le ratio étant multiplicatif : recevoir "
             "deux fois trop et deux fois trop peu sont deux écarts de même ampleur. "
             "Les graduations\n"
             "restent des ratios.\n"
             f"(*) ratio assis sur moins de {SEUIL_FRAGILE} collèges dans l'ensemble "
             "optimal, pour au moins un des deux étalons : un collège de plus ou de "
             "moins le déplacerait fortement.\n"
             "Aucun des deux étalons n'est le critère officiel de classement : un "
             "écart à 1 mesure un désaccord entre deux instruments, pas une erreur de "
             "répartition — et\n"
             "le désaccord entre les deux étalons ne dit pas lequel a raison.\n"
             "Champ : collèges publics, rentrée 2024-2025 / évaluations de septembre "
             "2024. Sources : DEPP (IPS, évaluations nationales de sixième), annuaire "
             "de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "ratios_enveloppe_etalons.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


# Positions candidates d'une etiquette autour de son point, en points
# typographiques, de la plus lisible a la moins. La premiere qui ne heurte rien
# est retenue.
CANDIDATS = [(12, 0), (-12, 0), (12, 13), (-12, 13), (12, -13), (-12, -13),
             (0, 16), (0, -16), (26, 8), (-26, 8), (26, -8), (-26, -8),
             # Portee longue, en dernier recours : la ligne de rappel s'allonge
             # mais l'etiquette reste lisible, ce qui vaut mieux qu'un
             # chevauchement.
             (44, 0), (-44, 0), (44, 20), (-44, 20), (44, -20), (-44, -20),
             (0, 30), (0, -30), (62, 10), (-62, 10)]


def placer_etiquettes(fig, ax, annotations, priorite) -> int:
    """Place chaque etiquette a la premiere position candidate libre.

    POURQUOI PAS UN REPULSEUR ITERATIF

    La premiere version deplacait les etiquettes en conflit par petits pas
    jusqu'a resolution. Elle a diverge : dans un amas dense, les etiquettes se
    repoussent en chaine et deux d'entre elles sont sorties du cadre, reliees a
    leur point par une ligne de rappel traversant toute la figure. Un placement
    par positions candidates est BORNE PAR CONSTRUCTION — une etiquette ne
    s'eloigne jamais de plus de 26 points de son point — et deterministe.

    Les etiquettes sont posees par ordre de PRIORITE decroissante : les grosses
    academies, celles qui pesent dans la redistribution, obtiennent la meilleure
    place, et les petites se contentent de ce qui reste.

    Returns:
        Le nombre d'etiquettes pour lesquelles aucune position n'etait libre.
        Elles restent a droite de leur point et peuvent se chevaucher : mieux
        vaut le savoir que de le decouvrir sur la figure.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    cadre = ax.get_window_extent(renderer=renderer)

    posees, irreductibles = [], 0
    for indice in np.argsort(priorite)[::-1]:
        annotation = annotations[indice]
        for candidat in CANDIDATS:
            annotation.set_position(candidat)
            fig.canvas.draw()
            boite = annotation.get_window_extent(renderer=renderer)
            # `contains` sur un Bbox teste un point : on verifie les deux coins.
            dedans = (cadre.x0 <= boite.x0 and boite.x1 <= cadre.x1
                      and cadre.y0 <= boite.y0 and boite.y1 <= cadre.y1)
            if dedans and not any(boite.overlaps(b) for b in posees):
                posees.append(boite)
                break
        else:
            annotation.set_position(CANDIDATS[0])
            fig.canvas.draw()
            posees.append(annotation.get_window_extent(renderer=renderer))
            irreductibles += 1
    return irreductibles


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
    """
    a, b = list(ETALONS)
    ra, rb = f"ratio_enveloppe_{a}", f"ratio_enveloppe_{b}"

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

    fig, ax = plt.subplots(figsize=(12.8, 13.2))
    fig.subplots_adjust(left=0.075, right=0.978, top=0.878, bottom=0.188)

    borne = (np.log2(0.38), np.log2(6.4))
    ax.plot(borne, borne, color=ENCRE_2, linewidth=1.0, linestyle="--",
            zorder=1)
    ax.annotate("les deux étalons s'accordent", xy=(np.log2(3.1), np.log2(3.1)),
                xytext=(6, -14), textcoords="offset points", fontsize=8,
                color=ENCRE_2, rotation=45, rotation_mode="anchor",
                ha="left", va="center")

    ax.axvline(0.0, color=ENCRE, linewidth=1.1, zorder=2)
    ax.axhline(0.0, color=ENCRE, linewidth=1.1, zorder=2)

    ax.scatter(x, y, s=tailles, c=couleurs, alpha=0.72, linewidths=0.6,
               edgecolors="white", zorder=3)

    annotations = []
    for xi, yi, nom, frag in zip(x, y, t["academie"], t["fragile"]):
        annotations.append(ax.annotate(
            f"{nom.title()}{' *' if frag else ''}", xy=(xi, yi),
            xytext=(11, 0), textcoords="offset points", fontsize=7.5,
            color=ENCRE, va="center", ha="left",
            arrowprops=dict(arrowstyle="-", color=MUET, linewidth=0.5,
                            shrinkA=0, shrinkB=2)))
    restantes = placer_etiquettes(fig, ax, annotations, places)
    if restantes:
        print(f"  {restantes} etiquettes sans position libre : elles se "
              f"chevauchent peut-etre")

    for graduation in (ax.set_xticks, ax.set_yticks):
        graduation([np.log2(g) for g in GRADUATIONS])
    etiquettes = [f"{g:g}".replace(".", ",") for g in GRADUATIONS]
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
    sans = t[t[ra] < 3]
    corr = f"{sans[ra].corr(sans[rb]):+.2f}".replace(".", ",")

    fig.suptitle("Les deux étalons placent-ils les académies au même endroit ?",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.978)
    fig.text(0.02, 0.938,
             "Chaque académie est un point : son ratio d'enveloppe selon l'IPS "
             "en abscisse, selon le score de 6ᵉ en ordonnée. Un point sur la "
             "diagonale signifie\n"
             "que les deux étalons s'accordent exactement ; la distance à la "
             "diagonale mesure leur désaccord. La surface du point est "
             "proportionnelle au nombre\n"
             "de places de l'académie — un ratio de 0,75 sur 118 places ne pèse "
             "pas comme un ratio de 1,40 sur 7 places.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.140,
             f"Les deux droites à 1 découpent le plan en quatre. En bas à gauche "
             f"et en haut à droite, les deux étalons s'accordent sur le sens. "
             f"Dans les deux autres quadrants\n"
             f"ils se contredisent : ce sont les {n_change} académies sur "
             f"{len(t)} qui changent de côté. Hors les deux académies au-delà de "
             f"3 — Corse et Paris, dont le ratio est\n"
             f"identique dans les deux étalons et vaut cinq fois la moyenne — les "
             f"deux ratios corrèlent à {corr} seulement.\n"
             "Les deux échelles sont logarithmiques, le ratio étant "
             "multiplicatif : recevoir deux fois trop et deux fois trop peu sont "
             "deux écarts de même ampleur. Les\n"
             "graduations restent des ratios, et le repère est orthonormé pour que "
             "la diagonale soit bien à 45°.\n"
             f"(*) ratio assis sur moins de {SEUIL_FRAGILE} collèges dans "
             "l'ensemble optimal, pour au moins un des deux étalons : un collège "
             "de plus ou de moins le déplacerait fortement.\n"
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
    figure(t)
    figure_nuage(t)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_TABLES / "ratios_enveloppe_etalons.csv"
    t.to_csv(chemin, index=False, encoding="utf-8")
    print(f"[+] {chemin.name} ({len(t)} academies)")


if __name__ == "__main__":
    main()
