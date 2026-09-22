# Éducation prioritaire et réalité sociale des établissements

> **Statut : en cours de construction.** Les sections marquées 🚧 restent à rédiger.

**Le classement en éducation prioritaire coïncide-t-il avec la réalité sociale des
établissements, mesurée par l'indice de position sociale (IPS) ? Et là où les deux
divergent, que nous apprennent ces exceptions ?**

Ce travail confronte deux mesures du même phénomène : d'un côté le classement
administratif en REP et REP+, de l'autre l'IPS publié par la DEPP pour chaque école
et chaque collège. Il quantifie leur recouvrement, identifie les établissements
socialement défavorisés situés hors du dispositif, et cartographie leur répartition
territoriale.

🚧 *À compléter en fin de projet : 2–3 phrases donnant le principal résultat chiffré.*

---

## Cadrage préalable

Un premier examen des données écarte d'emblée la question naïve — « le ciblage
est-il correct ? ». Rentrée 2024-2025 :

| Statut | Écoles | IPS moyen | Collèges | IPS moyen |
|---|---:|---:|---:|---:|
| REP+ | 1 300 | **77,2** | 362 | **74,6** |
| REP | 2 317 | **85,7** | 732 | **86,0** |
| Hors dispositif | 26 147 | **107,9** | 5 880 | **109,2** |

L'écart entre REP+ et hors dispositif atteint **30 points pour les écoles et 35 pour
les collèges**, quand la DEPP recommande de ne pas interpréter des différences de
3 points ou moins. Le ciblage est donc globalement très cohérent avec la réalité
sociale mesurée par l'IPS.

L'intérêt de l'analyse se déplace par conséquent vers les **divergences** : quels
établissements socialement défavorisés restent hors dispositif, où se situent-ils,
et ces exceptions dessinent-elles une géographie particulière — rural, villes
moyennes, outre-mer ?

*Chiffres provisoires issus d'une passe exploratoire, à consolider une fois le
pipeline de nettoyage écrit.*

---

## Précautions méthodologiques

**1. Le classement en éducation prioritaire ne repose pas sur l'IPS.** Il s'appuie
sur d'autres critères sociaux. Un écart entre les deux ne constitue donc pas une
erreur de l'administration — c'est la confrontation de deux instruments de mesure,
dont l'analyse des divergences est précisément l'objet de ce travail.

**2. L'éducation prioritaire est organisée en réseaux, non en établissements
isolés.** Un réseau associe un collège aux écoles dont les élèves y sont orientés,
et c'est l'ensemble du réseau qui est classé. Le label d'une école découle donc de
celui de son collège de secteur. Une école socialement favorisée peut être classée
REP parce qu'elle alimente un collège défavorisé : ce n'est pas une anomalie de
ciblage, c'est la conception du dispositif.

Les données confirment cette organisation de deux façons : **aucun lycée** ne porte
de label (0 sur 5 600), et l'on compte **environ six écoles labellisées par collège
labellisé** (6 552 pour 1 104), soit l'ordre de grandeur d'un secteur de recrutement.
Le lien école → collège n'étant pas présent dans les fichiers utilisés, cette
structure est cohérente avec les données sans être démontrée par elles ; la liste
officielle des réseaux serait nécessaire pour la confirmer.

Cette organisation n'altère toutefois pas la lisibilité des résultats : l'écart
d'IPS entre établissements classés et non classés est de même ampleur pour les
écoles (−22 points en REP, −31 en REP+) que pour les collèges (−23 et −35). Le
classement des écoles suit donc leur propre réalité sociale presque aussi
étroitement que celui des collèges.

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
