# Éducation prioritaire et réalité sociale des collèges

> Analyse territoriale — données DEPP et annuaire de l'éducation, rentrée 2024-2025.

**Le classement en éducation prioritaire (REP et REP+) coïncide-t-il avec la réalité sociale des
collèges ?**

Ce travail confronte deux mesures: d'un côté le classement
administratif en REP et REP+, de l'autre l'IPS publié par la DEPP pour chaque
collège. Il identifie les collèges socialement
défavorisés situés hors du dispositif (les oubliés) ainsi que les collège socialement favorisés qui profite du dispositif (les sur-inclus),  et cartographie la répartition territoriale de chacun.

**Résultat principal.** En a séparé tous les établissements en 2 groupes. Le premier a tout les indices de position sociale les plus faibles et contient autant d'établissement que ceux qui sont REP ou REP+. Le second contient tout le reste. En prenant un seuil de tolérance de 3 points d'IPS (seuil jugé par la DEPP comme interprétable), on constate que **90,6 % des collèges ont le dispositif adapté**. Dans le détail, **environ 1% des collèges (48) s'écartent de plus
de 10 points d'IPS**, dont 32 classés malgré un IPS élevé (11 rien qu'à Paris intra muros) et 16 non classés malgré un IPS
très bas.

---

## Définitions

### Comment le classement en éducation prioritaire est construit

Ce travail confronte l'IPS au classement REP/REP+. Mais comment sont attribués les REP/REP+?

#### La procédure de 2015, en 2 temps

**1. Un indice social unique**, construit par la DEPP **au niveau du collège**. Il
agrège quatre taux :

| Variable |
|---|
| Élèves appartenant aux catégories sociales défavorisées |
| Élèves boursiers (taux 3) |
| Élèves résidant dans ou à moins de **300 mètres** d'une ZUS, devenue QPV |
| Élèves en retard à l'entrée en classe de sixième |

L'agrégation ne se fait pas par moyenne pondérée : l'indice est « construit au
travers d'une **régression économétrique**, c'est-à-dire d'une analyse des
corrélations entre les facteurs mentionnés ». Les poids sont estimés, non choisis.

**2. Un dialogue local** conduit par les recteurs d'octobre à décembre 2014, la liste
finale étant arrêtée par le ministre.

**Résultat :** 1 093 réseaux d'éducation prioritaire, soit **362 collèges en REP+ et 731 en REP**.

#### Les limites du classement REP/REP+

**1. L'indice n'a pas été appliqué.** 350 collège étaient censés rentrer en éducation 
prioritaire et 350 devaient en sortir. Dans les faits, il n'y a eu que **195 sorties et 206 entrées**, soit environ 57 % des mouvements prescrits.

**2. La carte est figée depuis dix ans.** alors qu'elle devait être réactualisée tous les
quatre ans.

**3. Le label est binaire.** et non progressif. Les effets de seuil sont forts.

**4. L'indice n'est pas reproductible.** Ni la spécification de la régression, ni les
coefficients, ni la valeur du seuil séparant REP+ de REP ne sont publics.

### Qu'est-ce que l'IPS ?

C'est l'indice de position sociale. Il associe à chaque profession
et catégorie sociale (PCS) des parents, une **valeur numérique**
résumant un ensemble d'attributs socio-économiques et culturels liés à la réussite
scolaire : conditions de vie, capital culturel, environnement familial. Plus l'IPS
est élevé, plus les élèves sont en moyenne d'origine favorisée.

## Cadrage préalable

Rentrée 2024-2025 :

| Statut | Collèges | IPS moyen |
|---|---:|---:|
| REP+ | 362 | **74,6** |
| REP | 732 | **86,0** |
| Hors dispositif (public) | 4 231 | **104,9** |
| *Privé sous contrat* | *1 649* | *120,3* |

L'écart entre REP+ et collèges publics hors dispositif atteint **30 points d'IPS**, 
Le ciblage est donc globalement très cohérent avec la réalité sociale mesurée par
l'IPS.

---

## Données

| Jeu de données | Source | Lignes | Rentrées couvertes |
|---|---|---|---|
| IPS des collèges | data.education.gouv.fr — `fr-en-ips-colleges-ap2023` | 21 061 | 2023-24, 2024-25, 2025-26 |
| Annuaire de l'éducation | data.education.gouv.fr — `fr-en-annuaire-education` | 68 581 | millésime courant |

*Effectifs relevés le 22 septembre 2026.*

**Deux points méthodologiques :**

1. Le fichier IPS couvre trois rentrées scolaires. On retient la rentrée **2024-2025**, la plus récente pour
   laquelle l'annuaire et le fichier IPS concordent.

2. La jointure avec l'annuaire se fait sur le code UAI nommé `uai` qui est le l'identifiant unique de chaque établissement.

---

## Reproduire l'analyse

```bash
git clone <url-du-depot>
cd ips_inegalites_scolaires
uv sync
uv run python -m src.download
uv run python -m src.preparation
uv run python -m src.analyse
uv run python -m src.score_ecart
uv run python -m src.distribution_ips
uv run python -m src.distribution_ecart
uv run python -m src.ecarts_extremes
```

`uv sync` installe Python 3.12 et les dépendances aux versions exactes figées dans
`uv.lock`. Aucune donnée n'est versionnée : `src/download.py` reconstruit intégralement
`data/raw/` depuis l'API du ministère.

| Module | Rôle |
|---|---|
| `src/download.py` | télécharge les deux jeux de données bruts |
| `src/preparation.py` | nettoie, joint, contrôle les biais d'exclusion |
| `src/analyse.py` | couverture, ciblage, sensibilité au seuil, divergences territoriales |
| `src/cartographie.py` | fond de carte partagé : contours, DROM rapprochés, annotations |
| `src/score_ecart.py` | score d'écart d'IPS par collège, aux seuils national et académique |
| `src/distribution_ips.py` | distribution des IPS et position des seuils, national et académiques |
| `src/distribution_ecart.py` | distribution de l'écart au seuil, en points d'IPS, et sa répartition par plage |
| `src/ecarts_extremes.py` | les écarts d'au moins 10 points, des deux côtés, par académie et par département |
| `src/cartographie_score.py` | cartes départementales des écarts significatifs |
| `src/nuage_score.py` | fréquence et nature des écarts, par département |

---

## Structure du dépôt

```
data/raw/          données brutes, en lecture seule, non versionnées
data/processed/    données nettoyées, produites par les scripts
docs/              dictionnaire des données
notebooks/         exploration — brouillon, non destiné à la relecture
src/               code réutilisable
outputs/figures/   cartes (versionnées : elles font partie du livrable)
outputs/tables/    tableaux de résultats
```

---

## Méthode

### Construction du fichier d'analyse

`src/preparation.py` part des deux fichiers bruts et produit
`data/processed/colleges_2024_2025.csv` : une ligne par collège.

| Étape | Effet |
|---|---:|
| Fichier IPS brut (3 rentrées) | 21 061 lignes |
| Filtrage sur la rentrée 2024-2025 | 6 987 |
| Exclusion des non-appariés à l'annuaire | −12 |
| Exclusion des IPS non publiés | −1 |
| **Retenus** | **6 974** |

Les 6 974 collèges retenus disposent tous de coordonnées géographiques. Le taux de
perte est ici de **0,2 %** : la confrontation IPS / annuaire est quasi intégrale au
niveau du collège.

## Le score d'écart d'IPS



### Le principe

Le dispositif classe 1 094 collèges publics sur 5 325. Une règle qui classerait le
même *nombre* d'établissements, mais d'après leur seul IPS, retiendrait les 1 094
IPS les plus faibles — c'est-à-dire tous ceux situés sous **88,80 points**, l'IPS du
collège qui ferme l'enveloppe. Ce seuil n'est donc pas choisi : il découle de la
décision budgétaire elle-même.

Chaque établissement reçoit un score :

- **0** s'il est classé et sous le seuil, ou non classé et au-dessus — conforme ;
- **son écart d'IPS au seuil** dans les deux cas restants.

Ces deux cas sont de sens opposé : **oubli** (sous le seuil, non classé) et
**sur-inclusion** (au-dessus du seuil, classé).

**Résultat d'ensemble : 90,6 % des collèges publics ont un score nul**

### La distribution de l'IPS

![Distribution des IPS des collèges publics et position des seuils](outputs/figures/distribution_ips.png)

**Commentaire à ajouter moi meme**

### La distribution de l'écart au seuil

![Distribution de l'écart d'IPS au seuil budgétaire](outputs/figures/distribution_ecart.png)

**Commentaire à ajouter moi meme**

Les quatre figures qui suivent retiennent, de chaque côté, les **50 plus gros
écarts**. La sélection se fait sur le rang et non sur un seuil fixe : les deux
séries ont ainsi le même effectif, ce qui rend les cartes directement comparables.

La contrepartie est instructive. **À effectif égal, les deux tops ne couvrent pas la
même étendue** : le cinquantième écart vaut 7,7 points du côté des sur-inclusions et
5,7 points seulement du côté des oublis. Il faut donc descendre plus bas pour réunir
cinquante oublis — une autre façon de constater que le dispositif se trompe plus fort
lorsqu'il classe que lorsqu'il omet.

#### Les sur-inclusions

![Collèges sur-inclus par académie et par ampleur de l'écart](outputs/figures/sur_inclusions_academies.png)

Vingt académies sur trente sont représentées ; les dix autres n'ont aucun collège
dans le top 50. **Paris en concentre 13 à lui seul**, dont les 4 écarts supérieurs à
20 points. Bordeaux suit avec 6, dont les 2 autres écarts extrêmes : à elles deux,
ces académies détiennent la totalité de la tranche haute.

![Nombre de collèges sur-inclus par département](outputs/figures/sur_inclusions_departements.png)

Vingt-huit départements sont concernés : Paris (13), puis la Gironde, la Nièvre et la
Corse-du-Sud (3 chacun). Le fait notable est l'**absence de motif géographique** :
en dehors de Paris, les cas sont isolés et dispersés, sans continuité territoriale.
Il ne s'agit donc pas d'un phénomène régional mais d'une accumulation de situations
locales.

#### Les oublis

![Collèges oubliés par académie et par ampleur de l'écart](outputs/figures/oublis_academies.png)

**Aucun oubli n'atteint 20 points** — le plus fort vaut 17,4 — alors que six
sur-inclusions dépassent ce niveau. La tranche haute figure dans la légende mais
reste vide : les deux figures partagent le même découpage, sans quoi l'asymétrie
disparaîtrait de la lecture. Et là où 32 sur-inclusions dépassent 10 points, les
oublis ne sont que 16 : les deux tiers du top 50 des oublis restent sous ce niveau.

Vingt académies sont représentées, et la concentration est d'une tout autre nature
que du côté des sur-inclusions : **Lille en compte 9 et Nancy-Metz 7**, soit un tiers
du total à elles deux, mais aucune ne domine comme Paris. Ce sont deux académies que
l'arithmétique de l'enveloppe contraint — elles comptent plus de collèges sous le
seuil national que de places à pourvoir.

![Nombre de collèges oubliés par département](outputs/figures/oublis_departements.png)

Vingt-huit départements. Le **Nord en compte 6** et la Moselle 4, devant l'Aisne, la
Meurthe-et-Moselle, le Haut-Rhin, le Pas-de-Calais et la Loire (3 chacun). La
répartition est ici franchement périphérique et continue — Nord, Nord-Est, sillon
rhodanien, arc méditerranéen — à l'inverse du semis dispersé des sur-inclusions. Les
deux cas les plus marqués sont le collège Gérard Philipe de Clermont-Ferrand
(IPS 71,4) et le collège Montesquieu d'Évry-Courcouronnes (71,8), non classés alors
que leur IPS les place parmi les plus défavorisés de France.

### Pourquoi Paris n'est pas comparable aux autres

La répartition des réseaux par académie est arrêtée au niveau national ; le recteur
désigne ensuite les établissements dans l'enveloppe reçue. Or **Paris ne compte que
6 collèges sous le seuil national pour 30 places à pourvoir**. Le minimum de
sur-inclusions arithmétiquement possible y est donc de 24 — exactement le nombre
observé. Aucune carte parisienne à 30 collèges ne ferait mieux au regard d'un étalon
national.

Recalculé à l'intérieur de Paris, à enveloppe parisienne inchangée, le nombre de
sur-inclusions tombe de 24 à 8. `src/score_ecart.py` produit cette variante
académique en parallèle de la variante nationale, dans les mêmes fichiers.

Bordeaux, en revanche, résiste au changement d'étalon : l'IPS médian des collèges de
Gironde est de 107,4, et le collège le plus sur-inclus de France y atteint 121,0. Son
écart ne s'explique pas par un effet de repère.

*Cette mesure compare la carte réelle à un classement par IPS. L'IPS n'étant pas le
critère officiel, un écart signale un désaccord entre deux instruments — et non une
erreur administrative.*

## Limites

### Ce que mesure l'indicateur

**L'IPS est un indice construit, pas une observation directe.** Il repose sur les
PCS déclarées par les familles et enregistrées par les établissements. La DEPP
recommande de ne pas interpréter des différences de 3 points ou moins : les
classements fins entre établissements ou entre départements proches n'ont pas de
sens.

**L'IPS ne dit rien des résultats scolaires.** Ce travail porte sur la composition
sociale des collèges, jamais sur leur performance.

### Le champ retenu

**Le premier degré est hors champ.** C'est un choix assumé, justifié plus haut : les
écoles ont été labellisées par héritage du collège de secteur, sans indice propre.
Ce travail ne dit donc rien des « écoles orphelines » ni des désajustements du
premier degré, qui constituent pourtant une part importante du problème posé par la
carte de l'éducation prioritaire.

**13 collèges sont exclus** : 12 absents de l'annuaire et 1 sans IPS publié, soit
0,2 % du champ. Le biais est négligeable à cette échelle.

**Dix collèges REP+ manquent au fichier IPS** pour la rentrée 2024-2025, soit 2,7 %
des REP+. Ils ne sont pas écartés par le nettoyage : ils n'ont simplement pas de
ligne cette année-là. Étant par construction parmi les plus défavorisés, leur absence
atténue très légèrement les écarts mesurés.

**Le privé sous contrat est écarté** du calcul de couverture, aucun de ses collèges
n'étant classé. La question de la ségrégation entre secteurs public et privé,
pourtant centrale dans le débat sur les inégalités scolaires, n'est donc pas traitée
ici.

**Les lycées sont hors champ**, l'éducation prioritaire s'arrêtant au collège.

### Les choix de méthode

**Aucune pondération par les effectifs d'élèves — c'est la limite principale.** Ni le
fichier IPS ni l'annuaire ne fournissent d'effectif. Un collège de 150 élèves pèse
donc autant qu'un collège de 900 dans chaque taux calculé ici. Conséquence directe :
tous les résultats décrivent une part de **collèges**, jamais une part d'**élèves**.
Or une politique éducative vise des élèves. Ni les 33 collèges non couverts ni les
48 écarts extrêmes ne doivent être convertis en nombre d'enfants concernés.

**Le seuil de 10 % est conventionnel**, et son ciblage est plafonné par la taille de
l'enveloppe. Le nombre de collèges non couverts varie de 4 à 409 selon le seuil
retenu : aucun chiffre absolu ne doit être cité sans lui. C'est précisément ce que
le score d'écart évite, en déduisant son seuil de l'enveloppe observée.

**Une seule rentrée est analysée.** Aucune évolution n'est mesurée.

**L'analyse départementale de la couverture n'est pas conduite**, faute d'effectifs
suffisants : 14 départements seulement comptent au moins dix collèges défavorisés.
Les cartes de ce dépôt reposent sur le score d'écart, qui attribue une valeur à
chaque collège et n'a donc pas cette fragilité — sous réserve du seuil d'effectif
appliqué à chaque carte, rappelé dans sa note.

### Ce que ce travail ne dit pas

**Ce n'est pas une évaluation de l'efficacité de l'éducation prioritaire.** On mesure
la cohérence entre un classement et un indicateur social, jamais les effets du
dispositif sur les élèves qui en bénéficient.

**Aucune relation causale n'est établie.** L'analyse est intégralement descriptive.

**Le décalage temporel entre les deux instruments n'est pas traité.** La carte de
l'éducation prioritaire a été refondue en 2015 ; les IPS mobilisés datent de
2024-2025. Une divergence peut donc traduire une évolution sociale survenue depuis le
classement autant qu'une inadéquation d'origine. Distinguer les deux supposerait de
croiser une série temporelle d'IPS avec l'historique des révisions de la carte.

**Les critères réels du classement ne sont pas mobilisés, et ne peuvent pas l'être.**
Le classement repose sur un indice social composite construit par régression au
niveau du collège, dont ni la spécification ni les coefficients ni le seuil ne sont
publics. Ce travail confronte donc deux instruments de mesure ; il ne reconstitue pas
la décision administrative et ne peut à aucun moment conclure qu'un établissement est
« mal classé ».

**Une part des divergences est imputable à la carte, non à la mesure.** La carte de
2015 s'écarte substantiellement de son propre indice social : 206 entrées et
195 sorties réalisées pour 350 et 350 prescrites. Une fraction des écarts observés
ici reflète donc des arbitrages locaux de 2014, et non une inadéquation entre l'IPS
et les critères officiels. Faute d'accès à la carte théorique, cette fraction n'est
pas quantifiable.

**Le premier degré n'est pas traité.** Le label d'une école découlant de celui de
son collège de secteur, la confronter à son propre IPS reviendrait à juger une
décision prise ailleurs. Ce travail ne dit donc rien des désajustements du premier
degré, qui pèsent pourtant lourd dans la critique de la carte.

---

## Prolongements possibles

- Pondérer par les effectifs d'élèves, pour passer d'une part de collèges à une part
  d'élèves — la limite principale de ce travail. Le jeu de données IPS ne fournit
  pas l'effectif ; il faudrait le joindre depuis une autre source du ministère.
- Mobiliser les trois rentrées du fichier IPS plutôt qu'une seule, afin d'examiner
  si les écarts se creusent ou se résorbent.
- Croiser avec les données de revenu médian communal de l'Insee (Filosofi) pour
  confronter l'IPS à une mesure indépendante du niveau de vie local.
- Corriger le recouvrement académique de la taille de l'enveloppe, dont il dépend
  mécaniquement, avant d'en tirer un classement de qualité de la décision locale.
- Étendre l'analyse au premier degré, en reconstituant d'abord le rattachement
  école → collège de secteur, sans lequel la comparaison n'a pas de sens.

---

## Sources

**Données**

- [IPS des collèges](https://data.education.gouv.fr/explore/dataset/fr-en-ips-colleges-ap2023/) — DEPP
- [Annuaire de l'éducation](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/) — ministère chargé de l'Éducation nationale
- Contours départementaux : [cartiflette](https://github.com/InseeFrLab/cartiflette), laboratoire d'innovation de l'Insee, d'après IGN ADMIN EXPRESS

**Construction et critique du classement REP / REP+**

- [L'éducation prioritaire, une politique publique à repenser](https://www.ccomptes.fr/fr/publications/leducation-prioritaire-une-politique-publique-repenser) — Cour des comptes, 2025. Texte intégral en [annexe du rapport sénatorial n° 575](https://www.senat.fr/rap/r24-575/r24-575-annexe.pdf) : construction de l'indice social (p. 24), rattachement des écoles et écoles orphelines (p. 57-59)
- [Refondation de l'éducation prioritaire](https://www.education.gouv.fr/bo/14/Hebdo23/MENE1412775C.htm) — circulaire du 4 juin 2014
- [Critères de classement des écoles en réseau d'éducation prioritaire](https://www.senat.fr/questions/base/2025/qSEQ251106739.html) — question au Sénat et réponse ministérielle, 2025
- [Révision des zonages des réseaux d'éducation prioritaire](https://www.senat.fr/questions/base/2022/qSEQ221103796.html) — réponse ministérielle, avril 2023 : la carte n'a pas été révisée depuis 2015
- [L'éducation prioritaire](https://www.education.gouv.fr/l-education-prioritaire-3140) — ministère chargé de l'Éducation nationale : 1 093 réseaux à la rentrée 2023

**Méthodologie de l'IPS**

- Rocher, T. (2016), « Construction d'un indice de position sociale des élèves », *Éducation & formations*, DEPP, n° 90, pp. 5-27
- Dauphant, F., Evain, F., Guillerm, M., Simon, C., Rocher, T. (2023), « L'indice de position sociale (IPS) : un outil statistique pour décrire les inégalités sociales entre établissements », *Note d'information de la DEPP* n° 23.16
- [L'indice de position sociale (IPS)](https://www.education.gouv.fr/l-indice-de-position-sociale-ips-357755) — ministère chargé de l'Éducation nationale

**Sur la publication des IPS**

- [Indice de position sociale](https://fr.wikipedia.org/wiki/Indice_de_position_sociale) — Wikipédia
- [Comment un journaliste a obtenu les données sur les IPS](https://www.lucyol.fr/blog/ips)
- [Mixité sociale à l'École : comment est construit « l'IPS » ?](https://www.publicsenat.fr/actualites/societe/mixite-sociale-a-lecole-comment-est-construit-lips-lindice-de-position-sociale) — Public Sénat

Voir aussi [`docs/dictionnaire_donnees.md`](docs/dictionnaire_donnees.md) pour la
description détaillée des trois fichiers et des pièges de jointure.

## Auteur

Rémy Darquin
