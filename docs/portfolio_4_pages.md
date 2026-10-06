# Portfolio imprimé — structure des 4 pages

Document de travail. Il fixe **ce que dit chaque page** et **ce qu'elle contient**, avant
d'écrire la moindre ligne de Typst. Le « percutant » se joue ici, pas dans l'outil.

---

## La contrainte qui commande tout le plan

Une page A4 fait 29,7 cm de haut. Avec 2 cm de marge en haut et en bas, il reste
**25,7 cm**. Les figures du dépôt, ramenées à la largeur utile de **17 cm**, occupent :

| Famille de figures | Hauteur à 17 cm | Part de la page |
|---|---:|---:|
| Figures larges à deux panneaux | 9,6 à 12,6 cm | 37 à 49 % |
| Nuages de points | 16,0 à 16,7 cm | 62 à 65 % |
| Cartes à un seul panneau | 19,3 à 20,5 cm | 75 à 80 % |

**Conséquence : une carte à panneau unique mange une page entière et ne laisse aucune
place au texte.** Les quatre figures retenues ci-dessous sont donc toutes des figures
larges — ce ne sont pas les plus jolies à l'écran, ce sont les seules qui tiennent sur
du papier à côté d'un propos.

### Les notes de figure ne survivront pas

Dans matplotlib, **une taille de police est une taille physique**. Une figure enregistrée
en 14 pouces de large et placée sur 17 cm est réduite de moitié, et tout son texte avec.

| Figure | Largeur d'origine | Réduction | Note à 7,5 pt devient |
|---|---:|---:|---:|
| `distribution_ips` | 27,9 cm | ×0,61 | 4,6 pt |
| `ecarts_significatifs` | 33,0 cm | ×0,52 | 3,9 pt |
| `rep_plus_ecart` | 35,6 cm | ×0,48 | 3,6 pt |
| `matrices_classement_marges` | 36,1 cm | ×0,47 | 3,5 pt |

En dessous de 8 pt on ne lit plus. **Les notes de bas de figure doivent donc sortir des
images et devenir du texte de page.** Ce n'est pas une perte : sur papier, une note
reprise à côté de la figure se lit mieux qu'une note incrustée dedans.

Deux façons de procéder, au choix :

1. **Sans toucher au code** — on recadre à l'export, ou on laisse la note illisible et on
   la réécrit à côté. Rapide, un peu sale.
2. **Variantes « impression »** — on régénère les quatre figures en `figsize` de 17 cm de
   large, sans note incrustée. Les polices retombent alors à leur taille réelle. Plus
   propre, demande de modifier les modules concernés.

---

## Page 1 — Le principe et le résultat

> **Message :** le seuil n'est pas choisi, il découle du budget. Et à ce seuil, le
> dispositif est largement cohérent.

**Bandeau d'ouverture — quatre chiffres, gros**

| | |
|---|---|
| **5 325** | collèges publics, rentrée 2024-2025 |
| **1 094** | places en éducation prioritaire |
| **90,6 %** | de collèges dont le classement est conforme |
| **2** | étalons indépendants confrontés |

**Le principe, en trois phrases.** Le dispositif classe 1 094 collèges sur 5 325. Une
règle qui classerait le même *nombre* d'établissements d'après le seul IPS retiendrait
les 1 094 IPS les plus faibles, soit tous ceux sous **88,80 points**. Ce seuil n'est donc
pas une convention : il découle de la décision budgétaire elle-même.

C'est l'argument méthodologique du projet et il doit être lisible en dix secondes. Tout
le reste en dépend.

**Figure :** `distribution_ips.png` — 12,1 cm. Elle montre la distribution et la position
des seuils d'un seul coup d'œil : c'est le principe rendu visible.

**Encadré bas de page — « Ce que ce travail ne dit pas ».** Deux lignes, pas plus :
l'IPS n'est pas le critère officiel de classement, qui repose sur un indice non public.
Un écart mesure donc **un désaccord entre deux instruments, jamais une erreur
administrative**.

> Placer cette réserve en page 1 plutôt qu'en page 4 est un choix délibéré. En entretien,
> c'est elle qui montre que tu sais ce que ton chiffre vaut.

**À écrire par toi :** le paragraphe d'accroche, 3 à 4 lignes, qui pose la question.

---

## Page 2 — Où sont les écarts, et pourquoi Paris n'est pas une erreur

> **Message :** les deux types d'écart n'ont ni la même géographie ni la même cause, et
> le cas le plus spectaculaire est une contrainte arithmétique, pas une faute.

**Figure :** `ecarts_significatifs.png` — 11,5 cm. Deux panneaux : la **fréquence** des
écarts à gauche, leur **nature** à droite.

**Le texte doit porter le point de lecture** que la note incrustée ne pourra plus porter :
chaque collège compté pèse au moins 3 points d'IPS, donc une moyenne proche de zéro ne
veut pas dire « peu d'écart » mais « autant dans un sens que dans l'autre ».

**Le contraste à montrer**, en deux lignes :

| | Fréquence | Moyenne signée | Lecture |
|---|---:|---:|---|
| Guadeloupe | 19,6 % | **+0,8** | les deux types se compensent |
| Paris | 16,7 % | **−13,7** | des sur-inclusions, et rien d'autre |

Même fréquence, diagnostic opposé. C'est l'argument pour deux cartes plutôt qu'une.

**Encadré « Paris » — le morceau de bravoure de la page.**

Paris ne compte que **6 collèges sous le seuil national pour 30 places à pourvoir**. Le
minimum de sur-inclusions arithmétiquement possible y est donc de **24** — exactement le
nombre observé. Aucune carte parisienne à 30 collèges ne ferait mieux au regard d'un
étalon national. Recalculé à l'intérieur de Paris, à enveloppe inchangée, le nombre tombe
de 24 à 8.

> C'est le passage qui distingue le plus un analyste d'un producteur de graphiques :
> savoir reconnaître qu'un écart spectaculaire est **imposé par la structure du problème**
> et non par une mauvaise décision.

**À écrire par toi :** ta lecture de l'opposition entre une géographie dispersée (les
sur-inclusions) et une géographie continue et périphérique (les oublis).

---

## Page 3 — Deux approfondissements qui changent la lecture

> **Message :** resserré sur REP+, le mot « oubli » ne veut plus dire la même chose ; et
> un second étalon indépendant ne confirme pas le premier.

### 3a. REP+ : une question de graduation, pas de couverture

**Figure :** `rep_plus_ecart.png` — 9,6 cm, la plus compacte du dépôt.

Le fait, en une phrase : **sur les 101 collèges que l'IPS désigne sans que REP+ les
retienne, 90 sont déjà classés REP.** Onze seulement sont hors éducation prioritaire.

Un « oubli » ne signifie donc presque jamais que l'État n'a rien fait : il signifie qu'il
a mis **REP là où l'IPS dirait REP+**. On passe d'une question de couverture à une
question de graduation.

| | REP et REP+ | REP+ seul |
|---|---:|---:|
| Places | 1 094 | 362 |
| Seuil d'IPS | 88,80 | **77,80** |
| Collèges bien placés | 76,8 % | **72,1 %** |

### 3b. Un second étalon ne confirme pas le premier

Pas de figure : **le résultat tient dans deux nombres, et un nombre qui tient dans une
phrase ne mérite pas une image sur un document de quatre pages.**

Les évaluations nationales de début de 6ᵉ fournissent un étalon indépendant de l'IPS,
mesuré sur les élèves eux-mêmes. Confrontés académie par académie, les deux ne
s'accordent pas : **la moitié des académies changent de côté** et les deux ratios ne
corrèlent qu'à **+0,31**.

Mentionner aussi, en une ligne, que les bornes d'interprétation ont été **reconstruites**
pour ce second étalon plutôt que reprises de l'IPS : 8 points, soit deux erreurs-types de
la moyenne d'un collège. Reprendre les 3 points de l'IPS aurait fait paraître le score de
6ᵉ deux fois plus en désaccord qu'il ne l'est.

**À écrire par toi :** ce que tu conclus du désaccord entre les deux instruments.

---

## Page 4 — Synthèse, et ce qu'on ne peut pas savoir

> **Message :** en tenant compte de ce que les instruments ne permettent pas de trancher,
> il reste un désaccord réel — et les politiques qui corrigeraient le problème sont
> précisément celles dont les données ne sortent pas.

**Figure :** `matrices_classement_marges.png` — 10,8 cm. Les trois niveaux croisés d'un
coup, marges d'interprétation comprises.

**Le tableau de synthèse :**

| | Sans marge | Avec marges |
|---|---:|---:|
| IPS — diagonale | 87,0 % | **93,5 %** |
| IPS — kappa pondéré | 0,70 | **0,85** |
| Score de 6ᵉ — diagonale | 81,2 % | **94,2 %** |
| Score de 6ᵉ — kappa pondéré | 0,55 | **0,83** |

**La phrase qui doit rester :** cette amélioration n'est pas un résultat, c'est le prix de
l'aveu d'imprécision. On cesse de compter comme désaccords des cas sur lesquels on ne peut
pas se prononcer. Ce qui **reste** hors diagonale, en revanche, compte : **348 collèges**
au sens de l'IPS sont franchement du mauvais côté d'un seuil, au-delà de ce que
l'instrument autorise.

**Clôture — l'asymétrie des données ouvertes.** Trois dispositifs gradués existent et
corrigeraient l'effet de seuil mesuré ici : les contrats locaux d'accompagnement,
l'allocation progressive des moyens, les groupes de besoins. **Aucun ne publie la liste
des établissements concernés**, alors que le dispositif binaire est entièrement public.

> C'est la meilleure fin possible : elle est mémorable, elle ne se termine pas sur une
> liste de limites, et elle montre que tu penses au-delà de ton propre jeu de données.

**Pied de page :** lien du dépôt, éventuellement un QR code, et la mention des sources
(DEPP, annuaire de l'éducation, contours Insee/cartiflette).

**À écrire par toi :** ta conclusion, 3 lignes.

---

## Ce qui est volontairement laissé de côté

Garder quatre pages suppose de renoncer. Les abandons assumés :

- **Les cartes académiques de ratio** (19,5 cm) — superbes, mais elles coûtent une page
  entière chacune. Leur message passe dans le texte de la page 2.
- **Le second volet cartographique de REP+** — redondant avec la page 3 une fois le fait
  des 90 oublis déjà REP énoncé.
- **Le nuage des deux étalons** — remplacé par ses deux nombres, voir 3b.
- **Les figures `_eval6`** — le second étalon est présent comme argument, pas comme
  galerie. Doubler chaque visuel doublerait le document.
- **La partie « autres politiques »** du README — réduite à la clôture de la page 4.

---

## Récapitulatif des figures retenues

| Page | Figure | Hauteur à 17 cm |
|---:|---|---:|
| 1 | `distribution_ips.png` | 12,1 cm |
| 2 | `ecarts_significatifs.png` | 11,5 cm |
| 3 | `rep_plus_ecart.png` | 9,6 cm |
| 4 | `matrices_classement_marges.png` | 10,8 cm |

Quatre figures, une par page, toutes au format large. Le reste de chaque page est du
texte, des chiffres et des encadrés.

---

## Produire le PDF

`typst` est déclaré dans `pyproject.toml` (groupe `dev`), donc figé dans `uv.lock` comme
le reste de la chaîne : `uv sync` suffit à quiconque clone le dépôt.

Pour l'aperçu en direct pendant la mise en page, installer en plus le binaire :

```
winget install Typst.Typst
typst watch docs/portfolio.typ
```

Le PDF se régénère à chaque sauvegarde.
