"""Synthese : le classement observe contre celui que l'etalon designerait.

CE QUE LA MATRICE AJOUTE AU RESTE DU PROJET

Tout ce qui precede traite les deux niveaux separement — l'education prioritaire
entiere d'un cote, REP+ de l'autre — et chaque fois en binaire : classe ou non.
Or le dispositif est GRADUE, et un college peut etre mal place de deux manieres
tres differentes : d'un cran, ou de deux. Mettre REP la ou il faudrait REP+
n'est pas la meme chose que ne rien mettre du tout.

La matrice croise les trois niveaux d'un coup et separe ces cas.

CONSTRUCTION, ET POURQUOI LES MARGES COINCIDENT

L'etalon reaffecte les colleges A ENVELOPPES INCHANGEES : les n1 colleges les
plus bas deviennent REP+, les n2 suivants REP, le reste hors education
prioritaire — n1 et n2 etant les effectifs REELLEMENT observes.

Les totaux de ligne egalent donc exactement les totaux de colonne. Ce n'est pas
un classifieur libre qu'on comparerait a une verite : c'est une REALLOCATION
sous la meme contrainte budgetaire. La matrice ne dit pas « l'etalon ferait
mieux », elle dit « a moyens egaux, voici les colleges que les deux
affectations ne placent pas au meme endroit ».

Consequence arithmetique a garder en tete : le nombre de colleges sur-classes
egale necessairement le nombre de sous-classes, cran par cran. Une asymetrie
entre les deux cotes de la diagonale serait un bug, pas un resultat.

POURQUOI UN KAPPA PONDERE

Le taux de concordance brut traite un ecart de deux crans comme un ecart d'un
seul, et il ne corrige pas du hasard : avec 79 % des colleges hors education
prioritaire, une affectation aleatoire respectant les marges tomberait juste
tres souvent. Le kappa pondere lineairement corrige les deux : il rapporte
l'accord observe a l'accord attendu sous independance, en comptant un
desaccord de deux crans pour le double d'un desaccord d'un cran.

Prerequis : `uv run python -m src.preparation`

Lancement (depuis la racine du projet) :
    uv run python -m src.matrices_classement
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import DATA_PROCESSED, FIGURES, PROJECT_ROOT
from src.etalons import ETALONS

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

# L'ordre est celui de l'intensite croissante du dispositif. Il compte : c'est
# lui qui donne un sens a « un cran » et au signe de l'ecart.
NIVEAUX = ["hors EP", "REP", "REP+"]
LIBELLES = ["Non classé", "REP", "REP+"]

BLEU, BLEU_CLAIR = "#1f3b73", "#9ec4ee"
ORANGE, ORANGE_CLAIR = "#eb6834", "#f2a888"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
DIAGONALE, FOND_MARGE = "#eceae2", "#f7f6f2"

# Couleur d'une cellule selon l'ecart, en crans, entre observe et attendu.
# Bleu quand le college est classe PLUS haut que l'etalon ne le placerait,
# orange quand il l'est moins — meme convention que les cartes du projet, ou
# l'orange signale l'oubli.
TEINTES = {0: DIAGONALE, 1: BLEU_CLAIR, 2: BLEU, -1: ORANGE_CLAIR,
           -2: ORANGE}


def matrice(cle: str) -> tuple[pd.DataFrame, dict]:
    """Croise le classement observe et celui que l'etalon designerait."""
    fichier = DATA_PROCESSED / "colleges_2024_2025.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.preparation")

    colonne = ETALONS[cle]["colonne"]
    df = pd.read_csv(fichier)
    df = df[df["secteur"] == "public"].dropna(subset=[colonne])
    df = df.sort_values("uai").reset_index(drop=True)

    n_plus = int((df["ep"] == "REP+").sum())
    n_rep = int((df["ep"] == "REP").sum())

    # `method="first"` departage les ex aequo par l'ordre du tableau, trie par
    # UAI : le choix reste arbitraire mais devient REPRODUCTIBLE.
    rangs = df[colonne].rank(method="first")
    df["attendu"] = np.select(
        [rangs <= n_plus, rangs <= n_plus + n_rep],
        ["REP+", "REP"], default="hors EP")

    m = pd.crosstab(df["attendu"], df["ep"]).reindex(
        index=NIVEAUX, columns=NIVEAUX, fill_value=0)

    # Les marges DOIVENT coincider : l'etalon redistribue la meme enveloppe.
    # On le verifie plutot que de l'affirmer.
    if not (m.sum(axis=1).to_numpy() == m.sum(axis=0).to_numpy()).all():
        raise ValueError(
            "les marges de la matrice different : la reallocation n'a pas "
            "conserve les enveloppes, le calcul est faux.")

    rang = {n: i for i, n in enumerate(NIVEAUX)}
    ecart = df["ep"].map(rang) - df["attendu"].map(rang)

    # Kappa pondere lineairement : un desaccord de deux crans compte double.
    obs = m.to_numpy() / len(df)
    hasard = np.outer(obs.sum(axis=1), obs.sum(axis=0))
    poids = 1 - np.abs(np.subtract.outer(range(3), range(3))) / 2
    po, pe = (poids * obs).sum(), (poids * hasard).sum()

    info = {
        "cle": cle, "etalon": ETALONS[cle], "champ": len(df),
        "n_plus": n_plus, "n_rep": n_rep,
        "diagonale": int(np.trace(m.to_numpy())),
        "kappa": (po - pe) / (1 - pe),
        "ecarts": {v: int((ecart == v).sum()) for v in (-2, -1, 1, 2)},
    }
    return m, info


def matrice_marges(cle: str) -> tuple[pd.DataFrame, dict]:
    """Meme matrice, mais en tenant compte des marges d'interpretabilite.

    LE PRINCIPE

    Les trois niveaux sont separes par DEUX seuils : celui de REP+ et celui de
    l'education prioritaire. Autour de chacun, l'etalon ne tranche pas — trois
    points d'IPS, recommandation du producteur de la donnee ; huit points de
    score de sixieme, soit deux erreurs-types de la moyenne d'un college.

    Un college dont la valeur tombe dans l'une de ces marges a donc PLUSIEURS
    niveaux plausibles, et son classement observe ne peut pas etre contredit
    s'il figure parmi eux. On lui attribue alors son niveau observe.

    La concordance augmente mecaniquement. Ce n'est pas un resultat mais une
    consequence de l'aveu d'imprecision : on cesse de compter comme desaccords
    des cas que l'instrument ne permet pas de trancher. Ce qui RESTE hors
    diagonale, en revanche, est un desaccord que la marge n'explique pas.

    LE CAS DES MARGES QUI SE CHEVAUCHENT

    Les deux seuils sont distants de onze points pour les deux etalons. La
    marge de l'IPS valant trois, les deux zones restent disjointes. Celle du
    score de sixieme valant huit, elles se RECOUVRENT sur cinq points : 375
    colleges s'y trouvent, pour lesquels aucun des trois niveaux ne peut etre
    exclu. C'est une limite propre a cet etalon pour un classement a trois
    niveaux, et la figure la signale.
    """
    fichier = DATA_PROCESSED / "colleges_2024_2025.csv"
    colonne = ETALONS[cle]["colonne"]
    marge = ETALONS[cle]["marge_interpretable"]

    df = pd.read_csv(fichier)
    df = df[df["secteur"] == "public"].dropna(subset=[colonne])
    df = df.sort_values("uai").reset_index(drop=True)

    n_plus = int((df["ep"] == "REP+").sum())
    n_rep = int((df["ep"] == "REP").sum())
    tries = df[colonne].sort_values().to_numpy()
    seuil_plus, seuil_ep = tries[n_plus - 1], tries[n_plus + n_rep - 1]

    valeurs = df[colonne].to_numpy()
    en_marge_plus = np.abs(valeurs - seuil_plus) <= marge
    en_marge_ep = np.abs(valeurs - seuil_ep) <= marge

    rangs = df[colonne].rank(method="first")
    central = np.select([rangs <= n_plus, rangs <= n_plus + n_rep],
                        ["REP+", "REP"], default="hors EP")

    # Niveaux plausibles : le niveau central, plus ceux que la marge rend
    # indiscernables. Un college dans les deux marges a les trois.
    plausibles = [{c} for c in central]
    for i in np.where(en_marge_plus)[0]:
        plausibles[i] |= {"REP+", "REP"}
    for i in np.where(en_marge_ep)[0]:
        plausibles[i] |= {"REP", "hors EP"}

    df["central"] = central
    df["conforme"] = [o in p for o, p in zip(df["ep"], plausibles)]
    # L'attendu devient l'observe quand la marge interdit de le contredire.
    df["attendu"] = np.where(df["conforme"], df["ep"], df["central"])

    m = pd.crosstab(df["attendu"], df["ep"]).reindex(
        index=NIVEAUX, columns=NIVEAUX, fill_value=0)

    # Combien de colleges chaque marge fait-elle basculer sur la diagonale, et
    # dans quelle case ? C'est ce que la figure detaille.
    rattrape = df["conforme"] & (df["central"] != df["ep"])
    apport = {
        niveau: {
            "ep": int((rattrape & en_marge_ep & ~en_marge_plus
                       & (df["ep"] == niveau)).sum()),
            "plus": int((rattrape & en_marge_plus & ~en_marge_ep
                         & (df["ep"] == niveau)).sum()),
            "deux": int((rattrape & en_marge_ep & en_marge_plus
                         & (df["ep"] == niveau)).sum()),
        }
        for niveau in NIVEAUX}

    rang = {n: i for i, n in enumerate(NIVEAUX)}
    ecart = df["ep"].map(rang) - df["attendu"].map(rang)

    obs = m.to_numpy() / len(df)
    hasard = np.outer(obs.sum(axis=1), obs.sum(axis=0))
    poids = 1 - np.abs(np.subtract.outer(range(3), range(3))) / 2
    po, pe = (poids * obs).sum(), (poids * hasard).sum()

    info = {
        "cle": cle, "etalon": ETALONS[cle], "champ": len(df), "marge": marge,
        "n_plus": n_plus, "n_rep": n_rep,
        "seuil_plus": float(seuil_plus), "seuil_ep": float(seuil_ep),
        "diagonale": int(np.trace(m.to_numpy())),
        "kappa": (po - pe) / (1 - pe),
        "ecarts": {v: int((ecart == v).sum()) for v in (-2, -1, 1, 2)},
        "marge_plus": int(en_marge_plus.sum()),
        "marge_ep": int(en_marge_ep.sum()),
        "indecis": int((en_marge_plus & en_marge_ep).sum()),
        "rattrapes": int(rattrape.sum()),
        "apport": apport,
    }
    return m, info


def resumer(m: pd.DataFrame, info: dict) -> None:
    """Affiche la matrice et ses indicateurs."""
    print(f"\n{'=' * 74}")
    print(f"ETALON {info['etalon']['libelle_long'].upper()} — "
          f"{info['champ']} colleges publics")
    print("=" * 74)
    print(f"\n  enveloppes : {info['n_plus']} REP+, {info['n_rep']} REP")
    print("\n  lignes = attendu par l'etalon, colonnes = observe\n")
    print(m.to_string())

    part = 100 * info["diagonale"] / info["champ"]
    print(f"\n  sur la diagonale : {info['diagonale']} ({part:.1f} %)")
    print(f"  kappa pondere    : {info['kappa']:.3f}")
    for valeur, sens in ((2, "sur-classe de DEUX crans"),
                         (1, "sur-classe d'un cran"),
                         (-1, "sous-classe d'un cran"),
                         (-2, "sous-classe de DEUX crans")):
        n = info["ecarts"][valeur]
        print(f"    {sens:<28} {n:>5} ({100 * n / info['champ']:.1f} %)")


def panneau(ax, m: pd.DataFrame, info: dict) -> None:
    """Dessine une matrice 3x3 avec ses marges."""
    valeurs = m.to_numpy()
    total = valeurs.sum()

    ax.set_xlim(-0.75, 4.6)
    ax.set_ylim(3.9, -0.9)  # ordonnee inversee : la premiere ligne en haut
    ax.set_axis_off()

    for i in range(3):          # ligne : attendu
        for j in range(3):      # colonne : observe
            n = int(valeurs[i, j])
            couleur = TEINTES[j - i]
            ax.add_patch(plt.Rectangle((j - 0.46, i - 0.42), 0.92, 0.84,
                                       facecolor=couleur, edgecolor="white",
                                       linewidth=1.5))
            # Texte blanc sur les deux teintes pleines, encre ailleurs.
            sombre = abs(j - i) == 2
            ax.text(j, i - 0.14, f"{n:,}".replace(",", " "), ha="center",
                    va="center", fontsize=15, fontweight="bold",
                    color="white" if sombre else ENCRE)
            ax.text(j, i + 0.13, f"{100 * n / total:.1f} %".replace(".", ","),
                    ha="center", va="center", fontsize=8,
                    color="white" if sombre else ENCRE_2)

    # Marges : totaux de ligne a droite, de colonne en bas. Ils sont egaux deux
    # a deux, et c'est precisement ce que la figure doit laisser verifier.
    for i, n in enumerate(valeurs.sum(axis=1)):
        ax.add_patch(plt.Rectangle((3 - 0.46 + 1, i - 0.42), 0.92, 0.84,
                                   facecolor=FOND_MARGE, edgecolor="white",
                                   linewidth=1.5))
        ax.text(4, i, f"{int(n):,}".replace(",", " "), ha="center",
                va="center", fontsize=11, color=ENCRE_2)
    for j, n in enumerate(valeurs.sum(axis=0)):
        ax.add_patch(plt.Rectangle((j - 0.46, 3 - 0.42), 0.92, 0.84,
                                   facecolor=FOND_MARGE, edgecolor="white",
                                   linewidth=1.5))
        ax.text(j, 3, f"{int(n):,}".replace(",", " "), ha="center",
                va="center", fontsize=11, color=ENCRE_2)

    for j, libelle in enumerate(LIBELLES):
        ax.text(j, -0.75, libelle, ha="center", va="center", fontsize=9.5,
                fontweight="bold", color=ENCRE)
    ax.text(4, -0.75, "Total", ha="center", va="center", fontsize=9,
            color=ENCRE_2)
    for i, libelle in enumerate(LIBELLES):
        ax.text(-0.62, i, libelle, ha="right", va="center", fontsize=9.5,
                fontweight="bold", color=ENCRE)
    ax.text(-0.62, 3, "Total", ha="right", va="center", fontsize=9,
            color=ENCRE_2)

    part = 100 * info["diagonale"] / info["champ"]
    part_txt = f"{part:.1f}".replace(".", ",")
    kappa_txt = f"{info['kappa']:.2f}".replace(".", ",")
    ax.set_title(f"Étalon {info['etalon']['libelle']}\n"
                 f"{part_txt} % sur la diagonale, kappa pondéré {kappa_txt}",
                 fontsize=11.5, fontweight="bold", loc="left", color=ENCRE,
                 pad=14)


def figure(donnees: dict) -> None:
    """Les deux matrices cote a cote."""
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 8.2))
    fig.subplots_adjust(left=0.075, right=0.988, top=0.780, bottom=0.300,
                        wspace=0.22)

    for ax, cle in zip(axes, ETALONS):
        panneau(ax, *donnees[cle])

    fig.text(0.022, 0.545, "ATTENDU\npar l'étalon", fontsize=9.5,
             fontweight="bold", color=ENCRE_2, ha="center", va="center",
             rotation=90, linespacing=1.6)
    for x in (0.275, 0.745):
        fig.text(x, 0.318, "CLASSEMENT OBSERVÉ", fontsize=9.5,
                 fontweight="bold", color=ENCRE_2, ha="center")

    poignees = [
        plt.Rectangle((0, 0), 1, 1, facecolor=DIAGONALE,
                      label="les deux affectations coïncident"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BLEU_CLAIR,
                      label="classé un cran AU-DESSUS de l'attendu"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BLEU,
                      label="classé deux crans au-dessus"),
        plt.Rectangle((0, 0), 1, 1, facecolor=ORANGE_CLAIR,
                      label="classé un cran EN DESSOUS de l'attendu"),
        plt.Rectangle((0, 0), 1, 1, facecolor=ORANGE,
                      label="classé deux crans en dessous"),
    ]
    legende = fig.legend(handles=poignees, loc="upper center",
                         bbox_to_anchor=(0.5, 0.285), ncol=3, fontsize=8.5,
                         frameon=False, handlelength=1.6, handleheight=1.1)
    for texte in legende.get_texts():
        texte.set_color(ENCRE_2)

    ips, eval6 = donnees["ips"][1], donnees["eval6"][1]
    deux_ips = ips["ecarts"][2] + ips["ecarts"][-2]

    fig.suptitle("Le dispositif place-t-il chaque collège au bon niveau ?",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.972)
    fig.text(0.02, 0.922,
             f"Chaque étalon réaffecte les collèges À ENVELOPPES INCHANGÉES : "
             f"les {ips['n_plus']} plus bas deviennent REP+, les "
             f"{ips['n_rep']} suivants REP, le reste hors éducation "
             f"prioritaire.\n"
             f"Les totaux de ligne égalent donc exactement ceux de colonne — ce "
             f"n'est pas un classifieur comparé à une vérité, mais une "
             f"réallocation sous la même contrainte budgétaire.\n"
             f"La matrice ne dit pas que l'étalon ferait mieux : elle dit où les "
             f"deux affectations divergent.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.212,
             f"Trois lectures. La diagonale d'abord : {100 * ips['diagonale'] / ips['champ']:.0f} % "
             f"des collèges au sens de l'IPS, "
             f"{100 * eval6['diagonale'] / eval6['champ']:.0f} % au sens du "
             f"score de 6ᵉ. Mais 79 % des collèges sont hors éducation "
             f"prioritaire, et une affectation\n"
             f"au hasard respectant les marges tomberait souvent juste : le "
             f"kappa pondéré corrige de ce hasard et compte double un désaccord "
             f"de deux crans. Il vaut {ips['kappa']:.2f} et "
             f"{eval6['kappa']:.2f}.\n"
             f"Les coins ensuite — {deux_ips} collèges au sens de l'IPS sont "
             f"mal placés de DEUX crans : {ips['ecarts'][2]} non classés que "
             f"l'IPS mettrait en REP+, {ips['ecarts'][-2]} REP+ qu'il laisserait "
             f"hors du dispositif.\n"
             f"La ligne du milieu enfin : REP est de loin le niveau le moins "
             f"bien identifié — coincé entre deux autres, il reçoit et cède des "
             f"collèges des deux côtés.\n"
             "Symétrie à ne pas lire comme un résultat : les enveloppes étant "
             "conservées, le nombre de collèges sur-classés égale "
             "nécessairement celui des sous-classés, cran par cran.\n"
             "Ni l'IPS ni le score de 6ᵉ n'est le critère officiel de "
             "classement : un écart mesure un désaccord entre deux instruments, "
             "pas une erreur administrative.\n"
             "Champ : collèges publics, rentrée 2024-2025 / évaluations de "
             "septembre 2024. Sources : DEPP (IPS, évaluations nationales de "
             "sixième), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "matrices_classement.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def panneau_marges(ax, m: pd.DataFrame, info: dict) -> None:
    """Matrice tenant compte des marges, avec le detail de leur apport."""
    panneau(ax, m, info)

    # Dans chaque case de la diagonale, le detail de ce que les marges ont
    # fait basculer. Sans lui, le gain serait invisible et la figure paraitrait
    # simplement « meilleure » sans qu'on sache pourquoi.
    #
    # Les libelles sont abreges — EP, R+, 2x — parce que la forme developpee
    # debordait de la case sur la voisine. La legende les developpe.
    for i, niveau in enumerate(NIVEAUX):
        apport = info["apport"][niveau]
        morceaux = [f"{court} {apport[champ]}"
                    for champ, court in (("ep", "EP"), ("plus", "R+"),
                                         ("deux", "2×"))
                    if apport[champ]]
        if morceaux:
            ax.text(i, i + 0.31, "marge · " + " · ".join(morceaux),
                    ha="center", va="center", fontsize=6, color=ENCRE_2,
                    style="italic")


def figure_marges(donnees: dict, reference: dict) -> None:
    """Les deux matrices, marges prises en compte."""
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 9.0))
    fig.subplots_adjust(left=0.075, right=0.988, top=0.772, bottom=0.350,
                        wspace=0.22)

    for ax, cle in zip(axes, ETALONS):
        panneau_marges(ax, *donnees[cle])

    fig.text(0.022, 0.580, "ATTENDU\npar l'étalon", fontsize=9.5,
             fontweight="bold", color=ENCRE_2, ha="center", va="center",
             rotation=90, linespacing=1.6)
    for x in (0.275, 0.745):
        fig.text(x, 0.368, "CLASSEMENT OBSERVÉ", fontsize=9.5,
                 fontweight="bold", color=ENCRE_2, ha="center")

    poignees = [
        plt.Rectangle((0, 0), 1, 1, facecolor=DIAGONALE,
                      label="aucun désaccord, ou désaccord que la marge "
                            "n'autorise pas à trancher"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BLEU_CLAIR,
                      label="classé un cran au-dessus, hors marge"),
        plt.Rectangle((0, 0), 1, 1, facecolor=BLEU,
                      label="deux crans au-dessus"),
        plt.Rectangle((0, 0), 1, 1, facecolor=ORANGE_CLAIR,
                      label="classé un cran en dessous, hors marge"),
        plt.Rectangle((0, 0), 1, 1, facecolor=ORANGE,
                      label="deux crans en dessous"),
    ]
    legende = fig.legend(handles=poignees, loc="upper center",
                         bbox_to_anchor=(0.5, 0.335), ncol=3, fontsize=8.5,
                         frameon=False, handlelength=1.6, handleheight=1.1)
    for texte in legende.get_texts():
        texte.set_color(ENCRE_2)

    ips, eval6 = donnees["ips"][1], donnees["eval6"][1]
    ref_ips, ref_eval6 = reference["ips"][1], reference["eval6"][1]
    gain_ips = 100 * (ips["diagonale"] - ref_ips["diagonale"]) / ips["champ"]
    gain_ev = 100 * (eval6["diagonale"] - ref_eval6["diagonale"]) / eval6["champ"]

    fig.suptitle("Les désaccords que les marges n'expliquent pas",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.974)
    fig.text(0.02, 0.928,
             f"Même matrice que la précédente, mais un collège dont la valeur "
             f"tombe dans la marge d'un seuil ne peut pas être contredit : "
             f"l'étalon n'y tranche pas.\n"
             f"Marge de ±{ips['marge']:g} points pour l'IPS — recommandation de "
             f"la DEPP — et de ±{eval6['marge']:g} pour le score de 6ᵉ, soit "
             f"deux erreurs-types de la moyenne d'un collège.\n"
             f"La concordance monte donc mécaniquement, de "
             f"{gain_ips:+.1f} et {gain_ev:+.1f} points. Ce n'est pas un "
             f"résultat : c'est le prix de l'aveu d'imprécision. Ce qui RESTE "
             f"hors diagonale, en revanche, compte.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.252,
             f"Il subsiste {ips['champ'] - ips['diagonale']} désaccords au sens "
             f"de l'IPS et {eval6['champ'] - eval6['diagonale']} au sens du "
             f"score de 6ᵉ — des collèges dont la valeur est franchement du "
             f"mauvais côté d'un seuil,\n"
             f"au-delà de ce que l'imprécision de l'instrument autorise. Ce sont "
             f"les seuls cas sur lesquels le projet se prononce.\n"
             f"Les deux seuils sont distants de 11 points pour les deux "
             f"étalons. La marge de l'IPS valant 3, les deux zones restent "
             f"disjointes. Celle du score de 6ᵉ valant 8, elles se RECOUVRENT :\n"
             f"{eval6['indecis']} collèges s'y trouvent, pour lesquels aucun des "
             f"trois niveaux ne peut être exclu. C'est une limite propre à cet "
             f"étalon dès qu'on classe à trois niveaux.\n"
             f"Sous chaque case de la diagonale, le détail de ce que les marges "
             f"ont fait basculer, par seuil : EP pour celui de l'éducation "
             f"prioritaire, R+ pour celui de REP+, 2× pour les collèges situés "
             f"dans les deux.\n"
             f"Les totaux de ligne ne coïncident plus avec ceux de colonne, à la "
             f"différence de la matrice précédente : un collège de la marge "
             f"prend son niveau observé, ce qui déplace les effectifs attendus. "
             f"Les colonnes,\n"
             f"elles, restent les enveloppes réelles. Les marges ne sortent "
             f"jamais un collège de la diagonale, elles ne font que l'y amener.\n"
             "Ni l'IPS ni le score de 6ᵉ n'est le critère officiel de "
             "classement : un écart mesure un désaccord entre deux instruments, "
             "pas une erreur administrative.\n"
             "Champ : collèges publics, rentrée 2024-2025 / évaluations de "
             "septembre 2024. Sources : DEPP (IPS, évaluations nationales de "
             "sixième), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    chemin = FIGURES / "matrices_classement_marges.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"[+] {chemin.name}")


def main() -> None:
    donnees, avec_marges = {}, {}
    for cle in ETALONS:
        m, info = matrice(cle)
        resumer(m, info)
        donnees[cle] = (m, info)

        m2, info2 = matrice_marges(cle)
        print(f"\n  --- marges d'interprétabilité (±{info2['marge']:g}) ---")
        print(f"    marge REP+ : {info2['marge_plus']} colleges, "
              f"marge EP : {info2['marge_ep']}, les deux : {info2['indecis']}")
        print(f"    {info2['rattrapes']} colleges reclasses conformes")
        print(f"    diagonale : {info2['diagonale']} "
              f"({100 * info2['diagonale'] / info2['champ']:.1f} %), "
              f"kappa {info2['kappa']:.3f}")
        avec_marges[cle] = (m2, info2)

    figure(donnees)
    figure_marges(avec_marges, donnees)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    for cle in ETALONS:
        for suffixe, (m, _) in (("", donnees[cle]),
                                ("_marges", avec_marges[cle])):
            chemin = DOSSIER_TABLES / f"matrice_classement_{cle}{suffixe}.csv"
            m.to_csv(chemin, encoding="utf-8")
            print(f"[+] {chemin.name}")


if __name__ == "__main__":
    main()
