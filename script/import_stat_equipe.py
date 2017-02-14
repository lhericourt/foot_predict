from bs4 import BeautifulSoup
import urllib.request as req
from objets.match import get_all_match_fromDB, get_match_with_no_stat_fromDB
import pandas as pd
from objets.equipe import get_all_equipes_fromDB
import psycopg2
from objets.stat_equipe import Stat_equipe
import re

conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
all_match = get_all_match_fromDB(conn)

# Récupération de l'ensemble des équipes de la base de données
liste_equipes = get_all_equipes_fromDB(conn)
liste_equipes = pd.DataFrame(liste_equipes, columns=["code", "libelle"])
liste_equipes["libelle"] = liste_equipes.apply(axis=1, func=lambda x: x["libelle"].replace(" ", ""))

url_equipe = "http://www.lequipe.fr"
url_result = "/base/football/opta/matchs"
url_match = "/Football/match"


def get_one_stat(soup_equipe, attr):
    """
    Permet de récupérer une valeur d'un attribut de la soupe
    Nécessaire car en fonction des matchs on a pas toujours
    les mêmes attributs sans la soupe
    :param soup_equipe: la soupe des stats d'une équipe lors d'un match
    :param attr: l'attribut que l'on souhaite récuper
    :return stat: valeur de l'attribut
    """
    stat = ""
    try:
        stat = soup_equipe[attr]
    except:
        pass
    return stat


def get_classement(soup_classement, equipe):
    """
    Permet d'obtenir le classe à partir des résultats d'une journée,
    qui sont affichés sur la pache d'un match
    :param soup_classement: la soupe du classement affichée sur la match d'un match
    :param equipe: le code d'une équipe
    :return: le classement de l'equipe après le match
    """
    for soup_equipe in soup_classement:
        libelle_equipe = soup_equipe.find("div", class_="equipe").find("a").text.lower().replace(" ","")
        try:
            code_equipe = liste_equipes[liste_equipes["libelle"].replace(" ","")==libelle_equipe]["code"].iloc[0]

            if(code_equipe == equipe):
                return soup_equipe.find("div", class_="rang").text[:-1]
        except:
            print("L'équipe {} n'est pas connues de la base".format(libelle_equipe))

def get_stat_equipe_for_a_day(match, soup_liste_equipe, soup_classement):
    """
    Génère deux objets de statistiques, un pour l'équipe qui reçoit et
    un pour l'equipe extérieure
    :param soup_liste_equipe: la soupe du fichier xml récapitulant les stat du match
    :return liste_stat_equipe: les deux statistiques
    """

    # Initialisation de données liées au match
    id_match = match[0]
    equipe_domicile = match[1]
    equipe_ext = match[2]
    score = match[4]
    but_domicile = int(re.findall(r"(\d+)", score)[0])
    but_ext = int(re.findall(r"(\d+)", score)[1])

    liste_stat_equipe = []

    for soup_equipe in soup_liste_equipe:
        possession = get_one_stat(soup_equipe, "poss")
        fautes = get_one_stat(soup_equipe, "fautes")
        cjaunes = get_one_stat(soup_equipe, "cjaunes")
        crouges = get_one_stat(soup_equipe, "crouges")
        tirs_contres = get_one_stat(soup_equipe, "tcontres")
        tirs_non_cadres = get_one_stat(soup_equipe, "tnoncadres")
        tirs_cadres = get_one_stat(soup_equipe, "tcadres")
        tirs = get_one_stat(soup_equipe, "tirs")
        hors_jeu = get_one_stat(soup_equipe, "hj")
        occasions = get_one_stat(soup_equipe, "occasions")
        duels_gagnes = get_one_stat(soup_equipe, "duels")
        passes = get_one_stat(soup_equipe, "passes")
        passes_reussies = get_one_stat(soup_equipe, "passes-r")
        corners = get_one_stat(soup_equipe, "corners")
        tactique = get_one_stat(soup_equipe, "tactique")
        stat_eq = Stat_equipe(
            id_match=id_match,
            code_equipe="",
            code_adversaire="",
            domicile="TRUE",
            victoire="",
            possession=possession,
            nbr_buts_mis="",
            nbr_buts_pris="",
            nbr_tirs=tirs,
            nbr_tirs_contres=tirs_contres,
            nbr_tirs_contres_def="",
            nbr_tirs_cadres=tirs_cadres,
            nbr_tirs_non_cadres = tirs_non_cadres,
            nbr_passes=passes,
            nbr_passes_reussies=passes_reussies,
            nbr_corners=corners,
            nbr_corners_def="",
            nbr_hors_jeu=hors_jeu,
            nbr_occasions=occasions,
            nbr_occasions_def="",
            nbr_duels_gagnes=duels_gagnes,
            nbr_duels_perdus="",
            nbr_fautes_commises=fautes,
            nbr_cjaunes=cjaunes,
            nbr_crouges=crouges,
            classement_avant_match="",
            classement_apres_match="",
            tactique=tactique
        )
        liste_stat_equipe.append(stat_eq)

    for i, stat_eq in enumerate(liste_stat_equipe):
        # Cas de l'équipe qui reçoit
        if i == 0:
            stat_eq.code_equipe = equipe_domicile
            stat_eq.code_adversaire = equipe_ext
            stat_eq.domicile = "TRUE"
            stat_eq.nbr_duels_perdus = liste_stat_equipe[1].nbr_duels_gagnes
            stat_eq.nbr_buts_mis = but_domicile
            stat_eq.nbr_buts_pris = but_ext
            stat_eq.nbr_tirs_contres_def = liste_stat_equipe[1].nbr_tirs_contres
            stat_eq.nbr_occasions_def = liste_stat_equipe[1].nbr_occasions
            stat_eq.nbr_corners_def = liste_stat_equipe[1].nbr_corners
            stat_eq.classement_apres_match = get_classement(soup_classement, equipe_domicile)
            if (but_domicile > but_ext):
                stat_eq.victoire = "V"
            elif but_domicile == but_ext:
                stat_eq.victoire = "N"
            else:
                stat_eq.victoire = "D"

        # Cas de l'équipe extérieure
        else:
            stat_eq.code_equipe = equipe_ext
            stat_eq.code_adversaire = equipe_domicile
            stat_eq.domicile = "FALSE"
            stat_eq.nbr_duels_perdus = liste_stat_equipe[0].nbr_duels_gagnes
            stat_eq.nbr_buts_mis = but_ext
            stat_eq.nbr_buts_pris = but_domicile
            stat_eq.nbr_tirs_contres_def = liste_stat_equipe[0].nbr_tirs_contres
            stat_eq.nbr_occasions_def = liste_stat_equipe[0].nbr_occasions
            stat_eq.nbr_corners_def = liste_stat_equipe[0].nbr_corners
            stat_eq.classement_apres_match = get_classement(soup_classement, equipe_ext)
            if (but_domicile < but_ext):
                stat_eq.victoire = "V"
            elif but_domicile == but_ext:
                stat_eq.victoire = "N"
            else:
                stat_eq.victoire = "D"

    return liste_stat_equipe


# Récupération de tous les matchs sans stat associées
liste_match = get_match_with_no_stat_fromDB(conn)

for match in liste_match:
    print(match)
    numero_match = re.findall(r"_(\d+).html", match[3])[0]
    # Récupération des stats du match
    try:
        xml_match = url_equipe + url_result + "/" + numero_match + ".xml"
        page_match = req.urlopen(xml_match).read().decode('utf-8', 'ignore')
        soup_match = BeautifulSoup(page_match, "lxml")
        soup_liste_equipe = soup_match.find_all("equipe")
    except:
        print("La page {} n'existe pas".format(xml_match))

    # Récupération du classement de la journée
    try:
        page_classement = req.urlopen(url_equipe + url_match + "/" + numero_match).read().decode('utf-8', 'ignore')
        soup_classement = BeautifulSoup(page_classement, "html.parser")
        soup_classement = soup_classement.find_all("div", class_=["ligneclub"])
    except:
        print("La page {} n'existe pas".format(url_match + "/" + numero_match))

    try:
        stat_equipe = get_stat_equipe_for_a_day(match, soup_liste_equipe, soup_classement)
        # Création des stats dans la base
        stat_equipe[0].create_stat(conn)
        stat_equipe[1].create_stat(conn)
    except:
        print("Erreur lors de l'insertion en base")



conn.close()
