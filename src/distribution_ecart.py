"""Forme de la distribution de l'ecart d'IPS au seuil budgetaire.

La variable est a INFLATION DE ZEROS : neuf colleges sur dix sont conformes et
valent exactement 0. Une distribution brute serait donc un pic unique entoure
de barres invisibles. Deux precautions la rendent lisible sans rien dissimuler :

    - la barre du zero est TRONQUEE, et son effectif reel annote ;
    - les classes sont calees pour que zero tombe AU CENTRE d'une barre. Sans
      cela, les conformes se repartiraient sur deux barres voisines et la masse
      centrale apparaitrait deux fois plus petite qu'elle n'est.

Le score est affiche SIGNE : negatif pour une sur-inclusion, positif pour un
oubli. La couleur reprend la convention du projet — bleu pour les
sur-inclusions, orange pour les oublis — l'axe portant deja le signe, le
redoublement est ici voulu : il relie la figure aux cartes.

Les deux variantes de seuil sont superposees, aplat pour le seuil national et
trait pour le seuil academique. La comparaison montre ou le changement d'etalon
agit : sur la queue, non sur le centre.

Prerequis : `uv run python -m src.score_ecart`

Lancement (depuis la racine du projet) :
    uv run python -m src.distribution_ecart
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURES, PROJECT_ROOT

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# Seuil d'interpretabilite de l'IPS recommande par la DEPP. Sert ici de repere
# visuel, pas de filtre : la figure montre toute la distribution.
SEUIL_INTERPRETABLE = 3.0

# Largeur de classe, en points d'IPS.
PAS = 1.0

BLEU, ORANGE = "#1f3b73", "#eb6834"
ENCRE, GRILLE, MUET, ENCRE_2 = "#0b0b0b", "#e1e0d9", "#898781", "#52514e"

VARIANTES = [("score_ecart_ips", "type_ecart", "national"),
             ("score_ecart_academie", "type_ecart_academie", "académique")]


def charger() -> pd.DataFrame:
    """Lit le fichier des scores, produit par `score_ecart.py`."""
    fichier = DOSSIER_TABLES / "score_ecart_ips.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.score_ecart")
    return pd.read_csv(fichier)


def signer(df: pd.DataFrame, col_score: str, col_type: str) -> np.ndarray:
    """Score signe : positif pour un oubli, negatif pour une sur-inclusion.

    Le score brut est une valeur absolue ; c'est la colonne de type qui porte
    le sens de l'ecart. Les reunir en une seule variable signee permet de
    tracer les deux cotes sur un meme axe.
    """
    return np.select(
        [df[col_type] == "oublie", df[col_type] == "sur-inclus"],
        [df[col_score], -df[col_score]], default=0.0)


def resumer(df: pd.DataFrame) -> None:
    """Affiche la composition de la distribution, par variante."""
    print(f"\n{'=' * 84}")
    print(f"DISTRIBUTION DE L'ECART D'IPS — {len(df)} colleges publics")
    print("=" * 84)

    for col_score, _, libelle in VARIANTES:
        s = df[col_score]
        nul = int((s == 0).sum())
        petit = int(((s > 0) & (s <= SEUIL_INTERPRETABLE)).sum())
        grand = int((s > SEUIL_INTERPRETABLE).sum())
        non_nuls = s[s > 0]
        q = non_nuls.quantile([0.5, 0.75, 0.9, 0.99]).round(2)
        print(f"\n  seuil {libelle:11s} : nul {nul:>5} "
              f"({100 * nul / len(df):>4.1f} %) | "
              f"0-{SEUIL_INTERPRETABLE:.0f} pts {petit:>5} "
              f"({100 * petit / len(df):>4.1f} %) | "
              f">{SEUIL_INTERPRETABLE:.0f} pts {grand:>5} "
              f"({100 * grand / len(df):>4.1f} %)")
        print(f"  {'':18s}   non nuls : med {q[0.5]:>5.2f}  Q3 {q[0.75]:>5.2f}  "
              f"D9 {q[0.9]:>5.2f}  C99 {q[0.99]:>5.2f}  max {non_nuls.max():>5.1f}")


def figure(df: pd.DataFrame) -> None:
    """Produit l'histogramme de l'ecart signe."""
    national = signer(df, "score_ecart_ips", "type_ecart")
    academique = signer(df, "score_ecart_academie", "type_ecart_academie")

    borne = max(np.abs(national).max(), np.abs(academique).max())
    # Bornes decalees d'un demi-pas pour que zero tombe au centre d'une classe.
    bins = np.arange(-borne - PAS, borne + 2 * PAS, PAS) - PAS / 2

    fig, ax = plt.subplots(figsize=(10, 6.8))
    fig.subplots_adjust(left=0.085, right=0.975, top=0.80, bottom=0.265)

    ax.hist(national[national < 0], bins=bins, color=BLEU, alpha=0.8,
            linewidth=0, label="Sur-inclusions (seuil national)")
    ax.hist(national[national > 0], bins=bins, color=ORANGE, alpha=0.8,
            linewidth=0, label="Oublis (seuil national)")
    ax.hist(academique, bins=bins, histtype="step", color=ENCRE, linewidth=1.1,
            label="Seuil académique")

    # Plafond cale sur la plus haute barre NON nulle : la barre du zero est
    # tronquee, sans quoi elle ecraserait tout le reste.
    hors_zero = national[national != 0]
    plafond = np.histogram(hors_zero, bins=bins)[0].max() * 1.35
    ax.set_ylim(0, plafond)

    n_nuls = int((national == 0).sum())
    ax.bar(0, plafond, width=PAS * 0.9, color=MUET, alpha=0.35, linewidth=0,
           zorder=0)
    ax.annotate(f"{n_nuls:,}".replace(",", " ") + " conformes\n"
                f"({100 * n_nuls / len(df):.1f} %)\nbarre tronquée",
                xy=(0, plafond), xytext=(6, -6), textcoords="offset points",
                ha="left", va="top", fontsize=7.5, color=ENCRE_2)

    for borne_seuil in (-SEUIL_INTERPRETABLE, SEUIL_INTERPRETABLE):
        ax.axvline(borne_seuil, color=MUET, linewidth=0.9, linestyle="--")

    ax.set_xlabel("Écart d'IPS au seuil budgétaire\n"
                  "← sur-inclusion          conforme          oubli →",
                  fontsize=9)
    ax.set_ylabel("Nombre de collèges", fontsize=9)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.grid(True, linewidth=0.4, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)

    fig.suptitle("Distribution de l'écart d'IPS au seuil budgétaire",
                 fontsize=13.5, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.945,
             "Neuf collèges sur dix sont conformes et valent exactement zéro : la "
             "barre centrale est tronquée pour que le reste de la\n"
             "distribution reste lisible, son effectif étant annoté. Les pointillés "
             f"marquent ± {SEUIL_INTERPRETABLE:.0f} points, seuil en deçà duquel la "
             "DEPP\nrecommande de ne pas interpréter une différence d'IPS.",
             fontsize=8.5, va="top", color=ENCRE_2)
    fig.text(0.02, 0.125,
             "Lecture : le seuil budgétaire est l'IPS du collège qui ferme "
             "l'enveloppe réellement allouée — 88,80 points au niveau national.\n"
             "Le trait noir donne la même distribution lorsque le seuil est recalculé "
             "académie par académie : la distribution se resserre,\n"
             "mais sur la queue plutôt que sur le centre.\n"
             "Champ : collèges publics, rentrée 2024-2025. L'IPS n'est pas le critère "
             "officiel de classement : un écart mesure un\n"
             "désaccord entre deux instruments, pas une erreur administrative.\n"
             "Sources : DEPP (IPS), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "distribution_ecart.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def main() -> None:
    df = charger()
    resumer(df)
    figure(df)


if __name__ == "__main__":
    main()
