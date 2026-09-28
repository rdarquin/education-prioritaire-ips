# Dictionnaire des données

Description des deux fichiers de `data/raw/`, reconstructibles par
`uv run python -m src.download`. Constats établis le 22 septembre 2026 sur les
millésimes alors en ligne.

Le champ de ce projet est celui des **collèges**. Les fichiers IPS du premier
degré et des lycées existent au catalogue du ministère mais ne sont pas
téléchargés : voir « Autres jeux IPS disponibles » en fin de document.

---

## Comment l'IPS est construit

Source : métadonnées officielles du jeu de données (DEPP – ministère chargé de
l'Éducation nationale), consultées le 22 septembre 2026.

**Le principe.** À chaque profession et catégorie sociale (PCS) des parents, ou
couple de PCS, est associée une valeur numérique. Cette valeur résume un
ensemble d'attributs socio-économiques et culturels liés à la réussite
scolaire — conditions de vie, capital culturel, environnement familial. Plus
l'IPS est élevé, plus les élèves sont en moyenne d'origine favorisée.

**Comment ces valeurs de référence sont obtenues.** Par une méthode
statistique appliquée aux *panels d'élèves* de la DEPP, échantillons suivis
dans le temps pour lesquels on dispose d'une information détaillée sur les
conditions de vie. On en tire une **table de passage PCS → IPS**. La version en
vigueur depuis la rentrée 2022 s'appuie sur le panel d'élèves entrés en CP en
2011 ; la précédente reposait sur le panel entré en sixième en 2007.

**Deux niveaux à ne pas confondre :**
- IPS d'un **élève** = la valeur associée à la PCS de ses parents
- IPS d'un **établissement** = la moyenne des IPS de ses élèves

Référence méthodologique : Rocher, T. (2016), « Construction d'un indice de
position sociale des élèves », *Éducation & formations*, DEPP, n° 90,
pp. 5-27. Voir aussi la Note d'information DEPP n° 23.16 (2023).

### Spécificités du calcul pour les collèges

- L'IPS d'un collège est calculé sur **l'ensemble de ses élèves**, dont les PCS
  sont collectées à l'inscription. Contrairement au premier degré, il n'y a ici
  ni décalage rétrospectif ni seuil d'effectif : l'indicateur décrit le public
  effectivement scolarisé à la rentrée considérée.
- Les valeurs manquantes sont de **vraies valeurs manquantes** — la case est
  vide — et non le code `NS` utilisé pour le premier degré. Elles sont rares :
  8 lignes sur 21 061, soit une seule pour la rentrée 2024-2025.
- Champ : collèges sous tutelle de l'Éducation nationale, publics et privés
  **sous contrat**. Le privé hors contrat n'est pas couvert.

### Deux avertissements de la DEPP à reprendre dans les limites

1. **« Il est conseillé de ne pas sur-interpréter des différences de 3 points
   ou moins »** entre IPS moyens. L'indice repose sur des PCS déclarées par les
   familles, donc entaché d'une marge d'erreur. À appliquer scrupuleusement
   dans les commentaires de cartes et de classements.
2. **Rupture de série à la rentrée 2022** : changement de table de passage, et
   les élèves dont les PCS des deux parents sont non renseignées ne sont plus
   inclus. Les données antérieures à 2022 ne sont pas comparables aux
   suivantes. *Les trois rentrées de ce fichier étant toutes postérieures à la
   rupture, elles sont comparables entre elles.*

---

## Vue d'ensemble

| Fichier | Une ligne = | Lignes | Colonnes |
|---|---|---|---|
| `ips_colleges.csv` | un collège × une rentrée | 21 061 | 24 |
| `annuaire.csv` | un établissement (état courant) | 68 581 | 70 |

Le fichier IPS est un **panel** : il couvre trois rentrées, 2023-24 à 2025-26.
La rentrée retenue est **2024-2025**, la plus récente pour laquelle l'annuaire
et le fichier IPS concordent. Sans filtre, chaque collège serait compté trois
fois.

L'annuaire n'a pas de dimension temporelle : c'est une photographie de l'état
actuel du réseau. Il couvre tous les types d'établissements (48 360 écoles,
9 183 collèges, 5 644 lycées, plus des services administratifs et
médico-sociaux), et n'est donc **pas restreint au champ du projet** — c'est la
jointure sur les UAI du fichier IPS qui opère la restriction.

---

## 1. `ips_colleges.csv`

### Identification

| Colonne | Signification |
|---|---|
| `uai` | **Clé de l'établissement.** « Unité Administrative Immatriculée », ex. `0010093W`. Identifiant national officiel, unique et stable. Toujours 8 caractères : 7 chiffres suivis d'une lettre de contrôle (vérifié sur 100 % du fichier). Les **3 premiers chiffres codent le département** (99,5 % du fichier) ; les exceptions sont `620` → Corse-du-Sud (`2A`) et `720` → Haute-Corse (`2B`), héritage d'avant la partition de la Corse. C'est de ce préfixe que vient le `code_departement` à 3 caractères de l'annuaire. Clé de jointure avec l'annuaire. |
| `nom_de_l_etablissement` | Libellé en majuscules non accentuées. Beaucoup d'homonymes — `Collège Jean Moulin` revient des dizaines de fois : **ne jamais joindre sur le nom**. Le projet retient le libellé de l'annuaire, accentué et en casse normale, lisible sur une carte. |

### Temps

| Colonne | Signification |
|---|---|
| `rentree_scolaire` | `2023-2024`, `2024-2025` ou `2025-2026`. **À filtrer systématiquement**, sinon chaque collège est compté trois fois. |

### Localisation administrative

| Colonne | Signification |
|---|---|
| `region_academique` / `region_insee` | Le fichier collèges fournit **les deux** : le découpage académique et le vrai code INSEE (`44` = Grand Est). Ne pas les confondre. |
| `code_academie` / `academie` | Académie de rattachement, 30 valeurs sur le champ public. Découpage propre à l'Éducation nationale, sans équivalent INSEE. C'est l'échelon auquel l'enveloppe d'éducation prioritaire a été répartie : variable centrale ici. |
| `code_du_departement` / `departement` | 2 caractères, ex. `01`, `51`. Inclut `2A` et `2B` (Corse) : **à garder en texte**, jamais en nombre. |
| `code_insee_de_la_commune` / `nom_de_la_commune` | 5 caractères, ex. `01004`. **C'est la bonne clé pour croiser avec l'INSEE** (revenu médian, population, contours communaux). |

### Caractéristique

| Colonne | Signification |
|---|---|
| `secteur` | `public` (16 052 lignes sur les trois rentrées) ou `privé sous contrat` (5 009). Deux modalités seulement. |

### La mesure

| Colonne | Signification |
|---|---|
| `ips` | **L'indice de position sociale de l'établissement.** Étendue observée en 2024-25 : 56,0 à 162,5, médiane 103,6. La colonne est lue en texte puis convertie : une case vide devient une valeur manquante. |
| `ecart_type_de_l_ips` | Dispersion des IPS des élèves *au sein* du collège. **Absente du fichier des écoles.** Deux collèges de même IPS moyen peuvent être très différents : l'un socialement homogène, l'autre mélangeant des publics opposés. Variable précieuse pour parler de mixité sociale — non exploitée à ce jour dans ce projet. |

### Valeurs de référence

Neuf colonnes : `ips_national`, `ips_national_public`, `ips_national_prive`, et
les mêmes déclinaisons en `ips_academique_*` et `ips_departemental_*`.

**Elles ne décrivent pas l'établissement.** Ce sont des moyennes de référence,
répétées à l'identique sur chaque ligne : une seule valeur nationale par
rentrée, une par académie, une par département. Vérifié.

Leur intérêt : positionner un établissement par rapport à son contexte. Un IPS
de 95 ne se lit pas pareil dans un département à 108 et dans un département à
92. Elles sont redondantes — on pourrait les recalculer — mais pratiques.

---

## 2. `annuaire.csv`

70 colonnes, dont une dizaine utiles ici. Taux de remplissage mesurés sur
l'ensemble du fichier, tous types d'établissements confondus.

| Colonne | Rempli | Signification |
|---|---|---|
| `identifiant_de_l_etablissement` | 100 % | **Le code UAI.** Nom différent de celui du fichier IPS (`uai`), même contenu. ⚠️ 75 UAI apparaissent en double (157 lignes) : même établissement, deux libellés. Dédoublonner avant toute jointure. |
| `nom_etablissement` | 100 % | Libellé, ici en casse normale et accentué — contrairement au fichier IPS. C'est celui que retient le projet. |
| `type_etablissement` | 99,6 % | `Ecole`, `Collège`, `Lycée`, `EREA`, `Médico-social`, `Service Administratif`… ⚠️ Les **SEGPA sont typées `Collège`** alors que ce sont des sections internes à un collège existant, dotées de leur propre UAI. Les compter comme collèges gonfle tout dénominateur : 1 391 SEGPA publiques pour 5 418 collèges publics réels. Elles ne perturbent pas la jointure de ce projet — elles n'ont pas de ligne IPS — mais tout comptage direct dans l'annuaire doit les écarter. |
| `statut_public_prive` | 97,1 % | `Public` / `Privé`. Redondant avec `secteur` du fichier IPS, et moins fiable (3 % de trous). Préférer `secteur`. |
| `latitude` / `longitude` | 99,4 % | **Coordonnées géographiques.** La raison d'être de ce fichier dans le projet. Parmi les collèges appariés avec l'IPS, aucun n'en est dépourvu. |
| `appartenance_education_prioritaire` | 11,2 % | `REP` ou `REP+`. ⚠️ **Le vide signifie « hors éducation prioritaire »**, ce n'est pas une donnée manquante — il est donc remplacé explicitement par `hors EP` dès le chargement, une chaîne ne se propageant pas silencieusement dans les `groupby` comme le ferait une valeur nulle. Variable de décision de tout le projet. |
| `code_commune` | 100 % | Code INSEE de la commune, 5 caractères. |
| `code_departement` | 100 % | ⚠️ **3 caractères** (`093`), alors que le fichier IPS en utilise 2 (`93`). Voir « Pièges ». |
| `code_region` | 100 % | ⚠️ Code **INSEE** ici (`11` = Île-de-France). |
| `etat` | 100 % | `OUVERT` (68 579) ou `A FERMER` (2). |
| `date_ouverture` | 100 % | Format `1971-05-24`. |

---

## Pièges de jointure

Quatre incohérences entre fichiers, toutes vérifiées. Ce sont elles qui
produisent des bugs silencieux — un résultat qui semble plausible mais qui est
faux.

**1. Les codes département n'ont pas le même format.** `93` dans le fichier
IPS, `093` dans l'annuaire. Une jointure directe ne rapprocherait rien. Plus
généralement, tout code administratif doit être lu en **texte** : `01` devenu
`1` ne se rapproche plus de rien, et `2A` échoue à la conversion numérique.

**2. Les UAI en double dans l'annuaire.** 75 UAI y figurent deux fois. Une
jointure naïve dupliquerait des lignes IPS et le nombre de collèges
augmenterait sans explication apparente. Le projet dédoublonne après avoir
vérifié que les lignes concernées ne se contredisent **ni** sur les coordonnées
**ni** sur le statut d'éducation prioritaire — aucune divergence constatée — et
déclare la jointure `one_to_one`, ce qui la fait échouer bruyamment plutôt que
de gonfler silencieusement le fichier.

**3. Les colonnes ne portent pas les mêmes noms.** `uai` vs
`identifiant_de_l_etablissement`, `code_du_departement` vs `code_departement`.

**4. Le code région du fichier IPS n'est pas toujours le code INSEE.** Le
fichier collèges fournit heureusement `region_insee` à côté de
`region_academique`. Le piège vaut surtout pour le fichier des écoles, qui ne
propose que la numérotation alphabétique de l'Éducation nationale (`01` =
Auvergne-Rhône-Alpes) : y joindre des données INSEE associerait
Auvergne-Rhône-Alpes à la Guadeloupe.

---

## Ce que les données ne contiennent pas

- **Aucun effectif d'élèves**, ni dans le fichier IPS ni dans l'annuaire. On ne
  peut donc pas pondérer les moyennes par la taille des établissements : un
  collège de 150 élèves pèse autant qu'un collège de 900. C'est la limite
  principale du projet, documentée comme telle dans le README.
- **Aucun indicateur de résultats scolaires.** L'IPS décrit l'origine sociale,
  pas la performance.
- **Le privé hors contrat** est absent.
- **Le rattachement école → collège de secteur.** Le label d'une école découle
  de celui de son collège, mais aucun des fichiers mobilisés ne permet de
  reconstituer ce lien. C'est ce qui rendrait possible une extension au premier
  degré.

---

## Autres jeux IPS disponibles au catalogue

Le catalogue du ministère (306 jeux de données) contient plusieurs variantes
IPS. Celle retenue ici n'est pas la seule :

| Identifiant | Rentrées couvertes | Remarque |
|---|---|---|
| `fr-en-ips-colleges-ap2023` *(utilisé)* | 2023-24 → 2025-26 | |
| `fr-en-ips-ecoles-ap2022` | 2022-23 → 2024-25 | premier degré ; ⚠️ **« Ce jeu de données n'est plus actualisé »** (avertissement officiel) |
| `donnees-ips-ecoles` | 2016-17 → 2024-25 | premier degré, 9 rentrées |
| `donnees-ips-lycees` | 2016-17 → 2024-25 | lycées, hors du dispositif d'éducation prioritaire |
| `fr-en-ips-erea-ap2022` | — | EREA |

**Le piège de la série longue.** Les jeux couvrant neuf rentrées paraissent
préférables. Mais ils enjambent la rupture méthodologique de 2022 : comparer
2016-17 à 2024-25 reviendrait à comparer deux indices construits différemment.
Si une telle source est retenue, la rupture doit être traitée explicitement —
pas ignorée parce que les colonnes se ressemblent.

---

## Appariement IPS ↔ annuaire (rentrée 2024-2025)

| | Appariés | Total | Taux |
|---|---|---|---|
| Collèges | 6 975 | 6 987 | **99,8 %** |

Les 12 collèges non appariés sont dispersés sur huit départements, sans
concentration notable. Vraisemblablement fermés ou regroupés entre la collecte
de l'IPS et la mise à jour de l'annuaire.

**Un écart en sens inverse existe aussi** et mérite d'être connu : dix collèges
classés REP+ dans l'annuaire n'ont **aucune ligne** dans le fichier IPS pour
2024-2025 — huit y figurent pour d'autres rentrées, deux n'y apparaissent
jamais. Ils ne sont donc pas écartés par le nettoyage, ils manquent à la
source. Le fichier d'analyse compte 362 collèges REP+ là où l'annuaire en
recense 372.
