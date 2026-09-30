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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.analyse import charger, restreindre_au_public
from src.config import FIGURES, PROJECT_ROOT
from src.etalons import ETALONS
from src.score_ecart import ajouter_score, controler_identite

DOSSIER_TABLES = PROJECT_ROOT / "outputs" / "tables"

BLEU, ORANGE, ORANGE_CLAIR = "#1f3b73", "#eb6834", "#f2a888"
ENCRE, ENCRE_2, MUET, GRILLE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

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


def main() -> None:
    donnees = {}
    for cle in ETALONS:
        df, info = preparer(cle)
        resumer(df, info)
        donnees[cle] = (df, info)

    figure(donnees)

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
