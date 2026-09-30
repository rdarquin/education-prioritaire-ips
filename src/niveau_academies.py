"""Le niveau des eleves a l'entree en sixieme, rapporte a l'IPS de l'academie.

LA QUESTION

Les deux etalons du projet — l'IPS et le score aux evaluations de sixieme —
mesurent deux choses : un milieu social et un niveau scolaire. Ils sont
fortement lies au niveau du college, mais cela ne dit rien de leur relation
AGREGEE. Cette figure la trace : un point par academie, son IPS moyen en
abscisse, son score moyen en ordonnee.

CE QU'ELLE REND VISIBLE

La droite d'ajustement donne le niveau qu'un IPS donne laisse attendre. Un
point au-dessus signifie que les eleves de l'academie arrivent en sixieme avec
un niveau superieur a ce que leur milieu social laisse prevoir ; un point en
dessous, l'inverse.

Ces ecarts ne sont pas du bruit : ils atteignent plusieurs points de score, la
ou l'ecart-type entre academies n'en fait qu'une dizaine. Deux academies
ultramarines s'en detachent nettement.

CE QU'ELLE N'EXPLIQUE PAS

Un ecart a la droite peut tenir a l'ecole primaire, a la composition sociale
mal captee par l'IPS dans certains contextes, a la langue parlee a la maison, a
la scolarisation anterieure. L'evaluation ayant lieu en SEPTEMBRE, a l'entree
en sixieme, elle ne mesure en revanche RIEN de ce que le college produit : ces
ecarts ne sont pas imputables aux colleges.

POURQUOI DES AXES LINEAIRES

L'IPS et le score de sixieme sont des echelles d'intervalle, pas des rapports :
un IPS de 120 n'est pas "deux fois" un IPS de 60. Le logarithme, utile aux
ratios d'enveloppe, n'aurait ici aucun sens.

POURQUOI LA MOYENNE DES COLLEGES ET NON DES ELEVES

Chaque point est la moyenne non ponderee des colleges publics de l'academie.
Ponderer par les effectifs donnerait la moyenne des ELEVES, qui est une autre
grandeur : elle ferait peser Lille et Creteil sur la position de leur academie
au detriment de leurs petits colleges. La question posee ici portant sur les
etablissements, c'est leur moyenne qu'on retient — et le libelle de chaque axe
le dit.

Prerequis : `uv run python -m src.preparation`

Lancement (depuis la racine du projet) :
    uv run python -m src.niveau_academies
"""

import matplotlib

matplotlib.use("Agg")  # backend sans fenetre : on ecrit des fichiers

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import DATA_PROCESSED, FIGURES, PROJECT_ROOT
from src.etiquettes import placer_etiquettes

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE = "#1f3b73", "#eb6834"
BLEU_CLAIR, ORANGE_CLAIR = "#9ec4ee", "#f2a888"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

# Au-dela de cet ecart a la droite d'ajustement, exprime en ecarts-types des
# residus, une academie est nommee comme atypique dans la note. Deux suffisent
# a la commenter sans alourdir la figure.
SEUIL_ATYPIQUE = 1.5

# En dessous de cet IPS moyen, une academie sort du cadre ET de l'ajustement.
# Deux sont concernees a ce jour, Mayotte (71,9) et la Guyane (77,8), tres
# loin de la plus basse des autres — La Reunion, a 84,9. Les garder etirait
# l'echelle sur une plage de quinze points d'IPS que personne n'occupe et
# tassait les vingt-huit autres dans le coin superieur droit.
#
# Elles sortent aussi de l'AJUSTEMENT, et ce n'est pas une commodite. Elles
# portaient a elles seules toute la courbure : sans elles, le gain d'un
# ajustement quadratique sur un ajustement lineaire tombe de +0,080 a +0,009 de
# R2. Les retirer du cadre en gardant la courbe afficherait une courbure
# justifiee par des points invisibles.
SEUIL_IPS_CADRE = 82.0


def charger() -> pd.DataFrame:
    """Moyennes academiques d'IPS et de score de sixieme, colleges publics."""
    fichier = DATA_PROCESSED / "colleges_2024_2025.csv"
    if not fichier.exists():
        raise FileNotFoundError(
            f"{fichier.name} absent. Lance d'abord : uv run python -m src.preparation")

    df = pd.read_csv(fichier)
    pub = df[df["secteur"] == "public"]

    aca = pub.groupby("academie").agg(
        colleges=("uai", "size"),
        ips_moyen=("ips", "mean"),
        eval6_moyen=("eval6", "mean"),
        classes_ep=("ep", lambda s: (s != "hors EP").sum()),
        eval6_manquant=("eval6", lambda s: s.isna().sum()),
    ).reset_index()
    aca["part_ep"] = 100 * aca["classes_ep"] / aca["colleges"]

    manquants = int(aca["eval6_manquant"].sum())
    if manquants:
        print(f"  {manquants} colleges sans score de sixieme, exclus des "
              f"moyennes de l'ordonnee")
    return aca


def ajuster(aca: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Ajuste le score sur l'IPS et calcule le residu de chaque academie.

    POURQUOI UNE DROITE, ET SUR VINGT-HUIT ACADEMIES

    L'ajustement porte sur les academies CADREES, Mayotte et la Guyane en etant
    exclues (voir `SEUIL_IPS_CADRE`). Ce choix decide de la forme :

      - sur les trente, un ajustement quadratique gagnait +0,080 de R2 sur une
        droite (0,837 -> 0,917), et la courbure etait franche ;
      - sur les vingt-huit, il ne gagne plus que +0,009 (0,686 -> 0,695).

    Autrement dit, la courbure etait portee par ces deux points a elle seule.
    Une fois qu'ils sortent du cadre, la droite s'impose : ajuster une courbe
    dont la forme depend de points qu'on ne montre pas serait indefendable.

    Le prix a payer est explicite : le R2 passe de 0,92 a 0,69. Ce n'est pas
    une perte de qualite mais un changement de question. Les trente academies
    couvrent une plage d'IPS de quarante-quatre points, ou n'importe quelle
    relation parait forte ; les vingt-huit n'en couvrent que vingt-quatre, et
    la relation y est reellement plus lache.

    Le residu reste la grandeur interessante — c'est lui qui dit qu'une
    academie sort du rang.
    """
    aca = aca.copy()
    aca["dans_cadre"] = aca["ips_moyen"] >= SEUIL_IPS_CADRE
    cadrees = aca[aca["dans_cadre"]]
    x, y = cadrees["ips_moyen"].to_numpy(), cadrees["eval6_moyen"].to_numpy()

    coefficients = np.polyfit(x, y, 1)
    aca["attendu"] = np.polyval(coefficients, aca["ips_moyen"])
    aca["residu"] = aca["eval6_moyen"] - aca["attendu"]

    # R2 et ecart-type des residus sur les seules academies ajustees : les
    # inclure fausserait les deux, l'ajustement ne les ayant pas vues.
    residus = aca.loc[aca["dans_cadre"], "residu"]
    total = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (residus ** 2).sum() / total
    quad = np.polyfit(x, y, 2)
    r2_quad = 1 - ((y - np.polyval(quad, x)) ** 2).sum() / total

    ajustement = {
        "coefficients": coefficients, "r2": r2, "r2_quad": r2_quad,
        "sigma": residus.std(), "n": len(cadrees),
    }
    # Le caractere atypique n'a de sens que pour les academies ajustees : pour
    # les autres, le residu serait une extrapolation loin hors du domaine.
    aca["atypique"] = (aca["dans_cadre"]
                       & (aca["residu"].abs()
                          > SEUIL_ATYPIQUE * ajustement["sigma"]))
    return aca, ajustement


def resumer(aca: pd.DataFrame, ajustement: dict) -> None:
    """Affiche l'ajustement et les academies qui s'en ecartent."""
    hors = aca[~aca["dans_cadre"]]
    print(f"\n{'=' * 78}")
    print("NIVEAU A L'ENTREE EN SIXIEME ET IPS, PAR ACADEMIE")
    print("=" * 78)
    print(f"\n  {len(aca)} academies, dont {ajustement['n']} ajustees")
    print(f"  hors cadre (IPS moyen < {SEUIL_IPS_CADRE:g}) : "
          f"{', '.join(hors['academie'])}")
    pente, ordonnee = ajustement["coefficients"]
    print(f"\n  score = {ordonnee:.1f} + {pente:.3f} x IPS")
    print(f"  R2 {ajustement['r2']:.3f}  (un ajustement quadratique : "
          f"{ajustement['r2_quad']:.3f}, soit "
          f"{ajustement['r2_quad'] - ajustement['r2']:+.3f})")
    print(f"  ecart-type des residus : {ajustement['sigma']:.2f} points de score")
    print(f"\n  un point d'IPS de plus correspond a {pente:.2f} point de "
          f"score de plus")

    vue = ["academie", "colleges", "ips_moyen", "eval6_moyen", "attendu",
           "residu"]
    tri = aca[aca["dans_cadre"]].sort_values("residu")
    print("\n  les plus BAS au regard de leur IPS :")
    print(tri.head(5)[vue].round(1).to_string(index=False))
    print("\n  les plus HAUTS :")
    print(tri.tail(5)[vue].round(1).to_string(index=False))
    print("\n  les deux exclues, pour memoire :")
    print(hors[["academie", "colleges", "ips_moyen", "eval6_moyen"]]
          .round(1).to_string(index=False))


def figure(aca: pd.DataFrame, ajustement: dict) -> None:
    """Nuage IPS moyen x score moyen, une academie par point.

    Mayotte et la Guyane sont hors cadre — elles etiraient l'echelle sur une
    plage de quinze points d'IPS que personne n'occupe — mais nommees dans une
    note encadree, avec leurs valeurs et une fleche vers le coin ou elles se
    trouvent. Les omettre en silence serait malhonnete.
    """
    cadrees, hors = aca[aca["dans_cadre"]], aca[~aca["dans_cadre"]]
    x = cadrees["ips_moyen"].to_numpy()
    y = cadrees["eval6_moyen"].to_numpy()
    colleges = cadrees["colleges"].to_numpy()

    # La SURFACE porte le nombre de colleges : c'est l'aire que l'oeil compare,
    # d'ou la racine carree. Une academie de 430 colleges et une de 22 ne
    # pesent pas pareil dans la moyenne nationale.
    tailles = 20 + 380 * np.sqrt(colleges / colleges.max())

    # La couleur porte le SIGNE et l'ampleur du residu : orange au-dessus de
    # l'attendu, bleu en dessous, gris au voisinage de la droite. C'est la
    # seule information que la position seule ne donne pas d'un coup d'oeil.
    sigma = ajustement["sigma"]
    reduit = cadrees["residu"] / sigma
    couleurs = np.select(
        [reduit < -SEUIL_ATYPIQUE, reduit < -0.5, reduit > SEUIL_ATYPIQUE,
         reduit > 0.5],
        [BLEU, BLEU_CLAIR, ORANGE, ORANGE_CLAIR], default=MUET)

    # Large et peu haute : le nuage est etire le long de la diagonale, et
    # c'est l'etalement HORIZONTAL qui desserre l'amas central.
    fig, ax = plt.subplots(figsize=(14.5, 11.8))
    fig.subplots_adjust(left=0.065, right=0.982, top=0.872, bottom=0.198)

    # Droite d'ajustement, tracee sur l'etendue des academies AJUSTEES et non
    # sur tout l'axe : la prolonger vers Mayotte et la Guyane suggererait une
    # validite hors du domaine ou elle a ete estimee.
    bornes_x = np.array([x.min(), x.max()])
    ax.plot(bornes_x, np.polyval(ajustement["coefficients"], bornes_x),
            color=ENCRE_2, linewidth=1.1, linestyle="--", zorder=1)

    ax.scatter(x, y, s=tailles, c=couleurs, alpha=0.78, linewidths=0.6,
               edgecolors="white", zorder=3)

    # Un encart de zoom a ete essaye sur l'amas central, puis retire : les deux
    # variables correlant a +0,92, l'amas occupe une part telle du nuage que le
    # rectangle de zoom en couvrait presque toute la moitie haute, et l'encart
    # lui-meme recouvrait Paris et Versailles. Il aggravait le probleme qu'il
    # devait resoudre. On garde donc un nuage simple, quitte a ce que quelques
    # etiquettes du centre restent serrees — le module le signale, et le
    # fichier CSV porte les valeurs exactes.
    annotations = []
    for xi, yi, nom in zip(x, y, cadrees["academie"]):
        annotations.append(ax.annotate(
            nom.title(), xy=(xi, yi), xytext=(11, 0),
            textcoords="offset points", fontsize=7, color=ENCRE,
            va="center", ha="left",
            arrowprops=dict(arrowstyle="-", color=MUET, linewidth=0.5,
                            shrinkA=0, shrinkB=2)))
    restantes = placer_etiquettes(fig, ax, annotations, colleges)
    if restantes:
        print(f"  {restantes} etiquettes sans position libre : elles se "
              f"chevauchent peut-etre")

    # ---- les academies hors cadre, signalees et non tues -------------------
    if len(hors):
        lignes = [
            f"{nom.title()} : IPS {ips:.0f}, score {score:.0f}"
            for nom, ips, score in zip(hors["academie"], hors["ips_moyen"],
                                       hors["eval6_moyen"])]
        # La fleche part de la note vers le coin inferieur gauche, ou les deux
        # academies se trouveraient. On ne donne PAS leur ecart a la droite :
        # ce serait une extrapolation a plus de dix points d'IPS hors du
        # domaine ou elle a ete estimee.
        ax.annotate("↙ Hors cadre\n" + "\n".join(lignes),
                    xy=(0.0, 0.0), xycoords="axes fraction",
                    xytext=(26, 26), textcoords="offset points",
                    fontsize=8, color=ENCRE_2, ha="left", va="bottom",
                    linespacing=1.5,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="white",
                              edgecolor=GRILLE, linewidth=0.6))

    ax.set_xlabel("IPS moyen des collèges publics de l'académie", fontsize=10,
                  labelpad=6)
    ax.set_ylabel("Score moyen aux évaluations de début de 6ᵉ", fontsize=10,
                  labelpad=6)
    ax.grid(True, linewidth=0.5, color=GRILLE)
    ax.set_axisbelow(True)
    for bord in ["top", "right"]:
        ax.spines[bord].set_visible(False)
    ax.tick_params(labelsize=8.5)

    poignees = [
        plt.Line2D([], [], marker="o", linestyle="", markersize=8,
                   markerfacecolor=ORANGE, markeredgecolor="white",
                   label="nettement au-dessus du niveau attendu"),
        plt.Line2D([], [], marker="o", linestyle="", markersize=8,
                   markerfacecolor=MUET, markeredgecolor="white",
                   label="proche du niveau attendu"),
        plt.Line2D([], [], marker="o", linestyle="", markersize=8,
                   markerfacecolor=BLEU, markeredgecolor="white",
                   label="nettement en dessous du niveau attendu"),
    ]
    premiere = ax.legend(handles=poignees, loc="upper left", fontsize=8.5,
                         frameon=True, framealpha=0.96, edgecolor=GRILLE,
                         title="Écart à la droite d'ajustement",
                         title_fontsize=8.5)
    premiere.get_frame().set_linewidth(0.6)
    ax.add_artist(premiere)

    reperes = [30, 150, 430]
    poignees_taille = [
        plt.Line2D([], [], marker="o", linestyle="", markeredgecolor=MUET,
                   markerfacecolor="white",
                   markersize=np.sqrt(20 + 380 * np.sqrt(n / colleges.max())) / 2,
                   label=f"{n} collèges")
        for n in reperes]
    seconde = ax.legend(handles=poignees_taille, loc="lower right",
                        fontsize=8.5, frameon=True,
                        framealpha=0.96, edgecolor=GRILLE, labelspacing=1.6,
                        title="Taille de l'académie", title_fontsize=8.5,
                        borderpad=1.0)
    seconde.get_frame().set_linewidth(0.6)

    # Les nombres du texte sont formates AVANT d'entrer dans la chaine : une
    # substitution de virgule appliquee a un bloc de litteraux adjacents
    # toucherait aussi les points de fin de phrase.
    r2_txt = f"{ajustement['r2']:.2f}".replace(".", ",")
    gain_txt = f"{ajustement['r2_quad'] - ajustement['r2']:+.3f}".replace(
        ".", ",")
    pente_txt = f"{ajustement['coefficients'][0]:.2f}".replace(".", ",")
    sigma_txt = f"{ajustement['sigma']:.1f}".replace(".", ",")
    noms_hors = " et ".join(nom.title() for nom in hors["academie"])

    atypiques = aca[aca["atypique"]].sort_values("residu")
    noms = ", ".join(
        f"{a.title()} ({r:+.0f})" for a, r in
        zip(atypiques["academie"], atypiques["residu"])) or "aucune"

    fig.suptitle("Le niveau à l'entrée en 6ᵉ suit-il l'IPS de l'académie ?",
                 fontsize=14, fontweight="bold", x=0.02, ha="left", y=0.978)
    fig.text(0.02, 0.938,
             f"Une académie par point : l'IPS moyen de ses collèges publics en "
             f"abscisse, leur score moyen aux évaluations nationales de début de "
             f"6ᵉ en ordonnée.\n"
             f"La droite donne le score qu'un IPS donné laisse attendre : "
             f"R² = {r2_txt}. Un point d'IPS de plus correspond à {pente_txt} "
             f"point de score de plus.\n"
             f"{noms_hors} sont hors cadre : leur IPS moyen est inférieur de "
             f"plus de sept points à celui de la plus basse des "
             f"{ajustement['n']} autres, et les garder étirait l'échelle sur "
             f"une plage\n"
             f"que personne n'occupe. Elles sont aussi exclues de "
             f"l'ajustement, faute de quoi la droite serait estimée sur des "
             f"points que la figure ne montre pas.",
             fontsize=9, va="top", color=ENCRE_2)

    fig.text(0.02, 0.152,
             f"L'écart à la droite est la grandeur intéressante : il dit si les "
             f"élèves d'une académie arrivent en 6ᵉ au-dessus ou en dessous de "
             f"ce que leur milieu social\n"
             f"laisse prévoir. L'écart-type de ces écarts vaut {sigma_txt} points "
             f"de score. Académies s'en écartant de plus de "
             f"{SEUIL_ATYPIQUE:g} écarts-types : {noms}.\n"
             f"Sur les trente académies, un ajustement courbe s'imposait — la "
             f"relation s'aplatissant dans le haut. Sans {noms_hors}, qui "
             f"portaient à elles seules cette courbure, il ne gagne plus que\n"
             f"{gain_txt} de R² : la droite suffit. Aucun écart n'est calculé "
             f"pour les deux exclues, ce qui demanderait d'extrapoler la droite "
             f"loin hors de son domaine.\n"
             "L'évaluation a lieu en SEPTEMBRE, à l'entrée en sixième : elle ne "
             "mesure rien de ce que le collège produit, et ces écarts ne lui sont "
             "donc pas imputables.\n"
             "Ils peuvent tenir à l'école primaire, à la langue parlée à la "
             "maison, à la scolarisation antérieure, ou à un IPS qui capte mal "
             "certains contextes — cette figure ne tranche pas.\n"
             "Chaque point est la moyenne non pondérée des collèges de "
             "l'académie, et non celle de ses élèves : la question posée porte "
             "sur les établissements.\n"
             "Les axes sont linéaires, l'IPS et le score étant des échelles "
             "d'intervalle et non des rapports.\n"
             "Champ : collèges publics, rentrée 2024-2025 / évaluations de "
             "septembre 2024. Sources : DEPP (IPS, évaluations nationales de "
             "sixième), annuaire de l'éducation.",
             fontsize=7.5, va="top", color=ENCRE_2)

    FIGURES.mkdir(parents=True, exist_ok=True)
    chemin = FIGURES / "niveau_ips_academies.png"
    fig.savefig(chemin, dpi=200, facecolor="white")
    plt.close(fig)
    print(f"\n[+] {chemin.name}")


def main() -> None:
    aca = charger()
    aca, ajustement = ajuster(aca)
    resumer(aca, ajustement)
    figure(aca, ajustement)

    DOSSIER_TABLES.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_TABLES / "niveau_ips_academies.csv"
    aca.round(3).to_csv(chemin, index=False, encoding="utf-8")
    print(f"[+] {chemin.name} ({len(aca)} academies)")


if __name__ == "__main__":
    main()
