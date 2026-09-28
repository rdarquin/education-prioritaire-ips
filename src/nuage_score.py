"""Nuage de points des deux variables cartographiees dans `cartographie_score`.

En abscisse la FREQUENCE des ecarts significatifs (part des etablissements du
departement dont le score depasse 3 points d'IPS), en ordonnee leur NATURE
(score signe moyen de ces seuls etablissements, positif pour un oubli, negatif
pour une sur-inclusion). Un point par departement.

LA STRUCTURE A CONNAITRE AVANT DE LIRE

Chaque etablissement compte dans l'ordonnee pese au moins 3 points d'IPS en
valeur absolue, par construction du filtre. Il s'ensuit que :

    un departement dont tous les ecarts significatifs sont des oublis
    a necessairement y >= +3 ;

    un departement qui ne sur-inclut que a necessairement y <= -3 ;

    la bande -3 < y < +3 n'est donc atteignable QU'EN MELANGEANT les deux
    types d'erreur, et suppose au moins deux etablissements significatifs.

Un departement proche de zero n'a donc pas "peu d'ecart" : il en a autant dans
les deux sens. C'est le contresens que ce graphique doit empecher, et c'est
pourquoi les deux bornes a +/- 3 sont tracees et la bande ombree.

POURQUOI LA TAILLE CODE LES EFFECTIFS SIGNIFICATIFS

L'ordonnee est une moyenne calculee sur les seuls etablissements significatifs.
Sa fiabilite depend donc de leur NOMBRE, pas du nombre total d'etablissements
du departement. Les points sont dimensionnes en consequence : un departement
qui n'a qu'un seul etablissement significatif apparait minuscule, et sa
position forcee hors de la bande centrale se lit comme telle.

CE QUE LE GRAPHIQUE AJOUTE AUX CARTES

Les cartes montrent OU. Le nuage montre comment frequence et nature se
combinent : un departement qui s'ecarte souvent mais sans direction et un
departement qui s'ecarte rarement mais toujours dans le meme sens y occupent
des positions opposees, alors qu'aucune des deux cartes prise seule ne permet
de les distinguer.

Prerequis : `uv run python -m src.cartographie_score`

Lancement (depuis la racine du projet) :
    uv run python -m src.nuage_score
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.cartographie_score import (MIN_ETABLISSEMENTS, NIVEAUX,
                                    SEUIL_SIGNIFICATIF)
from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE = "#1f3b73", "#eb6834"
GRILLE, MUET, ENCRE_2 = "#e1e0d9", "#898781", "#52514e"

# Nombre de departements etiquetes par panneau. Au-dela, les etiquettes se
# recouvrent et le graphique devient moins lisible qu'un tableau.
N_ETIQUETTES = 4

# Decalages verticaux successifs essayes pour une etiquette, en pourcentage de
# la hauteur du graphique. Le premier qui n'entre en conflit avec aucune
# etiquette deja posee est retenu.
DECALAGES = [0.0, 4.5, -4.5, 9.0, -9.0, 13.5, -13.5]


def charger(radical: str) -> pd.DataFrame:
    """Charge un tableau departemental et ajoute la distinction territoriale."""
    fichier = DOSSIER_TABLES / f"score_ecart_par_departement_{radical}.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : "
            f"uv run python -m src.cartographie_score")

    dep = pd.read_csv(fichier, dtype={"code_departement": str})
    dep["zone"] = np.where(
        dep["code_departement"].str.startswith(("97", "98")), "outre-mer", "métropole")
    return dep


def verifier_structure(dep: pd.DataFrame) -> None:
    """Controle qu'un departement a un seul ecart significatif sort de la bande.

    C'est une consequence necessaire de la definition : avec un unique
    etablissement retenu, la moyenne EST son score, donc superieure a 3 en
    valeur absolue. Si la verification echoue, l'agregation melange des
    etablissements qui n'auraient pas du etre retenus.
    """
    seuls = dep[dep["significatifs"] == 1]
    fautifs = seuls[seuls["score_moyen_significatifs"].abs() <= SEUIL_SIGNIFICATIF]
    if len(fautifs):
        raise ValueError(
            f"{len(fautifs)} departements n'ont qu'un ecart significatif mais une "
            f"moyenne inferieure a {SEUIL_SIGNIFICATIF} en valeur absolue : "
            f"le filtre a 3 points est mal applique.")


def tailles(valeurs, reference: pd.Series) -> np.ndarray:
    """Surface des points, proportionnelle au nombre d'etablissements retenus.

    L'echelle est TOUJOURS calculee sur `reference`, c'est-a-dire l'ensemble
    du panneau, jamais sur le sous-groupe trace. Sans cette precaution, les
    points d'outre-mer seraient normalises entre eux et un departement a
    9 etablissements significatifs apparaitrait aussi gros qu'un departement
    qui en compte 19.
    """
    etendue = reference.max() - reference.min()
    return 20 + 300 * (np.asarray(valeurs) - reference.min()) / etendue


def etiqueter(ax, dep: pd.DataFrame, xmax: float, ymax: float) -> None:
    """Nomme les departements les plus remarquables, sans chevauchement.

    Sont retenus les plus fortes frequences et les natures les plus tranchees
    dans les deux sens.
    """
    remarquables = pd.concat([
        dep.nlargest(N_ETIQUETTES, "part_significatifs"),
        dep.nlargest(3, "score_moyen_significatifs"),
        dep.nsmallest(3, "score_moyen_significatifs"),
    ]).drop_duplicates("code_departement").sort_values("part_significatifs",
                                                       ascending=False)

    hauteur = 2 * ymax
    posees: list[tuple[float, float]] = []

    for _, r in remarquables.iterrows():
        x, y = r["part_significatifs"], r["score_moyen_significatifs"]
        for decalage in DECALAGES:
            candidat = y + decalage / 100 * hauteur
            conflit = any(abs(x - px) < 0.22 * xmax
                          and abs(candidat - py) < 0.045 * hauteur
                          for px, py in posees)
            if not conflit:
                break
        posees.append((x, candidat))

        # Position du texte en coordonnees de donnees : c'est le seul moyen de
        # decaler d'une fraction connue du graphique. Un filet relie
        # l'etiquette a son point des qu'elle est deplacee.
        a_droite = x < 0.62 * xmax
        ecart_x = 0.025 * xmax
        ax.annotate(
            r["departement"].title(),
            xy=(x, y),
            xytext=(x + ecart_x if a_droite else x - ecart_x, candidat),
            textcoords="data",
            ha="left" if a_droite else "right", va="center",
            fontsize=7.2, color=ENCRE_2, zorder=4,
            arrowprops=dict(arrowstyle="-", color=MUET, linewidth=0.5,
                            shrinkA=0, shrinkB=3)
            if decalage else None)


def panneau(ax, dep: pd.DataFrame, pluriel: str, titre: str) -> None:
    """Trace le nuage d'un niveau sur un axe."""
    # Marge droite volontairement large : les trois annotations de bande sont
    # calees sur le bord droit, et aucun departement ne doit pouvoir s'y
    # trouver, sinon son etiquette les percute.
    xmax = dep["part_significatifs"].max() * 1.34
    ymax = dep["score_moyen_significatifs"].abs().max() * 1.10

    # ---- la bande interdite aux departements unilateraux ------------------
    ax.axhspan(-SEUIL_SIGNIFICATIF, SEUIL_SIGNIFICATIF, color=GRILLE,
               alpha=0.55, linewidth=0, zorder=0)
    for borne in (-SEUIL_SIGNIFICATIF, SEUIL_SIGNIFICATIF):
        ax.axhline(borne, color=MUET, linewidth=0.9, linestyle="--", zorder=1)
    ax.axhline(0, color=MUET, linewidth=0.9, zorder=1)

    ax.annotate("oublis seuls", xy=(xmax * 0.985, SEUIL_SIGNIFICATIF),
                xytext=(0, 7), textcoords="offset points", ha="right",
                va="bottom", fontsize=7, color=MUET, style="italic")
    ax.annotate("sur-inclusions seules", xy=(xmax * 0.985, -SEUIL_SIGNIFICATIF),
                xytext=(0, -7), textcoords="offset points", ha="right",
                va="top", fontsize=7, color=MUET, style="italic")
    ax.annotate("les deux types mêlés", xy=(xmax * 0.985, 0),
                xytext=(0, 4), textcoords="offset points", ha="right",
                va="bottom", fontsize=7, color=MUET, style="italic")

    # ---- les departements ------------------------------------------------
    # La taille est calculee une fois pour tout le panneau, puis decoupee par
    # zone : les deux groupes partagent ainsi la meme echelle.
    surfaces = pd.Series(tailles(dep["significatifs"], dep["significatifs"]),
                         index=dep.index)

    for zone, couleur in [("métropole", BLEU), ("outre-mer", ORANGE)]:
        sous = dep[dep["zone"] == zone]
        if sous.empty:
            continue
        ax.scatter(sous["part_significatifs"], sous["score_moyen_significatifs"],
                   s=surfaces[sous.index], c=couleur, alpha=0.65, linewidth=0.5,
                   edgecolor="white", label=f"{zone} ({len(sous)})", zorder=3)

    etiqueter(ax, dep, xmax, ymax)

    ax.set_xlim(0, xmax)
    ax.set_ylim(-ymax, ymax)
    ax.set_xlabel(f"Fréquence — part des {pluriel} dont l'écart dépasse "
                  f"{SEUIL_SIGNIFICATIF:.0f} points d'IPS (%)", fontsize=9)
    ax.set_ylabel("Nature — score signé moyen de ces seuls établissements\n"
                  "← sur-inclusion          oubli →", fontsize=9)
    ax.set_title(titre, fontsize=11, fontweight="bold", loc="left")
    ax.legend(loc="lower right", frameon=False, fontsize=8)
    ax.grid(True, linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)


def legende_taille(ax, dep: pd.DataFrame, pluriel: str) -> None:
    """Ajoute une legende expliquant la taille des points."""
    reperes = sorted({int(dep["significatifs"].min()),
                      int(dep["significatifs"].median()),
                      int(dep["significatifs"].max())})
    proxies = [ax.scatter([], [], s=t, c=MUET, alpha=0.6, linewidth=0.5,
                          edgecolor="white", label=f"{v}")
               for v, t in zip(reperes, tailles(reperes, dep["significatifs"]))]
    seconde = ax.legend(handles=proxies, loc="upper right", frameon=False,
                        fontsize=7.5, labelspacing=1.2, handletextpad=1.2,
                        title=f"{pluriel} au-delà de 3 pts", title_fontsize=7.5)
    ax.add_artist(seconde)


def main() -> None:
    # Panneaux hauts : la zone utile est etroite en ordonnee autour de la
    # bande centrale, et c'est la que se concentrent les departements.
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 10.2))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.875, bottom=0.135,
                        wspace=0.26)

    for ax, (niveau, radical, pluriel, titre_champ) in zip(axes, NIVEAUX):
        dep = charger(radical)
        verifier_structure(dep)

        # Une frequence n'a de sens que sur un effectif suffisant, et une
        # nature suppose au moins un etablissement retenu.
        dep = dep[(dep["etablissements"] >= MIN_ETABLISSEMENTS[niveau])
                  & (dep["significatifs"] >= 1)]

        panneau(ax, dep, pluriel, f"{titre_champ} ({len(dep)} départements)")
        legende_taille(ax, dep, pluriel.capitalize())

        dans_bande = (dep["score_moyen_significatifs"].abs()
                      < SEUIL_SIGNIFICATIF).sum()
        correlation = dep["part_significatifs"].corr(
            dep["score_moyen_significatifs"])
        print(f"{niveau:8s} : {len(dep)} departements traces | "
              f"{dans_bande} dans la bande centrale | "
              f"correlation frequence/nature {correlation:+.3f}")

    fig.suptitle(
        "Écarts significatifs à une allocation fondée sur l'IPS : "
        "fréquence et nature, par département",
        fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.978)
    fig.text(0.02, 0.949,
             "Chaque point est un département ; les deux variables sont celles des deux "
             "cartes. Chaque établissement compté pèse au moins 3 points d'IPS signés, "
             "donc un département dont tous\n"
             "les écarts significatifs vont dans le même sens tombe forcément hors de "
             "la bande grisée. S'y trouver ne veut pas dire « peu d'écart », mais "
             "« autant dans les deux sens ».",
             fontsize=8.5, va="top", color=ENCRE_2)

    fig.text(0.02, 0.092,
             "Lecture : vers la droite, le département s'écarte souvent ; vers le haut, "
             "ses écarts sont des oublis d'établissements défavorisés ; vers le bas, des "
             "classements d'établissements\n"
             "qui ne sont pas les plus défavorisés. La taille du point est le nombre "
             "d'établissements au-delà de 3 points, dont dépend la fiabilité de "
             "l'ordonnée : un point minuscule n'a qu'un seul\n"
             "établissement derrière lui, et sa position hors de la bande est alors "
             "imposée par la définition, non observée.\n"
             "Champ : établissements publics, rentrée 2024-2025. Les départements "
             "comptant moins de 20 collèges ou 50 écoles, ou aucun écart significatif, "
             "sont exclus.\n"
             "L'IPS n'est pas le critère officiel de classement : un écart mesure un "
             "désaccord entre deux instruments, pas une erreur administrative.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "nuage_frequence_nature.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


if __name__ == "__main__":
    main()
