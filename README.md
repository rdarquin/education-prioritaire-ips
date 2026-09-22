# Cartographie des inégalités scolaires en France

> **Statut : en cours de construction.** Les sections marquées 🚧 restent à rédiger.

Analyse territoriale de l'**indice de position sociale (IPS)** des écoles et collèges
français : mesure des disparités, cartographie, et comparaison des secteurs public et
privé sous contrat.

🚧 *À compléter : 3–4 phrases résumant la question posée et le principal résultat.
C'est le paragraphe que les lecteurs liront réellement — à écrire en dernier, une fois
les résultats connus.*

---

## Qu'est-ce que l'IPS ?

🚧 *À compléter. Points à couvrir :*
- *ce que l'indice mesure (construit à partir des professions et catégories
  socioprofessionnelles des parents d'élèves) ;*
- *son mode de calibrage et la valeur de référence nationale ;*
- *ce qu'il ne mesure pas — un IPS n'est pas un indicateur de performance scolaire ;*
- *l'historique de sa publication : ces données n'ont été rendues publiques qu'à la
  suite d'un contentieux administratif. À vérifier et sourcer précisément.*

---

## Données

| Jeu de données | Source | Lignes | Rentrées couvertes |
|---|---|---|---|
| IPS des écoles | data.education.gouv.fr — `fr-en-ips-ecoles-ap2022` | 97 080 | 2022-23, 2023-24, 2024-25 |
| IPS des collèges | data.education.gouv.fr — `fr-en-ips-colleges-ap2023` | 21 061 | 2023-24, 2024-25, 2025-26 |
| Annuaire de l'éducation | data.education.gouv.fr — `fr-en-annuaire-education` | 68 581 | millésime courant |

*Effectifs relevés le 22 septembre 2026.*

**Deux points méthodologiques structurants :**

1. **Les fichiers IPS sont des panels, pas des instantanés.** Malgré leurs
   identifiants (`ap2022`, `ap2023`), chacun couvre trois rentrées scolaires. La
   rentrée la plus récente commune aux deux niveaux est **2024-2025** : c'est la
   référence retenue pour toute comparaison écoles / collèges.

2. **La jointure avec l'annuaire se fait sur le code UAI**, nommé `uai` dans les
   fichiers IPS et `identifiant_de_l_etablissement` dans l'annuaire. L'annuaire
   apporte les coordonnées géographiques (`latitude`, `longitude`), indispensables à
   la cartographie, ainsi que l'appartenance à l'**éducation prioritaire** (REP/REP+)
   — variable de croisement à fort intérêt analytique.

---

## Reproduire l'analyse

```bash
git clone <url-du-depot>
cd ips_inegalites_scolaires
uv sync
uv run python -m src.download
```

`uv sync` installe Python 3.12 et les dépendances aux versions exactes figées dans
`uv.lock`. Aucune donnée n'est versionnée : `src/download.py` reconstruit intégralement
`data/raw/` depuis l'API du ministère.

---

## Structure du dépôt

```
data/raw/          données brutes, en lecture seule, non versionnées
data/processed/    données nettoyées, produites par les scripts
notebooks/         exploration — brouillon, non destiné à la relecture
src/               code réutilisable
outputs/figures/   figures du rapport (versionnées : elles font partie du livrable)
```

---

## Méthode

🚧 *À compléter au fil des étapes : contrôles qualité effectués, traitement des
valeurs manquantes et des établissements non appariés, mesures d'inégalité retenues
(indice de dissimilarité de Duncan, indice de Moran), choix cartographiques.*

## Résultats

🚧 *À compléter.*

## Limites

🚧 *À compléter. Une section « limites » honnête et précise vaut mieux qu'une
conclusion surconfiante — c'est aussi ce qui distingue un travail d'études d'une
infographie.*

---

## Sources

- [IPS des écoles](https://data.education.gouv.fr/explore/dataset/fr-en-ips-ecoles-ap2022/)
- [IPS des collèges](https://data.education.gouv.fr/explore/dataset/fr-en-ips-colleges-ap2023/)
- [Annuaire de l'éducation](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/)

## Auteur

Rémy Darquin
