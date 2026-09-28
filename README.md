# Éducation prioritaire et réalité sociale des établissements

> Analyse territoriale — données DEPP et annuaire de l'éducation, rentrée 2024-2025.

**Le classement en éducation prioritaire coïncide-t-il avec la réalité sociale des
établissements, mesurée par l'indice de position sociale (IPS) ? Et là où les deux
divergent, que nous apprennent ces exceptions ?**

Ce travail confronte deux mesures du même phénomène : d'un côté le classement
administratif en REP et REP+, de l'autre l'IPS publié par la DEPP pour chaque école
et chaque collège. Il quantifie leur recouvrement, identifie les établissements
socialement défavorisés situés hors du dispositif, et cartographie leur répartition
territoriale.

**Résultat principal.** Sur 30 889 établissements publics, **653 figurent parmi les
10 % socialement les plus défavorisés sans être classés en éducation prioritaire**.
Le ciblage est globalement cohérent — 30 points d'IPS séparent les établissements
classés REP+ des établissements non classés — mais il est nettement plus lâche pour
les écoles (**75,8 %** des plus défavorisées sont couvertes) que pour les collèges
(**93,8 %**). Cet écart découle de l'architecture du dispositif, organisé en réseaux
bâtis autour d'un collège : le classement d'un collège en difficulté est direct,
celui d'une école dépend du collège vers lequel ses élèves sont orientés.

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

Ce mécanisme est **établi par le producteur de la politique**, et non déduit des
données : le ministère indique que « les écoles maternelles et élémentaires sont
classées en fonction du collège de secteur ». Les données le confirment de deux
façons : **aucun lycée** ne porte de label (0 sur 5 600), et l'on compte **environ
six écoles labellisées par collège labellisé** (6 552 pour 1 104), soit l'ordre de
grandeur d'un secteur de recrutement.

Cette organisation n'altère toutefois pas la lisibilité des résultats : l'écart
d'IPS entre établissements classés et non classés est de même ampleur pour les
écoles (−22 points en REP, −31 en REP+) que pour les collèges (−23 et −35). Le
classement des écoles suit donc leur propre réalité sociale presque aussi
étroitement que celui des collèges.

---

## Comment le classement en éducation prioritaire est construit

Ce travail confronte l'IPS au classement REP/REP+. Encore faut-il savoir comment ce
classement a été établi — c'est la condition pour interpréter correctement les
écarts. Source : Cour des comptes, *L'éducation prioritaire, une politique publique
à repenser*, 2025.

### La procédure de 2015, en trois temps

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

*À noter : le revenu médian du secteur a été testé et écarté, au motif qu'« intégrant
tous les foyers fiscaux d'un quartier, dont les retraités et les personnes sans
enfants, il ne constitue pas une photographie de la population scolaire ».*

**2. Un dialogue local** conduit par les recteurs d'octobre à décembre 2014, la liste
finale étant arrêtée par le ministre.

**3. Les écoles classées par héritage.** « L'absence de base de données concernant
les écoles ne permettant pas de construire un indice qui leur est propre, le choix a
donc été fait de labelliser les écoles selon une logique de réseau. » Ce n'est donc
pas un choix pédagogique mais une **contrainte de données** — et l'on notera que
l'IPS des écoles, mobilisé ici, n'a été publié qu'en 2022, sept ans après la carte.

**Résultat :** 1 093 réseaux — 362 collèges et 2 459 écoles en REP+, 731 collèges et
4 136 écoles en REP.

### Cinq limites du dispositif de classement

**1. L'indice n'a pas été appliqué.** C'est le point le plus important pour ce
travail. « La carte théorique correspondant à ces critères nécessitait **350 réseaux
entrants et 350 réseaux sortants**. Or les contextes locaux n'ont permis de procéder
qu'à **195 sorties et 206 entrées** » — soit environ 57 % des mouvements prescrits.
Le périmètre devait rester constant, autour de 500 000 collégiens : chaque entrée
exigeait une sortie, et retirer un label s'est révélé politiquement très difficile.
Une mesure de compensation a même dû être créée — maintien des indemnités ZEP
pendant trois ans et bonification du barème de mutation.

**Conséquence directe : une partie des divergences mesurées ici ne provient pas de
l'IPS, mais du fait que la carte s'écarte de son propre indice social.**

**2. Les écoles ne sont pas évaluées pour elles-mêmes.** D'où deux désajustements
symétriques nommés par la Cour : les **« écoles orphelines »**, non classées « alors
même que la réalité sociologique de leur public le justifierait », et les **« écoles
embarquées »**, classées alors que leur public est plus favorisé.

**3. La carte est figée depuis dix ans.** Elle « devait être réactualisée tous les
quatre ans. Or l'entreprise, délicate, n'a pas été reconduite depuis dix ans ».

**4. Le label est binaire.** L'allocation de moyens étant conditionnée à la
labellisation, le mécanisme « apparaît comme binaire et ne permet d'offrir une réelle
progressivité dans les ressources ». Les effets de seuil sont forts.

**5. L'indice n'est pas reproductible.** Ni la spécification de la régression, ni les
coefficients, ni la valeur du seuil séparant REP+ de REP ne sont publics. L'instrument
qui a déterminé le classement de 1 093 réseaux ne peut pas être recalculé à partir
des sources ouvertes.

Et une critique de fond, posée par le SGMAP avant même la réforme : **« est-ce qu'une
politique est encore prioritaire quand elle concerne 20 % d'une population ? »**

---

## Qu'est-ce que l'IPS ?

L'indice de position sociale est produit par la DEPP. Il associe à chaque profession
et catégorie sociale (PCS) des parents, ou couple de PCS, une **valeur numérique**
résumant un ensemble d'attributs socio-économiques et culturels liés à la réussite
scolaire : conditions de vie, capital culturel, environnement familial. Plus l'IPS
est élevé, plus les élèves sont en moyenne d'origine favorisée.

Ces valeurs de référence proviennent d'une **table de passage PCS → IPS**, établie
statistiquement sur les panels d'élèves de la DEPP — des échantillons suivis dans le
temps et documentés en détail. La table en vigueur depuis la rentrée 2022 s'appuie
sur le panel d'élèves entrés en CP en 2011.

Deux niveaux à ne pas confondre : l'IPS d'un **élève** est la valeur associée à la
PCS de ses parents ; l'IPS d'un **établissement** est la moyenne des IPS de ses
élèves.

**Ce que l'IPS ne mesure pas.** Il ne dit rien des résultats scolaires. Un
établissement à IPS faible accueille un public socialement défavorisé, ce qui ne
préjuge ni de la qualité de son enseignement ni des performances de ses élèves.
Confondre les deux est le contresens le plus courant sur ces données.

**Marge d'erreur.** L'indice repose sur des PCS déclarées par les familles. La DEPP
recommande explicitement de **ne pas sur-interpréter des différences de 3 points ou
moins** entre IPS moyens. Cette réserve est appliquée dans tout ce travail.

**Une publication obtenue par voie contentieuse.** Ces données sont restées non
publiques jusqu'en 2022, le ministère craignant qu'elles ne servent à contourner la
carte scolaire. Après trois refus successifs malgré une saisine de la Commission
d'accès aux documents administratifs, le journaliste Alexandre Léchenet
(*La Gazette des communes*) a obtenu du tribunal administratif de Paris, par une
décision du 13 juillet 2022, que le ministère lui transmette les IPS. La DEPP les a
publiés sur data.education.gouv.fr en octobre 2022. L'existence même de ce jeu de
données relève ainsi d'une question de politique publique de la donnée — celle de
l'ouverture des statistiques administratives.

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
uv run python -m src.preparation
uv run python -m src.analyse
uv run python -m src.score_ecart
uv run python -m src.distribution_ecart
uv run python -m src.ecarts_extremes
```

`uv sync` installe Python 3.12 et les dépendances aux versions exactes figées dans
`uv.lock`. Aucune donnée n'est versionnée : `src/download.py` reconstruit intégralement
`data/raw/` depuis l'API du ministère.

| Module | Rôle |
|---|---|
| `src/download.py` | télécharge les trois jeux de données bruts |
| `src/preparation.py` | nettoie, joint, contrôle les biais d'exclusion |
| `src/analyse.py` | couverture, ciblage, sensibilité au seuil, divergences territoriales |
| `src/cartographie.py` | fond de carte partagé : contours, DROM rapprochés, annotations |
| `src/score_ecart.py` | score d'écart d'IPS par établissement, aux seuils national et académique |
| `src/distribution_ecart.py` | forme de la distribution de l'écart, aux deux seuils |
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

**Conformité des labels à la carte officielle.** Les statuts REP et REP+ de
l'annuaire sont confrontés aux effectifs publiés par le ministère pour la rentrée
2023 :

| | Carte officielle | Annuaire (données utilisées) |
|---|---:|---:|
| Collèges REP | 731 | 732 |
| Collèges REP+ | 362 | 372 |
| Écoles REP | 4 136 | 4 093 |
| **Écoles REP+** | **2 459** | **2 459** |

Les écoles REP+ concordent exactement ; les autres écarts vont de un à dix
établissements, imputables à la différence de millésime. Les labels de l'annuaire
reproduisent donc fidèlement la carte ministérielle.

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

### Mesures retenues

L'analyse reprend le cadre de l'évaluation d'un dispositif de ciblage. Deux
variables binaires sont croisées : être parmi les X % d'établissements au plus faible
IPS (la mesure), et être classé REP ou REP+ (la décision administrative). Deux taux
en découlent :

- **Couverture** — parmi les établissements les plus défavorisés, quelle part est
  classée ? Répond à : *le dispositif laisse-t-il des établissements de côté ?*
- **Ciblage** — parmi les établissements classés, quelle part figure parmi les plus
  défavorisés ? Répond à : *le dispositif classe-t-il des établissements qui ne sont
  pas les plus en difficulté ?*

Les deux ne disent pas la même chose et évoluent en sens contraire : élargir le
dispositif améliore la couverture et dégrade le ciblage. Le rang social est calculé
séparément pour les écoles et les collèges, dont les distributions d'IPS diffèrent.

Le seuil de 10 % étant conventionnel, une **analyse de sensibilité** l'accompagne
systématiquement (5 %, 10 %, 15 %, 20 %, 25 %).

### Choix cartographiques

Les contours départementaux proviennent de `cartiflette`, package du laboratoire
d'innovation de l'Insee redistribuant les fonds IGN ADMIN EXPRESS, dans sa variante
« DROM rapprochés » — convention des publications de l'Insee. Les départements
d'outre-mer y sont déplacés et redimensionnés pour figurer auprès de la métropole :
**ces cartes ne permettent donc aucune mesure de distance ni de surface**, et chacune
le rappelle dans sa note.

`src/cartographie.py` fournit le fond commun à toutes les cartes du dépôt — contours,
transformation des DROM et annotation des territoires ultramarins, qui seraient sinon
impossibles à identifier puisqu'ils ne sont ni à leur place ni à leur échelle.

Trois partis sont pris systématiquement :

1. **Un effectif minimal conditionne l'affichage.** Un taux départemental calculé sur
   quelques établissements varierait de plusieurs points au gré d'un seul d'entre
   eux ; les départements concernés sont laissés en gris plutôt qu'affichés avec une
   valeur instable.
2. **Les échelles sont découpées en classes de quantiles**, et non en rampes
   linéaires. La distribution des scores départementaux est très asymétrique :
   quelques départements extrêmes absorberaient toute la dynamique de couleur et
   écraseraient les quatre-vingt-dix autres dans une teinte indistincte. Les bornes
   de classes sont affichées sur chaque barre de couleur.
3. **La nature de la variable commande la palette.** Une grandeur sans polarité reçoit
   une échelle séquentielle d'une seule teinte ; une grandeur signée reçoit une
   échelle divergente dont le point neutre est un gris, et non un blanc qui
   disparaîtrait sur le fond.

## Résultats

Champ : **30 889 établissements publics** (25 564 écoles, 5 325 collèges), rentrée
2024-2025. Le privé sous contrat est écarté du calcul de couverture : **aucun de ses
5 849 établissements n'est classé REP ou REP+**, y compris les 26 qui figurent parmi
les 10 % les plus défavorisés. L'éducation prioritaire est un dispositif de
l'enseignement public ; les y inclure dégraderait mécaniquement le taux de couverture
sans rien mesurer.

### 1. Le dispositif vise le cinquième inférieur, pas le dixième

En retenant comme référence les 10 % d'établissements au plus faible IPS, seuls 46 %
des collèges classés et 54 % des écoles classées en font partie. Mais le taux monte à
76 % et 78 % lorsqu'on élargit la référence aux 20 % les plus défavorisés.

| Seuil retenu | Couverture collèges | Couverture écoles | Ciblage collèges | Ciblage écoles |
|---|---:|---:|---:|---:|
| 5 % | 98,5 % | 85,9 % | 23,9 % | 30,2 % |
| 10 % | 93,8 % | 75,8 % | 45,7 % | 53,8 % |
| 15 % | 87,3 % | 65,0 % | 63,5 % | 68,9 % |
| 20 % | 78,3 % | 55,3 % | 75,9 % | 78,2 % |
| 25 % | 69,3 % | 47,5 % | 84,4 % | 84,3 % |

L'apparent défaut de ciblage au seuil de 10 % n'en est donc pas un : il traduit le
fait que le périmètre de l'éducation prioritaire correspond approximativement au
cinquième le plus défavorisé des établissements publics.

### 2. Les collèges sont presque tous couverts, les écoles beaucoup moins

C'est le résultat le plus net.

| | Défavorisés (10 % plus bas) | Non classés | Couverture |
|---|---:|---:|---:|
| Collèges | 533 | **33** | **93,8 %** |
| Écoles | 2 567 | **620** | **75,8 %** |

Seuls 33 collèges parmi les plus défavorisés échappent au dispositif, contre 620
écoles. Cet écart est cohérent avec l'architecture de la politique : l'éducation
prioritaire est constituée de réseaux bâtis autour d'un collège, auxquels les écoles
sont rattachées. Le classement d'un collège en difficulté est direct ; celui d'une
école dépend du collège vers lequel ses élèves sont orientés. Une école très
défavorisée dont le collège de secteur ne l'est pas suffisamment reste hors
dispositif.

**Les divergences entre classement administratif et réalité sociale se concentrent
donc au niveau des écoles, et découlent d'un trait de conception du dispositif plutôt
que d'erreurs de classement individuelles.**

#### Validation externe

Ces 620 écoles correspondent à ce que la Cour des comptes nomme les **« écoles
orphelines »**. Un chiffrage indépendant existe : la mission *Territoires et
réussites* recensait en 2019, « en retenant un IPS équivalent ou inférieur à 78
(soit la médiane des écoles de l'éducation prioritaire REP+ et REP), **471 écoles
scolarisant 55 126 élèves** non labellisées éducation prioritaire ».

Deux méthodes distinctes — seuil absolu de 78 en 2019, décile national en 2024-2025 —
aboutissent au même ordre de grandeur. Le phénomène mesuré ici n'est donc pas un
artefact du critère retenu.

La mission notait par ailleurs que parmi ces écoles, « la majorité est en commune
urbaine, principalement en QPV mais 20 % appartiennent à l'espace rural,
principalement en rural éloigné » et « 20 % de ces écoles sont situées dans les
départements d'outre-mer ».

### 3. L'outre-mer cumule un désavantage massif et une meilleure couverture

| | Établissements | Part dans les 10 % les plus défavorisés | Couverture |
|---|---:|---:|---:|
| Métropole | 29 809 | 8,8 % | 77,0 % |
| Outre-mer | 1 080 | **43,2 %** | **89,7 %** |

Près d'un établissement ultramarin sur deux figure parmi les 10 % les plus
défavorisés de France, contre moins d'un sur dix en métropole. Ces territoires sont
par ailleurs mieux couverts que la métropole.

### 4. La couverture varie fortement entre départements, sans lien avec leur niveau social

Parmi les 42 départements comptant au moins 20 établissements défavorisés, la
couverture s'échelonne de **45,8 %** (Saône-et-Loire) à la couverture intégrale.

**Une hypothèse a été testée puis écartée** : celle selon laquelle les poches de
pauvreté isolées dans des départements globalement aisés seraient moins bien
couvertes. La corrélation entre IPS médian départemental et taux de couverture est
de **−0,08**, soit nulle, et la relation n'est pas monotone — ce sont les
départements du tiers médian qui affichent la couverture la plus faible (77,4 %),
devant le tiers le plus pauvre (81,7 %) et le tiers le plus aisé (84,9 %).

La variabilité départementale est donc réelle et forte, mais elle ne s'explique pas
par la richesse du département. Elle appelle d'autres pistes : l'ancienneté de la
carte de l'éducation prioritaire, dont la dernière révision d'ampleur remonte à
2015, ou des différences de pratique entre académies.

---

## Le score d'écart d'IPS

L'analyse de couverture repose sur un seuil conventionnel — les 10 % les plus
défavorisés. Une seconde mesure s'en dispense en prenant pour référence
**l'enveloppe réellement allouée**.

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
**sur-inclusion** (au-dessus du seuil, classé). Les confondre ferait disparaître
l'information la plus intéressante, ils sont donc distingués partout.

Les deux types d'erreur étant en nombre égal par construction, le seuil s'élimine de
la somme des scores, qui vaut alors exactement l'écart de masse d'IPS entre
l'allocation réelle et l'allocation optimale à enveloppe égale. Cette identité est
recalculée à chaque exécution et interrompt le programme si elle est violée.

**Résultat d'ensemble : 90,6 % des collèges publics ont un score nul**, et la médiane
des écarts non nuls est de 3,2 points — à peine au-dessus du seuil de 3 points en
deçà duquel la DEPP recommande de ne rien interpréter. Rapporté au nombre de places,
l'écart total vaut 2,01 points d'IPS par collège classé.

### La forme de la distribution

![Distribution de l'écart d'IPS au seuil budgétaire](outputs/figures/distribution_ecart.png)

La variable est à **inflation de zéros**, ce qui impose deux précautions de tracé.
La barre du zéro est tronquée et son effectif annoté, faute de quoi elle écraserait
tout le reste ; et les classes sont calées pour que zéro tombe au *centre* d'une
barre, sans quoi les conformes se répartiraient sur deux barres voisines et la masse
centrale paraîtrait deux fois plus petite qu'elle n'est.

**L'asymétrie ne porte pas sur les effectifs mais sur les queues.** Les deux côtés
comptent presque le même nombre d'établissements — 249 oublis contre 250
sur-inclusions — mais ils ne se répartissent pas de la même façon. Les oublis
s'entassent près de zéro : 135 des 249 restent sous 3 points. Les sur-inclusions
peuplent la queue : 141 des 250 la dépassent. Visuellement, la barre la plus haute est
orange, juste à droite de zéro, mais c'est le bleu qui s'étire jusqu'à −32 quand
l'orange s'arrête à +18. Le dispositif se trompe aussi souvent dans les deux sens,
mais il se trompe plus fort lorsqu'il classe.

Les écoles ont une distribution nettement plus étalée : médiane des écarts non nuls à
5,3 points contre 3,2, centile 99 à 31,3 contre 20,2. C'est cohérent avec le mécanisme
de labellisation par réseau, qui rattache une école sans regarder son propre IPS.

Le trait noir donne la même distribution lorsque le seuil est recalculé académie par
académie. **Le resserrement porte sur la queue, non sur le centre** : la part de
conformes ne gagne que 1,4 point pour les collèges (90,6 → 92,0 %), mais le centile 99
tombe de 20,2 à 17,1, et de 31,3 à 23,0 pour les écoles, soit −27 %. Autrement dit,
changer d'étalon élimine les cas spectaculaires sans rien changer au désaccord de
fond.

### Les 48 cas au-delà de 10 points

Restent les cas qu'aucune imprécision de mesure ne peut expliquer : **48 collèges**
dont l'écart au seuil atteint 10 points, soit plus de trois fois le seuil
d'interprétabilité. Ils se répartissent en **32 sur-inclusions et 16 oublis** — deux
fois plus de collèges classés à tort, au sens de l'IPS, que de collèges oubliés.

#### Les sur-inclusions

![Collèges sur-inclus par académie et par ampleur de l'écart](outputs/figures/sur_inclusions_academies.png)

Treize académies sur trente sont concernées ; les dix-sept autres n'ont aucun cas.
**Paris en concentre 11 à lui seul**, dont 4 des 6 écarts supérieurs à 20 points.
Bordeaux suit avec 5, dont les 2 autres écarts extrêmes. À elles deux, ces académies
détiennent la totalité de la tranche haute.

![Nombre de collèges sur-inclus par département](outputs/figures/sur_inclusions_departements.png)

Seize départements sont concernés : Paris (11), la Gironde (3), puis la Corse-du-Sud,
la Dordogne, la Seine-Saint-Denis et la Nièvre (2 chacun). Le fait notable est
l'**absence de motif géographique** : en dehors de deux foyers urbains, les cas sont
isolés et dispersés, sans continuité territoriale, et aucun DROM n'est concerné. Il
ne s'agit donc pas d'un phénomène régional mais d'une accumulation de situations
locales.

#### Les oublis

![Collèges oubliés par académie et par ampleur de l'écart](outputs/figures/oublis_academies.png)

**Aucun oubli n'atteint 20 points** — le plus fort vaut 17,4 — alors que six
sur-inclusions dépassent ce niveau. La tranche haute figure dans la légende mais
reste vide : les deux figures partagent le même découpage, sans quoi l'asymétrie
disparaîtrait de la lecture. Elle est le fait le plus net de cette comparaison.
Le dispositif se trompe donc dans les deux sens, mais il se trompe plus souvent
*et* plus fort lorsqu'il classe que lorsqu'il omet.

Dix académies sont concernées, et la dispersion est bien plus forte que du côté des
sur-inclusions : Montpellier en compte 4, Lille, Lyon et Nancy-Metz 2 chacune, six
autres une seule. Aucune académie ne domine comme Paris domine les sur-inclusions.

![Nombre de collèges oubliés par département](outputs/figures/oublis_departements.png)

Treize départements, dont trois à deux collèges — l'Hérault, la Loire et le
Pas-de-Calais. La répartition est ici franchement périphérique : Nord-Est, sillon
rhodanien, arc méditerranéen, Antilles. Les deux cas les plus marqués sont le collège
Gérard Philipe de Clermont-Ferrand (IPS 71,4) et le collège Montesquieu
d'Évry-Courcouronnes (71,8), non classés alors que leur IPS les place parmi les plus
défavorisés de France.

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

**L'IPS des écoles est rétrospectif.** Il est calculé sur les élèves de CM2 dont les
PCS sont connues à leur entrée en sixième, et correspond à la moyenne des anciens
élèves sur cinq ans. Il décrit donc le public de l'école au cours du quinquennat
écoulé, non celui qui y est actuellement scolarisé. Une école dont le recrutement
social s'est récemment dégradé apparaît meilleure qu'elle ne l'est.

**L'IPS ne dit rien des résultats scolaires.** Ce travail porte sur la composition
sociale des établissements, jamais sur leur performance.

### Le champ retenu

**2 743 établissements sont exclus** : 2 505 sans IPS publié (écoles de moins de
25 élèves de CM2 sur cinq ans) et 307 absents de l'annuaire, dont 69 cumulent les
deux motifs. Le biais a été mesuré —
les exclus ne sont que 4,3 % à relever de l'éducation prioritaire contre 12,3 % de
l'ensemble — mais il n'est pas nul : environ 110 établissements classés disparaissent
de l'analyse.

**Le privé sous contrat est écarté** du calcul de couverture, aucun de ses
établissements n'étant classé. La question de la ségrégation entre secteurs public
et privé, pourtant centrale dans le débat sur les inégalités scolaires, n'est donc
pas traitée ici.

**Les lycées sont hors champ**, l'éducation prioritaire s'arrêtant au collège.

**Le fichier IPS des écoles porte la mention « n'est plus actualisé »** dans les
métadonnées du ministère. Les résultats valent pour la rentrée 2024-2025 et ne
pourront pas être prolongés à partir de cette source.

### Les choix de méthode

**Aucune pondération par les effectifs d'élèves — c'est la limite principale.** Ni
les fichiers IPS ni l'annuaire ne fournissent d'effectif. Une école de 30 élèves pèse
donc autant qu'une école de 400 dans chaque taux calculé ici. Conséquence directe :
les taux de couverture décrivent une part d'**établissements**, jamais une part
d'**élèves**. Or une politique éducative vise des élèves. Le chiffre de 653
établissements non couverts ne doit en aucun cas être converti en nombre d'enfants
concernés.

**Le seuil de 10 % est conventionnel.** L'analyse de sensibilité montre que la
hiérarchie écoles / collèges est stable de 5 % à 25 %, mais que le nombre absolu
d'établissements non couverts varie de 184 à 3 775 selon le seuil retenu. Aucun
chiffre absolu ne doit être cité sans son seuil.

**Une seule rentrée est analysée.** Aucune évolution n'est mesurée.

**Les taux départementaux reposent souvent sur de très petits effectifs.** 59
départements sur 101 comptent moins de 20 établissements défavorisés et sont pour
cette raison exclus de la carte. Pour ceux qui figurent, un écart de quelques
établissements déplace le taux de plusieurs points.

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

**Le lien école → collège de secteur n'est pas dans les données.** Le mécanisme
d'héritage du label est établi par le ministère, mais les fichiers mobilisés ici ne
permettent pas de rattacher une école donnée à son collège. Il est donc impossible de
distinguer une école orpheline d'une école dont le collège de secteur est
effectivement peu défavorisé.

---

## Prolongements possibles

- Reconstituer le rattachement école → collège de secteur, seule voie pour
  distinguer les véritables « écoles orphelines » des écoles dont le collège de
  secteur est effectivement peu défavorisé.
- Mobiliser `donnees-ips-ecoles`, qui couvre neuf rentrées, en traitant explicitement
  la rupture méthodologique de 2022, afin d'examiner si les divergences se creusent.
- Croiser avec les données de revenu médian communal de l'Insee (Filosofi) pour
  confronter l'IPS à une mesure indépendante du niveau de vie local.
- Étendre l'analyse aux lycées, hors dispositif mais dotés d'un fichier IPS.

---

## Sources

**Données**

- [IPS des écoles](https://data.education.gouv.fr/explore/dataset/fr-en-ips-ecoles-ap2022/) — DEPP
- [IPS des collèges](https://data.education.gouv.fr/explore/dataset/fr-en-ips-colleges-ap2023/) — DEPP
- [Annuaire de l'éducation](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/) — ministère chargé de l'Éducation nationale
- Contours départementaux : [cartiflette](https://github.com/InseeFrLab/cartiflette), laboratoire d'innovation de l'Insee, d'après IGN ADMIN EXPRESS

**Construction et critique du classement REP / REP+**

- [L'éducation prioritaire, une politique publique à repenser](https://www.ccomptes.fr/fr/publications/leducation-prioritaire-une-politique-publique-repenser) — Cour des comptes, 2025. Texte intégral en [annexe du rapport sénatorial n° 575](https://www.senat.fr/rap/r24-575/r24-575-annexe.pdf) : construction de l'indice social (p. 24), rattachement des écoles et écoles orphelines (p. 57-59)
- [Refondation de l'éducation prioritaire](https://www.education.gouv.fr/bo/14/Hebdo23/MENE1412775C.htm) — circulaire du 4 juin 2014
- [Critères de classement des écoles en réseau d'éducation prioritaire](https://www.senat.fr/questions/base/2025/qSEQ251106739.html) — question au Sénat et réponse ministérielle, 2025
- [Révision des zonages des réseaux d'éducation prioritaire](https://www.senat.fr/questions/base/2022/qSEQ221103796.html) — réponse ministérielle, avril 2023 : la carte n'a pas été révisée depuis 2015
- [L'éducation prioritaire](https://www.education.gouv.fr/l-education-prioritaire-3140) — ministère chargé de l'Éducation nationale : 1 093 réseaux à la rentrée 2023
- France Stratégie, *Écoles primaires : mieux adapter les moyens aux territoires*, note d'analyse n° 76, avril 2019

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
