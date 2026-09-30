"""Les deux etalons du projet, et les conventions de nommage qui vont avec.

POURQUOI UN REGISTRE

Toute l'analyse repose sur une meme mecanique : classer les colleges sur une
variable, retenir les n plus bas — n etant l'enveloppe d'education prioritaire
reellement allouee — et confronter cet ensemble a la carte reelle. Cette
mecanique ne depend pas de la variable choisie. Le registre permet donc de la
faire tourner sur deux etalons sans dupliquer une ligne de calcul.

LES DEUX ETALONS

    IPS      indice de position sociale, publie par la DEPP. Mesure la
             composition sociale du college, en amont de la politique : le
             classement en REP ne le deplace pas.

    EVAL6    score moyen aux evaluations nationales de debut de sixieme,
             moyenne du francais et des mathematiques, sur une echelle
             standardisee centree sur 250.

CE QUI LES DISTINGUE

L'IPS decrit un milieu, l'evaluation mesure un niveau. Les deux sont en amont
de l'action du college — l'evaluation a lieu en SEPTEMBRE, a l'entree en
sixieme, avant que le college n'ait rien enseigne. Aucun des deux n'est donc
contamine par les moyens recus au titre de l'education prioritaire, et c'est
ce qui les rend comparables.

Ni l'un ni l'autre n'est le critere officiel de classement. Un ecart mesure un
desaccord entre deux instruments, jamais une erreur administrative.

CONVENTION DE NOMMAGE

L'IPS porte le suffixe vide : ses fichiers gardent les noms qu'ils avaient
avant l'introduction du second etalon, et les figures publiees conservent leurs
liens. L'evaluation porte le suffixe `_eval6`.

Les COLONNES produites par `score_ecart.py` sont en revanche identiques d'un
etalon a l'autre — `valeur`, `seuil`, `score_ecart`, `type_ecart`. Seul le
fichier change. C'est ce qui permet aux modules de figures de traiter les deux
etalons avec le meme code.
"""

ETALONS = {
    "ips": {
        "colonne": "ips",
        "suffixe": "",
        "libelle": "IPS",
        "libelle_long": "indice de position sociale",
        "avec_article": "l'IPS",
        "de_article": "de l'IPS",
        "unite": "points d'IPS",
        "unite_courte": "points",
        "axe": "Indice de position sociale (IPS)",
        "source": "DEPP (IPS)",
        # Pourquoi la barre des 3 points : pour l'IPS c'est une recommandation
        # du producteur de la donnee, pour le score de sixieme une simple
        # convention de comparabilite. La nuance doit apparaitre sur la figure.
        "justification_seuil":
            "En deçà, la DEPP recommande de ne pas interpréter une différence "
            "d'IPS.",
        # Pas de l'histogramme et arrondi d'affichage : l'IPS s'etale sur une
        # centaine de points, le score de sixieme sur plusieurs centaines.
        "pas_histogramme": 2.0,
        "decimales": 2,
    },
    "eval6": {
        "colonne": "eval6",
        "suffixe": "_eval6",
        "libelle": "score de 6ᵉ",
        "libelle_long": "score aux évaluations nationales de début de sixième",
        "avec_article": "le score de 6ᵉ",
        "de_article": "du score de 6ᵉ",
        "unite": "points de score",
        "unite_courte": "points",
        "axe": "Score aux évaluations nationales de début de 6ᵉ",
        "source": "DEPP (évaluations nationales de sixième)",
        "justification_seuil":
            "Aucune recommandation du producteur n'existe ici : la borne est "
            "reprise de l'IPS, dont la dispersion entre établissements est "
            "comparable (14,7 contre 16,9 points).",
        "pas_histogramme": 5.0,
        "decimales": 1,
    },
}


def fichier_scores(cle: str) -> str:
    """Nom du fichier de scores par college, pour un etalon."""
    return f"score_ecart_{cle}.csv"


def fichier_academies(cle: str) -> str:
    """Nom du fichier de synthese academique, pour un etalon."""
    return f"score_ecart_par_academie{ETALONS[cle]['suffixe']}.csv"


def nom_figure(radical: str, cle: str) -> str:
    """Nom de fichier d'une figure, pour un etalon.

    Le radical est le nom historique de la figure IPS : la variante IPS garde
    donc exactement son nom, et seule la variante `eval6` en ajoute un.
    """
    return f"{radical}{ETALONS[cle]['suffixe']}.png"
