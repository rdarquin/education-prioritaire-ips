// =============================================================================
// Plaquette imprimee — 4 pages A4
//
// Variante de `portfolio.typ`, meme contenu, autre registre de lecture.
// `portfolio.typ` est un document DENSE : 300 a 500 mots par page, un
// raisonnement que le lecteur peut reconstituer et contester, lu assis.
// Celui-ci est une PLAQUETTE : environ 150 mots par page, une seule idee
// dominante, lue debout en trente secondes.
//
// Ce qui change concretement :
//   - un message par page, affiche en grand, au lieu d'un argument qui progresse
//   - les encadres secondaires disparaissent ou tombent a trois lignes
//   - les figures sont rognees EN HAUT aussi : leur titre ferait doublon avec
//     celui de la page, qui le dit en plus gros
//   - le blanc devient un element de mise en page, pas une chute
//
// Compilation : uv run python -m src.portfolio
// =============================================================================

#let ENCRE = rgb("#0b0b0b")
#let ENCRE_2 = rgb("#52514e")
#let MUET = rgb("#898781")
#let GRILLE = rgb("#e1e0d9")
#let BLEU = rgb("#1f3b73")
#let ORANGE = rgb("#c9551d")
#let FOND = rgb("#f6f5f1")

#let MARGE_X = 2.0cm

#set page(
  paper: "a4",
  // Bas plus genereux que haut : le dernier bloc est pousse au ras de la
  // marge par les ressorts `1fr`, et viendrait sinon toucher le pied de page.
  margin: (x: MARGE_X, top: 1.8cm, bottom: 2.1cm),
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

#set text(font: ("Segoe UI", "DejaVu Sans"), size: 9.6pt, fill: ENCRE, lang: "fr")
#set par(justify: false, leading: 0.78em, spacing: 1.1em)

// -----------------------------------------------------------------------------
// Composants
// -----------------------------------------------------------------------------

// Le titre occupe le haut de la page et porte a lui seul le message.
#let ouverture(numero, titre, sous_titre) = {
  block(spacing: 0pt)[
    #text(size: 7.5pt, weight: "bold", fill: ORANGE, tracking: 0.12em)[
      #upper(numero)
    ]
    #v(0.55em)
    #text(size: 25pt, weight: "bold", fill: ENCRE)[#titre]
    #v(0.5em)
    #text(size: 11.5pt, fill: ENCRE_2)[#sous_titre]
  ]
  v(0.6em)
  line(length: 100%, stroke: 0.8pt + ENCRE)
  v(0.5em)
}

// L'idee de la page, affichee et non expliquee.
#let affiche(corps) = {
  v(0.1em)
  text(size: 13pt, fill: BLEU, weight: "semibold")[#corps]
  v(0.1em)
}

#let chiffre(valeur, libelle) = align(center)[
  #text(size: 30pt, weight: "bold", fill: BLEU)[#valeur]
  #v(-0.5em)
  #text(size: 8pt, fill: ENCRE_2)[#libelle]
]

#let note_basse(corps) = {
  v(0.2em)
  block(
    width: 100%,
    stroke: (top: 0.5pt + GRILLE),
    inset: (top: 6pt),
  )[#text(size: 7.8pt, fill: ENCRE_2)[#corps]]
}

#let encadre(titre, corps, couleur: ORANGE) = block(
  width: 100%,
  fill: FOND,
  stroke: (left: 2.5pt + couleur),
  inset: (left: 10pt, rest: 8pt),
  radius: (right: 2pt),
)[
  #text(size: 9pt, weight: "bold", fill: couleur)[#titre]
  #v(-0.2em)
  #set text(size: 8.8pt)
  #corps
]

#let a_toi(consigne) = block(
  width: 100%,
  stroke: (paint: MUET, thickness: 0.5pt, dash: "dashed"),
  inset: 7pt,
  radius: 2pt,
)[
  #text(size: 7.8pt, fill: MUET, style: "italic")[À écrire — #consigne]
]

// Figure rognee EN HAUT ET EN BAS.
//   ratio     = hauteur / largeur de l'image d'origine, en pixels
//   haut, bas = bornes de la bande conservee, en fraction de la hauteur
//
// Imposer la hauteur de l'image est indispensable : sans elle, une image dont
// seule la largeur est fixee se laisse REDUIRE pour tenir dans une boite plus
// courte qu'elle — on obtient la figure entiere rapetissee, pas un rognage.
// `place` la sort du flux et `dy` la remonte pour couper le haut.
#let coupe(chemin, ratio, haut, bas) = context {
  let l = page.width - 2 * MARGE_X
  let h = l * ratio
  box(
    width: l,
    height: h * (bas - haut),
    clip: true,
    place(top + left, dy: -h * haut, image(chemin, width: l, height: h)),
  )
}

// =============================================================================
// PAGE 1
// =============================================================================

#ouverture(
  "Éducation prioritaire — 1 / 4",
  "Le seuil n'est pas choisi.\nIl découle du budget.",
  [Le classement REP et REP+ coïncide-t-il avec la réalité sociale des collèges ?],
)

#v(0.5em)

#grid(
  columns: (1fr, 1fr, 1fr),
  gutter: 10pt,
  chiffre("5 325", "collèges publics, rentrée 2024-2025"),
  chiffre("1 094", "places en éducation prioritaire"),
  chiffre("90,6 %", "de classements conformes"),
)

#v(0.9em)

#affiche[
  Classer les 1 094 collèges d'IPS le plus faible, c'est tout classer sous
  *88,80 points*. Ce seuil n'est pas une convention : il découle de l'enveloppe
  elle-même.
]

#v(0.3em)

#coupe("../outputs/figures/distribution_ips.png", 0.70909, 0.120, 0.827)

#text(size: 8pt, fill: ENCRE_2)[
  Les 5 325 collèges publics empilés selon leur statut. Le trait vertical marque le seuil
  national ; le peigne du bas donne les 30 seuils académiques, dont l'étendue atteint
  19,6 points.
]

// `1fr` absorbe le blanc restant et le REPARTIT. Sans lui, tout le vide
// s'accumule en bas de page, ce qui se lit comme une page mal remplie plutot
// que comme une respiration. Si le commentaire de Remy allonge la page, ces
// ressorts se compriment d'eux-memes jusqu'a zero.
#v(1fr)

#note_basse[
  *L'IPS n'est pas le critère officiel de classement.* Celui-ci repose sur un indice
  composite dont ni la spécification, ni les coefficients, ni le seuil ne sont publics. Un
  écart mesure donc un désaccord entre deux instruments, jamais une erreur administrative.
]

#v(1fr)
#a_toi[l'accroche, 2 à 3 lignes.]

// =============================================================================
// PAGE 2
// =============================================================================

#pagebreak()

#ouverture(
  "La géographie — 2 / 4",
  "Paris : 24 sur-inclusions,\net aucune autre carte possible.",
  [Tous les collèges dont l'écart dépasse 3 points d'IPS. À gauche la fréquence de ces
   écarts, à droite leur sens.],
)

#v(0.3em)

// On coupe a 0,100 et non plus haut : au-dessus de 0,120 se trouvent les
// titres des DEUX PANNEAUX (« Fréquence des écarts » / « Nature de ces
// écarts »), qui disent lequel est lequel. Seul le titre general, redondant
// avec celui de la page, est retire.
#coupe("../outputs/figures/ecarts_significatifs.png", 0.67692, 0.100, 0.864)

#v(0.5em)

#affiche[
  Paris ne compte que 6 collèges sous le seuil national pour 30 places à pourvoir. Le
  minimum arithmétiquement possible y est donc de 24 — exactement le nombre observé.
]

#v(0.1em)

#text(size: 9pt)[
  Aucune carte parisienne à 30 collèges ne ferait mieux au regard d'un étalon national.
  L'écart ne mesure pas une décision locale, mais la contrainte que le niveau national lui
  impose. Recalculé à l'intérieur de Paris, à enveloppe inchangée, il tombe de 24 à *8*.
]

#v(1fr)

#encadre(
  "Même fréquence, diagnostic opposé",
  [La Guadeloupe est le département où les écarts sont les plus fréquents — *19,6 %* de
   ses collèges — pour une moyenne signée de *+0,8* : les deux types s'y compensent. Paris
   suit de près en fréquence, *16,7 %*, avec une moyenne de *−13,7* : des sur-inclusions,
   et rien d'autre.

   Chaque collège compté pesant au moins 3 points, une moyenne proche de zéro ne veut pas
   dire « peu d'écart » mais « autant dans un sens que dans l'autre ».],
)

#v(1fr)
#a_toi[ta lecture du contraste entre les deux géographies.]

// =============================================================================
// PAGE 3
// =============================================================================

#pagebreak()

#ouverture(
  "Le second volet — 3 / 4",
  "« Oubli » ne veut pas dire\nce qu'on croit.",
  [L'enveloppe réduite aux 362 places REP+, même mécanique, seuil plus sélectif :
   77,80 points d'IPS au lieu de 88,80.],
)

#v(0.3em)

#affiche[
  Sur les 101 collèges que l'IPS désigne sans que REP+ les retienne, *90 sont déjà classés
  REP*. Onze seulement sont hors éducation prioritaire.
]

#v(0.2em)

#text(size: 9.4pt)[
  Un « oubli » ne signifie donc presque jamais que l'État n'a rien fait : il signifie
  qu'il a mis *REP là où l'IPS dirait REP+*. On passe d'une question de *couverture* — qui
  est aidé — à une question de *graduation* — qui est aidé au bon niveau.
]

#v(0.4em)

#coupe("../outputs/figures/rep_plus_ecart.png", 0.56429, 0.150, 0.766)

#text(size: 8pt, fill: ENCRE_2)[
  Écart au seuil REP+ pour les deux étalons. La couleur distingue les oublis déjà classés
  REP des oublis hors éducation prioritaire — sans quoi le mot serait trompeur.
]

#v(1fr)

#encadre(
  "Un second étalon ne confirme pas le premier",
  [Les évaluations nationales de début de 6#super[e] mesurent les élèves eux-mêmes, en
   septembre : le niveau *à l'arrivée*, avant que l'établissement n'ait rien produit. Cet
   étalon est donc indépendant de l'IPS — et il ne le confirme pas. Académie par académie,
   *la moitié changent de côté*, et les deux ratios d'enveloppe ne corrèlent qu'à *+0,31*.],
  couleur: BLEU,
)

#v(1fr)
#a_toi[ce que tu conclus de ce désaccord.]

// =============================================================================
// PAGE 4
// =============================================================================

#pagebreak()

#ouverture(
  "Synthèse — 4 / 4",
  "Ce qui reste vrai\nune fois l'imprécision avouée.",
  [Les trois niveaux croisés d'un coup, à enveloppes inchangées.],
)

#v(0.3em)

#coupe("../outputs/figures/matrices_classement_marges.png", 0.63380, 0.145, 0.730)

#v(0.4em)

#grid(
  columns: (0.9fr, 1fr),
  gutter: 14pt,
  {
    set text(size: 8.6pt)
    table(
      columns: 3,
      align: (left, right, right),
      stroke: none,
      inset: (x: 5pt, y: 4pt),
      fill: (_, y) => if y == 0 { none } else if calc.odd(y) { FOND } else { none },
      table.hline(stroke: 0.7pt + ENCRE),
      text(weight: "bold", size: 8pt)[], text(weight: "bold", size: 8pt)[Sans marge],
      text(weight: "bold", size: 8pt)[Avec marges],
      table.hline(stroke: 0.5pt + GRILLE),
      [IPS — diagonale], [87,0 %], text(weight: "bold")[93,5 %],
      [IPS — kappa], [0,70], text(weight: "bold")[0,85],
      [6#super[e] — diagonale], [81,2 %], text(weight: "bold")[94,2 %],
      [6#super[e] — kappa], [0,55], text(weight: "bold")[0,83],
      table.hline(stroke: 0.7pt + ENCRE),
    )
  },
  [
    #text(size: 9.2pt)[
      *Cette amélioration n'est pas un résultat* : c'est le prix de l'aveu d'imprécision.
      On cesse de compter comme désaccords des cas sur lesquels on ne peut pas se
      prononcer.

      Ce qui *reste* hors diagonale compte : *348 collèges* sont franchement du mauvais
      côté d'un seuil.
    ]
  ],
)

#v(1fr)

#encadre(
  "Les dispositifs gradués sont ceux dont les données ne sortent pas",
  [Trois politiques corrigeraient précisément l'effet de seuil mesuré ici : les *contrats
   locaux d'accompagnement*, l'*allocation progressive des moyens*, les *groupes de
   besoins* de la rentrée 2024 — soit exactement le millésime analysé.

   *Aucune ne publie la liste des établissements concernés*, alors que le dispositif
   binaire, lui, est entièrement public. Cela limite d'avance toute analyse, y compris
   celle-ci.],
)

#v(0.5em)

#note_basse[
  Sources : IPS des collèges, annuaire de l'éducation et évaluations nationales de
  6#super[e] (DEPP, data.education.gouv.fr) ; contours Insee / cartiflette. Analyse
  descriptive, sans pondération par les effectifs d'élèves : les résultats décrivent une
  part de collèges, jamais une part d'élèves. Chaîne complète, versions figées et données
  reconstruites depuis l'API du ministère — *github.com/rdarquin/education-prioritaire-ips*
]

#v(1fr)
#a_toi[ta conclusion, 2 lignes.]
