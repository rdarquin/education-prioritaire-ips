"""Cartographie departementale des ecarts SIGNIFICATIFS au seuil budgetaire.

Produit, pour chaque niveau, une figure a deux cartes :

    FREQUENCE - part des etablissements du departement dont le score d'ecart
                depasse 3 points d'IPS. Echelle sequentielle : une frequence
                n'a pas de polarite, seulement une intensite.

    NATURE    - parmi ces seuls etablissements, moyenne du score SIGNE
                (positif pour un oubli, negatif pour une sur-inclusion).
                Echelle divergente centree sur zero, avec un gris neutre au
                milieu : ici le signe est l'information.

POURQUOI 3 POINTS

La DEPP recommande de ne pas interpreter des differences d'IPS de 3 points ou
moins : en deca, l'ecart est en dessous de la resolution de l'indicateur.
Filtrer a 3 points evite donc de compter comme "ecart" ce qui n'est que du
bruit de mesure. C'est le seul seuil du calcul, et il ne vient pas d'un choix
statistique mais du producteur de la donnee.

Consequence a garder en tete pour lire la seconde carte : chaque etablissement
retenu contribue pour au moins 3 points en valeur absolue. Un departement dont
tous les ecarts significatifs sont des oublis a donc une moyenne >= +3, et un
departement qui ne sur-inclut que, une moyenne <= -3. Une valeur proche de
zero ne signifie pas "peu d'ecart" mais "les deux types se compensent".

LES DEUX CARTES SONT COMPLEMENTAIRES

Un departement peut avoir peu d'ecarts significatifs mais tres unilateraux, ou
beaucoup d'ecarts qui s'annulent. La premiere carte donne la frequence, la
seconde la nature. Aucune des deux ne se deduit de l'autre.

POURQUOI DES CLASSES DE QUANTILES ET NON UNE RAMPE CONTINUE

La distribution des valeurs departementales est tres asymetrique : quelques
departements valent plusieurs fois la mediane. Une echelle lineaire leur donne
toute la dynamique de couleur et ecrase les quatre-vingt-dix autres dans une
teinte indistincte. Les bornes de classes sont donc prises sur les quantiles
de la distribution observee. Elles sont affichees sur la barre de couleur :
le lecteur voit l'echelle qu'on lui applique.

Le fond de carte, le repositionnement des DROM et leur annotation sont repris
de `cartographie.py` : meme convention, donc meme avertissement. CES CARTES NE
PERMETTENT AUCUNE MESURE DE DISTANCE NI DE SURFACE.

Prerequis : `uv run python -m src.score_ecart` (produit score_ecart_ips.csv)

Lancement (depuis la racine du projet) :
    uv run python -m src.cartographie_score
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

from src.cartographie import annoter_drom, charger_contours
from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Seuil d'interpretabilite de l'IPS, recommande par la DEPP. En dessous, une
# difference n'est pas lisible : on ne la compte pas comme un ecart.
SEUIL_SIGNIFICATIF = 3.0

# Effectif minimal d'etablissements pour qu'une part departementale ait un
# sens : en dessous, un seul etablissement deplacerait la part de plusieurs
# points. Les departements concernes sont laisses en gris.
MIN_ETABLISSEMENTS = {"college": 20, "ecole": 50}

# Effectif minimal d'etablissements SIGNIFICATIFS pour que leur moyenne ait un
# sens. Avec un ou deux etablissements, la seconde carte afficherait le score
# d'un etablissement isole en le faisant passer pour une caracteristique du
# departement.
MIN_SIGNIFICATIFS = 3

# niveau interne, radical ASCII pour les fichiers, pluriel affiche, titre
NIVEAUX = [
    ("college", "colleges", "collèges", "Collèges publics"),
    ("ecole", "ecoles", "écoles", "Écoles publiques"),
]

GRIS_ABSENT = "#e3e3e3"
N_CLASSES = 6

# Palette divergente construite sur les couleurs du projet, avec un GRIS
# neutre au centre. Les palettes divergentes standard de matplotlib passent
# par un blanc quasi invisible sur fond clair : un departement equilibre y
# disparaitrait au lieu de se lire comme neutre.
DIVERGENTE = LinearSegmentedColormap.from_list(
    "solde", ["#2a78d6", "#9ec4ee", "#d8d7d0", "#f2a888", "#eb6834"])


def agreger(scores: pd.DataFrame, niveau: str) -> pd.DataFrame:
    """Resume le score individuel a l'echelle departementale.

    Returns:
        Un tableau par departement. Les colonnes `score_moyen` et `solde`
        sont conservees pour `nuage_score.py` ; les cartes utilisent
        `part_significatifs` et `score_moyen_significatifs`.
    """
    sous = scores[scores["niveau"] == niveau].copy()

    # Score signe : positif pour un oubli, negatif pour une sur-inclusion.
    # C'est ce signe qui rend la seconde carte lisible.
    sous["score_signe"] = np.select(
        [sous["type_ecart"] == "oublie", sous["type_ecart"] == "sur-inclus"],
        [sous["score_ecart_ips"], -sous["score_ecart_ips"]],
        default=0.0)

    significatif = sous["score_ecart_ips"] > SEUIL_SIGNIFICATIF
    sous["est_significatif"] = significatif
    sous["score_signe_significatif"] = sous["score_signe"].where(significatif, 0.0)
    sous["masse_oublis"] = sous["score_ecart_ips"].where(
        sous["type_ecart"] == "oublie", 0.0)
    sous["masse_sur_inclusions"] = sous["score_ecart_ips"].where(
        sous["type_ecart"] == "sur-inclus", 0.0)

    dep = sous.groupby(["code_departement", "departement"]).agg(
        etablissements=("uai", "size"),
        classes=("ep", lambda s: (s != "hors EP").sum()),
        en_ecart=("score_ecart_ips", lambda s: (s > 0).sum()),
        significatifs=("est_significatif", "sum"),
        somme_signee_significative=("score_signe_significatif", "sum"),
        score_total=("score_ecart_ips", "sum"),
        masse_oublis=("masse_oublis", "sum"),
        masse_sur_inclusions=("masse_sur_inclusions", "sum"),
    ).reset_index()

    # Les deux variables cartographiees.
    dep["part_significatifs"] = 100 * dep["significatifs"] / dep["etablissements"]
    dep["score_moyen_significatifs"] = (dep["somme_signee_significative"]
                                        / dep["significatifs"].replace(0, np.nan))

    # Conservees pour le nuage de points, qui croise ces deux-la.
    dep["score_moyen"] = dep["score_total"] / dep["etablissements"]
    dep["solde"] = ((dep["masse_oublis"] - dep["masse_sur_inclusions"])
                    / dep["etablissements"])
    return dep


def classes_sequentielles(valeurs: np.ndarray, n: int = N_CLASSES) -> np.ndarray:
    """Bornes de classes prises sur les quantiles, pour une grandeur positive."""
    bornes = np.quantile(valeurs, np.linspace(0, 1, n + 1))
    return np.unique(np.round(bornes, 2))


def classes_divergentes(valeurs: np.ndarray) -> np.ndarray:
    """Bornes symetriques autour de zero, pour une grandeur signee.

    Les bornes interieures sont prises sur les quantiles de la VALEUR ABSOLUE,
    puis reflechies de part et d'autre de zero. La symetrie est indispensable :
    sans elle, le gris neutre de la palette ne tomberait pas sur l'equilibre
    et la carte mentirait sur le signe.
    """
    absolus = np.abs(valeurs)
    interieures = np.quantile(absolus, [0.30, 0.60, 0.85])
    extreme = absolus.max()
    bornes = np.concatenate([[-extreme], -interieures[::-1], [0.0],
                             interieures, [extreme]])
    return np.unique(np.round(bornes, 2))


def carte(ax, gdf, colonne: str, fiable, cmap, norme, contours) -> None:
    """Trace une choroplethe sur un axe, en grisant les valeurs non fiables."""
    gdf.plot(ax=ax, color=GRIS_ABSENT, edgecolor="white", linewidth=0.4)
    gdf[fiable].plot(ax=ax, column=colonne, cmap=cmap, norm=norme,
                     edgecolor="white", linewidth=0.4)
    annoter_drom(ax, contours)
    ax.set_axis_off()


def barre(fig, position, cmap, norme, bornes, etiquette: str) -> None:
    """Place une barre de couleur horizontale, graduee sur les bornes de classes."""
    echelle = plt.cm.ScalarMappable(cmap=cmap, norm=norme)
    cax = fig.add_axes(position)
    fig.colorbar(echelle, cax=cax, orientation="horizontal",
                 ticks=bornes, spacing="uniform")
    cax.set_xticklabels([f"{b:.1f}" for b in bornes], fontsize=6.5)
    cax.set_xlabel(etiquette, fontsize=8, labelpad=4)


def figure_niveau(dep: pd.DataFrame, contours, niveau: str, radical: str,
                  pluriel: str, titre_champ: str) -> None:
    """Produit la figure a deux cartes pour un niveau."""
    gdf = contours.join(dep.set_index("code_departement"), how="left")
    mini = MIN_ETABLISSEMENTS[niveau]

    assez_grand = gdf["etablissements"].fillna(0) >= mini
    assez_significatifs = gdf["significatifs"].fillna(0) >= MIN_SIGNIFICATIFS
    fiable_nature = assez_grand & assez_significatifs

    n_masques = int((~assez_grand).sum())
    n_sans_nature = int((assez_grand & ~assez_significatifs).sum())

    fig, axes = plt.subplots(1, 2, figsize=(13, 8.8))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.855, bottom=0.235,
                        wspace=0.02)

    # ---- frequence : echelle sequentielle --------------------------------
    valeurs = gdf.loc[assez_grand, "part_significatifs"].to_numpy()
    bornes = classes_sequentielles(valeurs)
    cmap = matplotlib.colormaps["Oranges"].resampled(len(bornes) - 1)
    norme = BoundaryNorm(bornes, ncolors=len(bornes) - 1)

    carte(axes[0], gdf, "part_significatifs", assez_grand, cmap, norme, contours)
    axes[0].set_title("Fréquence des écarts significatifs", fontsize=11.5,
                      fontweight="bold", loc="left")
    barre(fig, [0.07, 0.185, 0.36, 0.014], cmap, norme, bornes,
          f"Part des {pluriel} dont l'écart dépasse "
          f"{SEUIL_SIGNIFICATIF:.0f} points d'IPS (%)")

    # ---- nature : echelle divergente symetrique --------------------------
    valeurs = gdf.loc[fiable_nature, "score_moyen_significatifs"].to_numpy()
    bornes = classes_divergentes(valeurs)
    cmap = DIVERGENTE.resampled(len(bornes) - 1)
    norme = BoundaryNorm(bornes, ncolors=len(bornes) - 1)

    carte(axes[1], gdf, "score_moyen_significatifs", fiable_nature, cmap,
          norme, contours)
    axes[1].set_title("Nature de ces écarts", fontsize=11.5,
                      fontweight="bold", loc="left")
    barre(fig, [0.57, 0.185, 0.36, 0.014], cmap, norme, bornes,
          "← sur-inclusion     score signé moyen, en points d'IPS     oubli →")

    fig.suptitle(
        f"Éducation prioritaire : écarts significatifs à une allocation fondée "
        f"sur l'IPS\n{titre_champ}, rentrée 2024-2025",
        fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)

    fig.text(0.02, 0.128,
             "Le score d'un établissement vaut 0 s'il est classé et sous le seuil "
             "budgétaire, ou non classé et au-dessus ; sinon il vaut son écart d'IPS à "
             "ce seuil. Ne sont retenus ici que les\n"
             f"écarts supérieurs à {SEUIL_SIGNIFICATIF:.0f} points, la DEPP "
             "recommandant de ne pas interpréter des différences d'IPS inférieures. "
             "À gauche, leur fréquence ; à droite, leur nature.\n"
             "Chaque établissement retenu pèse au moins 3 points en valeur absolue : "
             "une moyenne proche de zéro signifie donc que les deux types se "
             "compensent, non qu'il y a peu d'écart.\n"
             "Les classes sont des quantiles de la distribution départementale, et non "
             "une échelle linéaire : quelques départements extrêmes écraseraient "
             "sinon tous les autres.\n"
             f"En gris : {n_masques} départements comptant moins de {mini} "
             f"{pluriel} publics ou sans donnée ; sur la carte de droite, "
             f"{n_sans_nature} de plus comptant moins de {MIN_SIGNIFICATIFS} "
             "établissements significatifs.\n"
             "L'IPS n'est pas le critère officiel de classement : un écart mesure un "
             "désaccord entre deux instruments, pas une erreur administrative.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation, contours Insee/cartiflette. "
             "DROM rapprochés, échelles et distances non respectées.",
             fontsize=7.5, va="top", color="#52514e")

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / f"ecarts_significatifs_{radical}.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"  [+] {chemin.name}")


def main() -> None:
    fichier = DOSSIER_TABLES / "score_ecart_ips.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.score_ecart")

    scores = pd.read_csv(fichier, dtype={"code_departement": str,
                                         "code_commune": str})

    print("Contours :")
    contours = charger_contours("FRANCE_ENTIERE_DROM_RAPPROCHES")
    print(f"  {len(contours)} departements")

    print("\nFigures :")
    for niveau, radical, pluriel, titre_champ in NIVEAUX:
        dep = agreger(scores, niveau)
        figure_niveau(dep, contours, niveau, radical, pluriel, titre_champ)

        dep.round(3).to_csv(
            DOSSIER_TABLES / f"score_ecart_par_departement_{radical}.csv",
            index=False, encoding="utf-8")

        mini = MIN_ETABLISSEMENTS[niveau]
        assez = dep[dep["etablissements"] >= mini]
        colonnes = ["code_departement", "departement", "etablissements",
                    "significatifs", "part_significatifs",
                    "score_moyen_significatifs"]

        total_sig = int(dep["significatifs"].sum())
        print(f"\n--- {niveau.upper()}S : {total_sig} etablissements a ecart "
              f"significatif sur {len(scores[scores.niveau == niveau])} "
              f"({100 * total_sig / len(scores[scores.niveau == niveau]):.1f} %) ---")
        print(f"  {len(assez)} departements retenus (>= {mini} etablissements)")
        print("\n  part la plus elevee :")
        print(assez.nlargest(8, "part_significatifs")[colonnes].round(2)
              .to_string(index=False))
        nature = assez[assez["significatifs"] >= MIN_SIGNIFICATIFS]
        print("\n  ecarts significatifs les plus orientes vers l'OUBLI :")
        print(nature.nlargest(5, "score_moyen_significatifs")[colonnes].round(2)
              .to_string(index=False))
        print("\n  ecarts significatifs les plus orientes vers la SUR-INCLUSION :")
        print(nature.nsmallest(5, "score_moyen_significatifs")[colonnes].round(2)
              .to_string(index=False))


if __name__ == "__main__":
    main()
