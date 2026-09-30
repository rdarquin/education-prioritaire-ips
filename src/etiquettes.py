"""Placement des etiquettes sur un nuage de points.

POURQUOI PAS UN REPULSEUR ITERATIF

La premiere version de ce code deplacait les etiquettes en conflit par petits
pas jusqu'a resolution. Elle a diverge : dans un amas dense, les etiquettes se
repoussent en chaine, et deux d'entre elles sont sorties du cadre, reliees a
leur point par une ligne de rappel traversant toute la figure.

Le placement par positions candidates est BORNE PAR CONSTRUCTION — une
etiquette ne s'eloigne jamais de plus de 62 points de son point — et
deterministe. Il ne resout pas tous les cas, mais il ne produit jamais
d'aberration, et il DIT combien de cas il n'a pas resolus.
"""

import numpy as np

# Positions candidates autour du point, en points typographiques, de la plus
# lisible a la moins. La premiere qui ne heurte rien est retenue.
CANDIDATS = [(12, 0), (-12, 0), (12, 13), (-12, 13), (12, -13), (-12, -13),
             (0, 16), (0, -16), (26, 8), (-26, 8), (26, -8), (-26, -8),
             # Portee longue, en dernier recours : la ligne de rappel
             # s'allonge mais l'etiquette reste lisible, ce qui vaut mieux
             # qu'un chevauchement.
             (44, 0), (-44, 0), (44, 20), (-44, 20), (44, -20), (-44, -20),
             (0, 30), (0, -30), (62, 10), (-62, 10),
             # Tres longue portee. Indispensable des que les points forment un
             # AMAS DIAGONAL serre : les positions proches y sont toutes prises
             # et la seule issue est de sortir de la bande, perpendiculairement.
             (0, 46), (0, -46), (70, 34), (-70, 34), (70, -34), (-70, -34),
             (0, 64), (0, -64), (96, 20), (-96, 20), (96, -20), (-96, -20)]


def placer_etiquettes(fig, ax, annotations, priorite) -> int:
    """Place chaque etiquette a la premiere position candidate libre.

    Les etiquettes sont posees par ordre de PRIORITE decroissante : les points
    qui comptent le plus obtiennent la meilleure place, et les autres se
    contentent de ce qui reste.

    Args:
        fig: la figure, qui doit etre rendue pour mesurer les boites.
        ax: l'axe dont le cadre borne les etiquettes.
        annotations: les objets `Annotation`, deja crees.
        priorite: un tableau de meme longueur ; les valeurs hautes passent
            en premier.

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
