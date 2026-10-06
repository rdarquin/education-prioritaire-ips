// =============================================================================
// Portfolio imprime — 4 pages A4
// Structure : docs/portfolio_4_pages.md
//
// Compilation :  uv run python -m src.portfolio
// Apercu vivant : typst watch docs/portfolio.typ   (binaire installe a part)
//
// LES FIGURES NE SONT PAS MODIFIEES. Leurs notes de bas de figure, illisibles
// une fois reduites a la largeur d'une page, sont ROGNEES ici par une boite
// `clip: true`, et leur contenu est reecrit dans le texte des pages. Pour
// ajuster une coupe, il suffit de changer le second nombre passe a `coupe`.
// =============================================================================

#let ENCRE = rgb("#0b0b0b")
#let ENCRE_2 = rgb("#52514e")
#let MUET = rgb("#898781")
#let GRILLE = rgb("#e1e0d9")
#let BLEU = rgb("#1f3b73")
#let ORANGE = rgb("#c9551d")
#let FOND = rgb("#f6f5f1")

#set page(
  paper: "a4",
  margin: (x: 1.9cm, top: 1.5cm, bottom: 1.4cm),
  footer: context {
    set text(size: 7pt, fill: MUET)
    grid(
      columns: (1fr, auto),
      align: (left, right),
      [Rémy Darquin — github.com/rdarquin/education-prioritaire-ips],
      [#counter(page).display() / 4],
    )
  },
)

#set text(font: ("Segoe UI", "DejaVu Sans"), size: 8.8pt, fill: ENCRE, lang: "fr")
#set par(justify: true, leading: 0.62em, spacing: 0.9em)

// -----------------------------------------------------------------------------
// Composants
// -----------------------------------------------------------------------------

// Titre de page : un filet de couleur, un titre, une ligne de cadrage.
#let titre_page(numero, titre, cadrage) = {
  block(spacing: 0.7em)[
    #text(size: 7.5pt, weight: "bold", fill: ORANGE, tracking: 0.08em)[
      #upper(numero)
    ]
    #v(-0.45em)
    #text(size: 17pt, weight: "bold", fill: ENCRE)[#titre]
    #v(-0.3em)
    #text(size: 9.2pt, fill: ENCRE_2)[#cadrage]
  ]
  line(length: 100%, stroke: 0.8pt + ENCRE)
  v(0.2em)
}

// Un chiffre qui doit se lire a trois metres.
#let chiffre(valeur, libelle) = align(center)[
  #text(size: 21pt, weight: "bold", fill: BLEU)[#valeur]
  #v(-0.55em)
  #text(size: 7.4pt, fill: ENCRE_2)[#libelle]
]

// Encadre : un filet epais a gauche, un fond tres pale.
#let encadre(titre, corps, couleur: BLEU) = block(
  width: 100%,
  fill: FOND,
  stroke: (left: 2.2pt + couleur),
  inset: (left: 9pt, rest: 7pt),
  radius: (right: 2pt),
)[
  #text(size: 8.4pt, weight: "bold", fill: couleur)[#titre]
  #v(-0.35em)
  #set text(size: 8.2pt)
  #corps
]

// Emplacement reserve au commentaire de Remy.
#let a_toi(consigne) = block(
  width: 100%,
  stroke: (paint: MUET, thickness: 0.5pt, dash: "dashed"),
  inset: 6pt,
  radius: 2pt,
)[
  #text(size: 7.6pt, fill: MUET, style: "italic")[À écrire — #consigne]
]

// Figure rognee de sa note de bas de figure.
//   ratio = hauteur / largeur de l'image d'origine, en pixels
//   garde = part de la hauteur conservee (le reste est la note, rognee)
// LE PIEGE : une image dont seule la largeur est fixee se laisse REDUIRE pour
// tenir dans une boite plus courte qu'elle. On obtient alors la figure
// entiere, note comprise, simplement rapetissee — l'inverse du rognage voulu.
// Il faut donc imposer AUSSI sa hauteur naturelle : l'image deborde alors la
// boite, et `clip` coupe le bas.
//
// `place` la sort du flux, pour que ce debordement ne pousse rien.
#let coupe(chemin, ratio, garde) = context {
  let l = page.width - 3.8cm
  box(
    width: l,
    height: l * ratio * garde,
    clip: true,
    place(top + left, image(chemin, width: l, height: l * ratio)),
  )
}

// Legende : ce que la note rognee disait, reecrit a taille lisible.
#let legende(corps) = {
  v(0.15em)
  text(size: 7.4pt, fill: ENCRE_2)[#corps]
}

#let tableau(entetes, lignes, alignements) = {
  set text(size: 8pt)
  table(
    columns: alignements.len(),
    align: alignements,
    stroke: none,
    inset: (x: 5pt, y: 3.4pt),
    fill: (_, y) => if y == 0 { none } else if calc.odd(y) { FOND } else { none },
    table.hline(stroke: 0.7pt + ENCRE),
    ..entetes.map(e => text(weight: "bold", size: 7.6pt)[#e]),
    table.hline(stroke: 0.5pt + GRILLE),
    ..lignes.flatten(),
    table.hline(stroke: 0.7pt + ENCRE),
  )
}

// =============================================================================
// PAGE 1 — Le principe et le résultat
// =============================================================================

#titre_page(
  "Page 1 — le principe",
  "Le seuil n'est pas choisi.\nIl découle du budget.",
  [Classement en éducation prioritaire et réalité sociale des collèges publics —
   données DEPP, rentrée 2024-2025.],
)

#v(0.3em)

#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  gutter: 6pt,
  chiffre("5 325", "collèges publics"),
  chiffre("1 094", "places en éducation prioritaire"),
  chiffre("90,6 %", "de classements conformes"),
  chiffre("2", "étalons indépendants confrontés"),
)

#v(0.4em)
#line(length: 100%, stroke: 0.5pt + GRILLE)
#v(0.2em)

Le dispositif classe 1 094 collèges sur 5 325. Une règle qui classerait le même
*nombre* d'établissements d'après le seul indice de position sociale retiendrait les
1 094 IPS les plus faibles — c'est-à-dire tous ceux situés sous *88,80 points*, l'IPS du
collège qui ferme l'enveloppe.

*Ce seuil n'est donc pas une convention : il découle de la décision budgétaire
elle-même.* Chaque collège reçoit alors un score : zéro s'il est classé et sous le seuil,
ou non classé et au-dessus ; sinon, son écart au seuil. Deux cas de sens opposé —
l'*oubli* et la *sur-inclusion*.

#v(0.2em)

#coupe("../outputs/figures/distribution_ips.png", 0.70909, 0.827)

#legende[
  Distribution de l'IPS des 5 325 collèges publics. Le trait vertical marque le seuil
  budgétaire national ; le peigne du bas donne le seuil propre à chaque académie, calculé
  sur sa seule enveloppe. L'écart entre ces seuils académiques et le seuil national est
  la première mesure de l'inégalité territoriale du dispositif.
]

#v(0.3em)

#grid(
  columns: (1fr, 1fr),
  gutter: 9pt,
  encadre(
    "Pourquoi un seuil endogène",
    [Fixer un seuil à 10 % ou à 90 points serait arbitraire, et le résultat varierait
     avec ce choix : le nombre de collèges non couverts va de 4 à 409 selon la
     convention retenue. En déduisant le seuil de l'enveloppe réellement distribuée, on
     supprime ce degré de liberté — et la somme des écarts devient une identité
     vérifiable, contrôlée à chaque exécution.],
  ),
  encadre(
    "Ce que ce travail ne dit pas",
    [L'IPS *n'est pas* le critère officiel de classement. Celui-ci repose sur un indice
     composite construit par régression, dont ni la spécification, ni les coefficients,
     ni le seuil ne sont publics. Un écart mesure donc *un désaccord entre deux
     instruments*, jamais une erreur administrative.],
    couleur: ORANGE,
  ),
)

#v(0.3em)
#a_toi[l'accroche, 3 à 4 lignes : la question posée et pourquoi elle se pose.]

// =============================================================================
// PAGE 2 — La géographie des écarts
// =============================================================================

#pagebreak()

#titre_page(
  "Page 2 — la géographie",
  "Deux types d'écart,\ndeux géographies.",
  [Et le cas le plus spectaculaire n'est pas une faute : c'est une contrainte
   arithmétique.],
)

Les deux cartes ne sélectionnent rien : elles portent sur *tous* les collèges dont
l'écart dépasse 3 points d'IPS — le seuil en deçà duquel la DEPP recommande de ne rien
interpréter. À gauche, la *fréquence* de ces écarts ; à droite, leur *nature*.

#v(0.1em)

#coupe("../outputs/figures/ecarts_significatifs.png", 0.67692, 0.864)

#legende[
  Classes de couleur : quantiles de la distribution départementale, et non échelle
  linéaire — quelques départements extrêmes écraseraient sinon tous les autres. En gris,
  les départements dont l'effectif ne permet pas le calcul : moins de 20 collèges publics
  à gauche, moins de trois collèges significatifs à droite.
]

#v(0.35em)

#grid(
  columns: (1.05fr, 1fr),
  gutter: 11pt,
  [
    *Le point de lecture.* Chaque collège compté pèse au moins 3 points en valeur
    absolue. Une moyenne proche de zéro ne signifie donc pas « peu d'écart », mais
    *autant dans un sens que dans l'autre*.

    #v(-0.2em)

    #tableau(
      ([], [Fréquence], [Moyenne], [Lecture]),
      (
        ([Guadeloupe], [19,6 %], [#text(fill: BLEU, weight: "bold")[+0,8]],
         [les deux types se compensent]),
        ([Paris], [16,7 %], [#text(fill: ORANGE, weight: "bold")[−13,7]],
         [des sur-inclusions, rien d'autre]),
      ),
      (left, right, right, left),
    )

    #v(-0.2em)

    Même fréquence, diagnostic opposé. C'est l'argument pour deux cartes plutôt qu'une.

    Les deux géographies diffèrent aussi dans leur forme : les sur-inclusions sont un
    semis dispersé, sans continuité territoriale ; les oublis dessinent un arc
    périphérique continu — Nord, Nord-Est, sillon rhodanien, arc méditerranéen.
  ],
  encadre(
    "Paris : 24 sur-inclusions, et aucune autre carte possible",
    [La répartition des réseaux par académie est arrêtée au niveau national ; le recteur
     désigne ensuite les établissements dans l'enveloppe reçue.

     Or Paris ne compte que *6 collèges sous le seuil national pour 30 places à
     pourvoir*. Le minimum de sur-inclusions arithmétiquement possible y est donc de
     *24* — exactement le nombre observé.

     Aucune carte parisienne à 30 collèges ne ferait mieux au regard d'un étalon
     national. Recalculé à l'intérieur de Paris, à enveloppe inchangée, le nombre tombe
     de 24 à *8*.

     L'écart ne mesure pas ici une décision locale, mais la contrainte que le niveau
     national lui impose.],
    couleur: ORANGE,
  ),
)

#v(0.3em)
#a_toi[ta lecture du contraste entre les deux géographies.]

// =============================================================================
// PAGE 3 — Deux approfondissements
// =============================================================================

#pagebreak()

#titre_page(
  "Page 3 — deux approfondissements",
  "« Oubli » ne veut pas dire\nce qu'on croit.",
  [Resserré sur REP+, le mot change de sens. Et un second étalon ne confirme pas le
   premier.],
)

#text(size: 10.5pt, weight: "bold", fill: BLEU)[
  1. Une question de graduation, pas de couverture
]

#v(-0.3em)

Le second volet réduit l'enveloppe aux 362 places REP+ et repose exactement la même
question. La mécanique ne change pas d'une ligne : seule la définition de « classé »
change, et le seuil devient plus sélectif — 77,80 points d'IPS au lieu de 88,80.

#v(0.1em)

#coupe("../outputs/figures/rep_plus_ecart.png", 0.56429, 0.765)

#legende[
  Distribution de l'écart au seuil REP+, pour les deux étalons. La couleur distingue les
  oublis déjà classés REP des oublis hors éducation prioritaire — sans quoi le mot serait
  trompeur.
]

#v(0.3em)

#grid(
  columns: (1fr, 0.82fr),
  gutter: 11pt,
  encadre(
    "Le résultat propre à ce volet",
    [Sur les *101 collèges* que l'IPS désigne sans que REP+ les retienne, *90 sont déjà
     classés REP*. Onze seulement sont hors éducation prioritaire.

     Un « oubli » ne signifie donc presque jamais que l'État n'a rien fait : il signifie
     qu'il a mis *REP là où l'IPS dirait REP+*. On passe d'une question de *couverture* —
     qui est aidé — à une question de *graduation* — qui est aidé au bon niveau.],
  ),
  tableau(
    ([], [REP et REP+], [REP+ seul]),
    (
      ([Places], [1 094], [#text(weight: "bold")[362]]),
      ([Seuil d'IPS], [88,80], [#text(weight: "bold")[77,80]]),
      ([Bien placés], [76,8 %], [#text(weight: "bold")[72,1 %]]),
      ([Écarts par côté], [254], [#text(weight: "bold")[101]]),
    ),
    (left, right, right),
  ),
)

#v(0.45em)

#text(size: 10.5pt, weight: "bold", fill: BLEU)[
  2. Un second étalon ne confirme pas le premier
]

#v(-0.3em)

Les évaluations nationales de début de 6#super[e] fournissent un étalon *indépendant de
l'IPS*, mesuré sur les élèves eux-mêmes et non sur la profession de leurs parents. Elles
ont lieu en septembre : le score mesure le niveau *à l'arrivée*, avant que
l'établissement n'ait rien produit — il n'est donc pas contaminé par les moyens reçus au
titre de l'éducation prioritaire.

Confrontés académie par académie, les deux instruments ne s'accordent pas : *la moitié
des académies changent de côté*, et les deux ratios d'enveloppe ne corrèlent qu'à
*+0,31*.

#encadre(
  "Les bornes du second étalon ont été reconstruites, pas reprises",
  [La DEPP recommande de ne pas interpréter un écart d'IPS inférieur à *3 points*. Elle ne
   publie aucun seuil équivalent pour le score de 6#super[e] — mais elle publie
   l'écart-type des élèves de chaque collège, ce qui permet de le construire : 46 points
   en médiane pour 113 élèves évalués, soit une erreur-type de 4,3 sur la moyenne du
   collège. Deux erreurs-types donnent *8 points*.

   Reprendre les 3 points de l'IPS aurait été une faute : ces bornes plaçaient 8,9 % des
   collèges hors de la bande centrale contre 4,8 % pour l'IPS, faisant paraître le score
   de 6#super[e] deux fois plus en désaccord qu'il ne l'est — uniquement parce qu'elles
   sont trop serrées pour une mesure plus bruitée.],
  couleur: ORANGE,
)

#v(0.25em)
#a_toi[ce que tu conclus du désaccord entre les deux instruments.]

// =============================================================================
// PAGE 4 — Synthèse
// =============================================================================

#pagebreak()

#titre_page(
  "Page 4 — synthèse",
  "Ce qui reste vrai\nune fois l'imprécision avouée.",
  [Les trois niveaux croisés d'un coup, marges d'interprétation comprises.],
)

Chaque étalon réaffecte les collèges *à enveloppes inchangées* : les 362 plus bas
deviennent REP+, les 732 suivants REP, le reste hors éducation prioritaire. Ce n'est pas
un classifieur comparé à une vérité, mais une *réallocation sous la même contrainte
budgétaire*. Les collèges tombant dans la marge d'aveuglement de l'instrument — ±3 points
d'IPS, ±8 points de score de 6#super[e] — ont plusieurs niveaux plausibles : leur
classement observé ne peut pas être contredit s'il figure parmi eux.

#v(0.1em)

#coupe("../outputs/figures/matrices_classement_marges.png", 0.63380, 0.729)

#legende[
  Lignes : le niveau attendu au sens de l'étalon. Colonnes : le niveau réellement
  observé, dont les totaux sont les enveloppes réelles. La diagonale est l'accord.
]

#v(0.3em)

#grid(
  columns: (0.85fr, 1fr),
  gutter: 11pt,
  tableau(
    ([], [Sans marge], [Avec marges]),
    (
      ([IPS — diagonale], [87,0 %], [#text(weight: "bold")[93,5 %]]),
      ([IPS — kappa pondéré], [0,70], [#text(weight: "bold")[0,85]]),
      ([6#super[e] — diagonale], [81,2 %], [#text(weight: "bold")[94,2 %]]),
      ([6#super[e] — kappa pondéré], [0,55], [#text(weight: "bold")[0,83]]),
    ),
    (left, right, right),
  ),
  [
    *Cette amélioration n'est pas un résultat* : c'est le prix de l'aveu d'imprécision. On
    cesse simplement de compter comme désaccords des cas sur lesquels on ne peut pas se
    prononcer.

    Ce qui *reste* hors diagonale, en revanche, compte : *348 collèges* au sens de l'IPS
    sont franchement du mauvais côté d'un seuil, au-delà de ce que l'instrument autorise.
    Ce sont les seuls cas sur lesquels ce travail se prononce.
  ],
)

#v(0.3em)

#encadre(
  "Pour finir : les dispositifs gradués sont ceux dont les données ne sortent pas",
  [Trois politiques corrigeraient précisément l'effet de seuil mesuré ici — les *contrats
   locaux d'accompagnement*, qui remplacent le label binaire par une aide contractuelle et
   progressive ; l'*allocation progressive des moyens*, qui module la dotation horaire par
   établissement ; les *groupes de besoins* de la rentrée 2024, soit exactement le
   millésime analysé.

   *Aucune ne publie la liste des établissements concernés*, alors que le dispositif
   binaire, lui, est entièrement public. Ce n'est pas neutre pour qui veut évaluer le
   ciblage des moyens — et cela limite d'avance toute analyse, y compris celle-ci.],
  couleur: ORANGE,
)

#v(0.3em)

#grid(
  columns: (1fr, 1fr),
  gutter: 11pt,
  [
    #text(size: 7.8pt, weight: "bold")[Ce que ce travail ne prétend pas faire]
    #v(-0.4em)
    #text(size: 7.6pt, fill: ENCRE_2)[
      Aucune relation causale n'est établie ; l'analyse est descriptive. Aucune
      pondération par les effectifs d'élèves n'est possible — les résultats décrivent une
      part de *collèges*, jamais une part d'*élèves*. Une seule rentrée est analysée. Le
      premier degré et le privé sous contrat sont hors champ.
    ]
  ],
  [
    #text(size: 7.8pt, weight: "bold")[Données et reproduction]
    #v(-0.4em)
    #text(size: 7.6pt, fill: ENCRE_2)[
      IPS des collèges, annuaire de l'éducation et évaluations nationales de 6#super[e]
      (DEPP, data.education.gouv.fr) ; contours Insee / cartiflette. Chaîne complète en
      Python, versions figées, données reconstruites depuis l'API du ministère :
      *github.com/rdarquin/education-prioritaire-ips*
    ]
  ],
)

#v(0.2em)
#a_toi[ta conclusion, 3 lignes.]
