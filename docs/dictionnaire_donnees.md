# Dictionnaire des données

Description des trois fichiers de `data/raw/`, reconstructibles par
`uv run python -m src.download`. Constats établis le 22 septembre 2026 sur les
millésimes alors en ligne.

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

### Spécificités du calcul pour les écoles

- L'IPS d'une école est calculé sur les seuls **élèves de CM2**, dont les PCS
  sont connues lorsqu'ils entrent en sixième. C'est donc un indicateur
  **rétrospectif** : la moyenne des anciens élèves sur les cinq dernières
  années, pas une photographie des élèves actuellement scolarisés.
- Seules les écoles ayant compté **au moins 25 élèves de CM2 sur cinq ans**
  reçoivent un IPS. En dessous : `NS`.
- Les **écoles maternelles sont hors champ**, faute d'élèves de CM2. C'est ce
  qui explique l'écart entre les 48 360 écoles de l'annuaire et les ~32 500
  écoles du fichier IPS.
- Champ : écoles sous tutelle de l'Éducation nationale, publiques et privées
  **sous contrat**.

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
| `ips_ecoles.csv` | une école × une rentrée | 97 080 | 23 |
| `ips_colleges.csv` | un collège × une rentrée | 21 061 | 24 |
| `annuaire.csv` | un établissement (état courant) | 68 581 | 70 |

Les deux fichiers IPS sont des **panels** : chacun couvre trois rentrées.
Écoles 2022-23 → 2024-25, collèges 2023-24 → 2025-26. Rentrée commune la plus
récente : **2024-2025**.

L'annuaire n'a pas de dimension temporelle : c'est une photographie de l'état
actuel du réseau. Il couvre tous les types d'établissements (48 360 écoles,
9 183 collèges, 5 644 lycées, plus des services administratifs et
médico-sociaux).

---

## 1. `ips_ecoles.csv`

### Identification

| Colonne | Signification |
|---|---|
| `uai` | **Clé de l'établissement.** « Unité Administrative Immatriculée », ex. `0010093W`. Identifiant national officiel, unique et stable. Toujours 8 caractères : 7 chiffres suivis d'une lettre de contrôle (vérifié sur 100 % du fichier). Les **3 premiers chiffres codent le département** (99,5 % du fichier) ; les exceptions sont `620` → Corse-du-Sud (`2A`) et `720` → Haute-Corse (`2B`), héritage d'avant la partition de la Corse. C'est de ce préfixe que vient le `code_departement` à 3 caractères de l'annuaire. Clé de jointure avec l'annuaire. |
| `nom_de_l_etablissement` | Libellé en majuscules non accentuées, ex. `ECOLE PRIMAIRE PRIVEE SAINTE MARIE`. Beaucoup d'homonymes (`ECOLE PRIMAIRE` revient des milliers de fois) : **ne jamais joindre sur le nom**. |
| `num_ligne` | Numéro de ligne technique, unique sur tout le fichier. Aucune valeur analytique. |

### Temps

| Colonne | Signification |
|---|---|
| `rentree_scolaire` | `2022-2023`, `2023-2024` ou `2024-2025`. **À filtrer systématiquement**, sinon chaque école est comptée trois fois. |

### Localisation administrative

| Colonne | Signification |
|---|---|
| `code_region` / `region` | ⚠️ **Code de l'Éducation nationale, PAS le code INSEE.** Numérotation alphabétique : `01` = Auvergne-Rhône-Alpes, `02` = Bourgogne-Franche-Comté, `03` = Bretagne… Voir « Pièges » plus bas. |
| `code_de_l_academie` / `academie` | Académie de rattachement. 29 valeurs. Découpage propre à l'Éducation nationale, sans équivalent INSEE. |
| `code_du_departement` / `departement` | 2 caractères, ex. `01`, `51`. Inclut `2A` et `2B` (Corse) : **à garder en texte**, jamais en nombre. |
| `code_insee_de_la_commune` / `nom_de_la_commune` | 5 caractères, ex. `01004`. **C'est la bonne clé pour croiser avec l'INSEE** (revenu médian, population, contours communaux). |

### Caractéristique

| Colonne | Signification |
|---|---|
| `secteur` | `public` (83 481 lignes) ou `privé sous contrat` (13 599). Deux modalités seulement : le privé hors contrat n'est pas couvert. |

### La mesure

| Colonne | Signification |
|---|---|
| `ips` | **L'indice de position sociale de l'établissement.** Étendue observée en 2024-25 : 54,9 à 160,9, médiane 104,4. ⚠️ Peut valoir `NS` : 2 504 écoles en 2024-25, soit 7,7 %. D'après la DEPP, l'IPS n'est publié que pour les écoles ayant compté **au moins 25 élèves de CM2 sur les cinq dernières années** — `NS` désigne donc les écoles en dessous de ce seuil. **La colonne est du texte, pas un nombre.** |

### Valeurs de référence

Neuf colonnes : `ips_national`, `ips_national_public`, `ips_national_prive`, et
les mêmes déclinaisons en `ips_academique_*` et `ips_departemental_*`.

**Elles ne décrivent pas l'établissement.** Ce sont des moyennes de référence,
répétées à l'identique sur chaque ligne : une seule valeur nationale par
rentrée, une par académie, une par département. Vérifié.

Leur intérêt : positionner un établissement par rapport à son contexte. Un IPS
de 95 ne se lit pas pareil dans un département à 108 et dans un département à
92. Elles sont redondantes — tu pourrais les recalculer — mais pratiques.

---

## 2. `ips_colleges.csv`

Structure très proche, avec **cinq différences à connaître** :

| Différence | Détail |
|---|---|
| `ecart_type_de_l_ips` | **Colonne supplémentaire, absente des écoles.** Dispersion des IPS des élèves *au sein* du collège. Deux collèges de même IPS moyen peuvent être très différents : l'un socialement homogène, l'autre mélangeant des publics opposés. Variable précieuse pour parler de mixité sociale. |
| `region_insee` | **Présente ici, absente du fichier écoles.** C'est le vrai code INSEE (`44` = Grand Est). |
| `region_academique` | Remplace la colonne `region` des écoles. |
| `code_academie` | S'appelle `code_de_l_academie` dans le fichier écoles. Nommage incohérent entre les deux fichiers : ton code ne sera pas réutilisable tel quel. |
| `num_ligne` | Absente. |

Autre différence, invisible dans les noms de colonnes : **les collèges n'utilisent
pas `NS`**. Les valeurs absentes y sont de vraies valeurs manquantes (8 lignes).
Les deux fichiers codent l'absence différemment.

Étendue de l'IPS en 2024-25 : 56,0 à 162,5, médiane 103,6.
Répartition : 16 052 lignes publiques, 5 009 privées sous contrat.

---

## 3. `annuaire.csv`

70 colonnes, dont une vingtaine utiles ici. Taux de remplissage mesurés sur
l'ensemble du fichier.

| Colonne | Rempli | Signification |
|---|---|---|
| `identifiant_de_l_etablissement` | 100 % | **Le code UAI.** Nom différent de celui des fichiers IPS (`uai`), même contenu. ⚠️ 75 UAI apparaissent en double (157 lignes) : même établissement, deux libellés. Dédoublonner avant toute jointure. |
| `nom_etablissement` | 100 % | Libellé, ici en casse normale et accentué — contrairement aux fichiers IPS. |
| `type_etablissement` | 99,6 % | `Ecole`, `Collège`, `Lycée`, `EREA`, `Médico-social`, `Service Administratif`… Permet de filtrer. |
| `statut_public_prive` | 97,1 % | `Public` / `Privé`. Redondant avec `secteur` des fichiers IPS, et moins fiable (3 % de trous). Préférer `secteur`. |
| `latitude` / `longitude` | 99,4 % | **Coordonnées géographiques.** La raison d'être de ce fichier dans le projet. Bonne nouvelle : parmi les établissements appariés avec l'IPS, aucun n'en est dépourvu. |
| `precision_localisation` | 99,4 % | Qualité du géocodage, ex. `Numéro de rue`. Permet d'écarter les points mal localisés. |
| `appartenance_education_prioritaire` | 11,2 % | `REP` (4 826) ou `REP+` (2 831). ⚠️ **Le vide signifie « hors éducation prioritaire »**, ce n'est pas une donnée manquante. Variable de croisement à fort intérêt. |
| `code_commune` | 100 % | Code INSEE de la commune, 5 caractères. |
| `code_departement` | 100 % | ⚠️ **3 caractères** (`093`), alors que les fichiers IPS en utilisent 2 (`93`). Voir « Pièges ». |
| `code_region` | 100 % | ⚠️ Code **INSEE** ici (`11` = Île-de-France), contrairement aux fichiers IPS. |
| `etat` | 100 % | `OUVERT` (68 579) ou `A FERMER` (2). |
| `date_ouverture` | 100 % | Format `1971-05-24`. |
| `ecole_maternelle` / `ecole_elementaire` | 70,5 % | Indicateurs `0`/`1`. Remplis pour les écoles seulement. |
| `segpa`, `ulis` | 22 % / 93 % | Présence de dispositifs adaptés. |

---

## Pièges de jointure

Quatre incohérences entre fichiers, toutes vérifiées. Ce sont elles qui
produisent des bugs silencieux — un résultat qui semble plausible mais qui est
faux.

**1. Le code région des fichiers IPS n'est pas le code INSEE.**

| Région | `code_region` (IPS) | Code INSEE |
|---|---|---|
| Auvergne-Rhône-Alpes | `01` | `84` |
| Bourgogne-Franche-Comté | `02` | `27` |
| Bretagne | `03` | `53` |
| Grand Est | `06` | `44` |

L'Éducation nationale numérote ses régions dans l'ordre alphabétique. Joindre
des données INSEE sur cette colonne associerait Auvergne-Rhône-Alpes à la
Guadeloupe. Le fichier collèges fournit `region_insee` ; **le fichier écoles
n'a pas d'équivalent** — il faut passer par le code commune ou par une table de
correspondance.

**2. Les codes département n'ont pas le même format.** `93` dans les fichiers
IPS, `093` dans l'annuaire. Une jointure directe ne rapprocherait rien.

**3. Les UAI en double dans l'annuaire.** Une jointure naïve dupliquerait des
lignes IPS. Le nombre d'établissements augmenterait sans explication apparente.

**4. Les colonnes ne portent pas les mêmes noms.** `uai` vs
`identifiant_de_l_etablissement`, `code_du_departement` vs `code_departement`,
`code_de_l_academie` vs `code_academie`.

---

## Ce que les données ne contiennent pas

- **Aucun effectif d'élèves**, ni dans les fichiers IPS ni dans l'annuaire. On
  ne peut donc pas pondérer les moyennes par la taille des établissements :
  une école de 30 élèves pèse autant qu'une école de 400 dans une moyenne
  départementale. À documenter dans les limites.
- **Aucun indicateur de résultats scolaires.** L'IPS décrit l'origine sociale,
  pas la performance.
- **Le privé hors contrat** est absent.
- **Les lycées** : présents dans l'annuaire, mais leur fichier IPS n'est pas
  téléchargé ici. Extension possible.

---

## Autres jeux IPS disponibles au catalogue

Le catalogue du ministère (306 jeux de données) contient plusieurs variantes
IPS. Les deux retenues ici ne sont pas les seules :

| Identifiant | Rentrées couvertes | Remarque |
|---|---|---|
| `fr-en-ips-ecoles-ap2022` *(utilisé)* | 2022-23 → 2024-25 | ⚠️ **« Ce jeu de données n'est plus actualisé »** (avertissement officiel) |
| `donnees-ips-ecoles` | 2016-17 → **2024-25** | 9 rentrées, effectifs légèrement différents |
| `fr-en-ips_ecoles_v2` | 2016-17 → 2021-22 | ancienne méthodologie uniquement |
| `fr-en-ips-colleges-ap2023` *(utilisé)* | 2023-24 → 2025-26 | |
| `donnees-ips-lycees` | 2016-17 → 2024-25 | lycées, non téléchargé |
| `fr-en-ips-erea-ap2022` | — | EREA |

**Le piège de la série longue.** `donnees-ips-ecoles` couvre neuf rentrées et
paraît donc préférable. Mais il enjambe la rupture méthodologique de 2022 :
comparer 2016-17 à 2024-25 sur ce fichier reviendrait à comparer deux indices
construits différemment. Si cette source est retenue, la rupture doit être
traitée explicitement — pas ignorée parce que les colonnes se ressemblent.

---

## Appariement IPS ↔ annuaire (rentrée 2024-2025)

| | Appariés | Total | Taux |
|---|---|---|---|
| Écoles | 32 199 | 32 494 | **99,1 %** |
| Collèges | 6 975 | 6 987 | **99,8 %** |

Les 295 écoles non appariées ne sont pas réparties au hasard : petites écoles
rurales, concentrées dans le Pas-de-Calais (17), la Seine-Maritime (14), la
Charente-Maritime (12). Vraisemblablement fermées ou regroupées entre la
collecte de l'IPS et la mise à jour de l'annuaire.
