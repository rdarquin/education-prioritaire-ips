"""Compile le portfolio imprime de quatre pages, de Typst vers PDF.

POURQUOI UN MODULE PLUTOT QU'UNE COMMANDE

Le paquet PyPI `typst` est une BIBLIOTHEQUE, pas la commande en ligne : il
expose `typst.compile` et aucun script `typst`. Son interet est ailleurs —
etant declare dans `pyproject.toml`, sa version est figee dans `uv.lock`
comme le reste de la chaine. Un `uv sync` suffit donc a reproduire le PDF a
l'identique, sans rien installer d'autre.

Pour la mise en page au jour le jour, le binaire officiel reste plus
confortable : `typst watch docs/portfolio.typ` recompile a chaque
sauvegarde. Les deux cohabitent ; ils lisent le meme fichier source.

LA RACINE

Typst refuse de lire un fichier situe hors de sa racine. Le document vit
dans `docs/` et appelle les figures par `../outputs/figures/`, donc la
racine doit etre celle du depot, pas celle du document.
"""

from pathlib import Path

import typst

from src.config import PROJECT_ROOT

# Deux documents, meme contenu, deux registres de lecture. `portfolio` est
# dense — un raisonnement qu'on reconstitue, lu assis. `plaquette` affiche une
# idee par page, lue debout. Tant que le choix n'est pas tranche, les deux se
# compilent ensemble : c'est le seul moyen de les comparer sur piece.
DOCUMENTS = ["portfolio", "plaquette"]


def compiler(nom: str) -> Path:
    """Produit le PDF d'un document et renvoie son chemin."""
    source = PROJECT_ROOT / "docs" / f"{nom}.typ"
    if not source.exists():
        raise FileNotFoundError(f"document absent : {source}")

    sortie = PROJECT_ROOT / "docs" / f"{nom}.pdf"
    typst.compile(source, output=sortie, root=PROJECT_ROOT)
    return sortie


def main() -> None:
    for nom in DOCUMENTS:
        chemin = compiler(nom)
        poids = chemin.stat().st_size / 1024
        print(f"[+] {chemin.relative_to(PROJECT_ROOT)} ({poids:.0f} Ko)")


if __name__ == "__main__":
    main()
