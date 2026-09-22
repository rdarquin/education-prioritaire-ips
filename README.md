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

*Chiffres produits par `src/preparation.py` sur 36 738 établissements retenus
(29 764 écoles, 6 974 collèges) après exclusion des établissements non appariés à
l'annuaire et de ceux dont l'IPS n'est pas publié. Voir « Méthode » pour le détail
des exclusions.*

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

### Construction du fichier d'analyse

`src/preparation.py` part des trois fichiers bruts et produit
`data/processed/etablissements_2024_2025.csv` : une ligne par établissement.

| Étape | Effet |
|---|---:|
| Fichiers IPS bruts (3 rentrées) | 118 141 lignes |
| Filtrage sur la rentrée 2024-2025 | 39 481 |
| Exclusion des non-appariés à l'annuaire | −307 |
| Exclusion des IPS non publiés | −2 505 |
| **Retenus** (chevauchement de 69 lignes) | **36 738** |

Les 36 738 établissements retenus disposent tous de coordonnées géographiques.

### Contrôles effectués

**Doublons de l'annuaire.** 75 UAI y figurent en double. Avant d'en conserver
arbitrairement la première occurrence, on vérifie que les lignes concernées ne se
contredisent pas : **aucune divergence** sur les coordonnées ni sur le statut
d'éducation prioritaire. Le choix est donc sans conséquence. La jointure est par
ailleurs déclarée `one_to_one`, ce qui la fait échouer bruyamment plutôt que de
dupliquer silencieusement des lignes.

**Biais d'exclusion des IPS non publiés.** 2 505 établissements (6,3 %), presque
exclusivement des écoles, n'ont pas d'IPS publié — la DEPP ne diffuse l'indice que
pour les écoles ayant compté au moins 25 élèves de CM2 sur cinq ans. Ces petites
écoles, majoritairement rurales, ne sont **que 4,3 % à relever de l'éducation
prioritaire, contre 12,3 % de l'ensemble**. Leur exclusion retire donc surtout des
établissements hors dispositif : elle est peu susceptible de fausser la
comparaison, sans être pour autant neutre (environ 110 établissements classés sont
perdus).

**Établissements non appariés.** 307 établissements (0,8 %) sont absents de
l'annuaire, dont 295 écoles, concentrées dans le Pas-de-Calais, la Seine-Maritime
et la Charente-Maritime. Vraisemblablement fermés ou regroupés entre la collecte de
l'IPS et la mise à jour de l'annuaire.

🚧 *À compléter : mesures d'inégalité retenues (indice de dissimilarité de Duncan,
indice de Moran), choix cartographiques.*

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
