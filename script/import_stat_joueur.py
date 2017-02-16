from objets.match import get_all_match_fromDB, get_match_with_no_stat_joueur_fromDB, get_match_fromDB
from objets.equipe import get_all_equipes_fromDB
from objets.stat_joueur import Stat_joueur
from objets.joueur import get_id_joueur_by_id_site_equipe_fromDB
from script.import_joueur import add_joueur
import re
import psycopg2
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request as req

conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
conn.set_session(autocommit=True)
all_match = get_all_match_fromDB(conn)

# Récupération de l'ensemble des équipes de la base de données
liste_equipes = get_all_equipes_fromDB(conn)
liste_equipes = pd.DataFrame(liste_equipes, columns=["code", "libelle"])
liste_equipes["libelle"] = liste_equipes.apply(axis=1, func=lambda x: x["libelle"].replace(" ", ""))

url_equipe = "http://www.lequipe.fr"
url_result = "/base/football/opta/matchs"
url_match = "/Football/match"


def get_one_stat(soup_stat_joueur, attr):
    value = ""
    soup_liste_stat = soup_stat_joueur.find_all("stat")
    for stat in soup_liste_stat:
        if attr == stat["type"]:
            value = stat["txt"]
    return value


def get_stat_one_joueur(id_joueur, id_match, code_equipe, soup_stat_joueur):
    arrets = get_one_stat(soup_stat_joueur, "Arrêts")
    arrets_decisifs = get_one_stat(soup_stat_joueur, "Arrêts décisifs")
    ballons_touches = get_one_stat(soup_stat_joueur, "Ballons touchés")
    ballons_perdus = get_one_stat(soup_stat_joueur, "Ballons perdus")
    buts_int_surface = get_one_stat(soup_stat_joueur, "Buts intérieur surface")
    buts_hors_surface = get_one_stat(soup_stat_joueur, "Buts hors surface")
    centres = get_one_stat(soup_stat_joueur, "Centres")
    centres_reussis = get_one_stat(soup_stat_joueur, "Centres réussis")
    duels_aeriens_perdus = get_one_stat(soup_stat_joueur, "Duels aériens perdus")
    duels_aeriens_gagnes = get_one_stat(soup_stat_joueur, "Duels aériens gagnés")
    duels_gagnes = get_one_stat(soup_stat_joueur, "Duels gagnés")
    duels_perdus = get_one_stat(soup_stat_joueur, "Duels perdus")
    fautes = get_one_stat(soup_stat_joueur, "Fautes")
    fautes_subies = get_one_stat(soup_stat_joueur, "Fautes subies")
    passes = get_one_stat(soup_stat_joueur, "Passes")
    passes_decisives = get_one_stat(soup_stat_joueur, "Passes décisives")
    passes_reussies = get_one_stat(soup_stat_joueur, "Passes réussies")
    tirs_cadres_hors_surface = get_one_stat(soup_stat_joueur, "Tirs cadrés hors surface")
    tirs_cadres_int_surface = get_one_stat(soup_stat_joueur, "Tirs cadrés intérieur surface")
    tirs_non_cadres_hors_surface = get_one_stat(soup_stat_joueur, "Tirs non cadrés hors surface")
    tirs_non_cadres_int_surface = get_one_stat(soup_stat_joueur, "Tirs non cadrés intérieur surface")
    tacles = get_one_stat(soup_stat_joueur, "Tacles")
    tacles_reussis = get_one_stat(soup_stat_joueur, "Tacles réussis")

    stat_joueur = Stat_joueur(
        id_joueur=id_joueur,
        id_match=id_match,
        code_equipe=code_equipe,
        arrets=arrets,
        arrets_decisifs=arrets_decisifs,
        ballons_touches=ballons_touches,
        ballons_perdus=ballons_perdus,
        buts_int_surface=buts_int_surface,
        buts_hors_surface=buts_hors_surface,
        centres=centres,
        centres_reussis=centres_reussis,
        duels_aeriens_perdus=duels_aeriens_perdus,
        duels_aeriens_gagnes=duels_aeriens_gagnes,
        duels_gagnes=duels_gagnes,
        duels_perdus=duels_perdus,
        fautes=fautes,
        fautes_subies=fautes_subies,
        passes=passes,
        passes_decisives=passes_decisives,
        passes_reussies=passes_reussies,
        tirs_cadres_hors_surface=tirs_cadres_hors_surface,
        tirs_cadres_int_surface=tirs_cadres_int_surface,
        tirs_non_cadres_hors_surface=tirs_non_cadres_hors_surface,
        tirs_non_cadres_int_surface=tirs_non_cadres_int_surface,
        tacles=tacles,
        tacles_reussis=tacles_reussis,
    )

    return stat_joueur


def get_stat_joueurs_for_a_day(match, soup_liste_equipe):
    """
    Génère un objets de statistiques, pour chacun des joueurs
    ayant participé au match
    :param match: les informations du match
    :param soup_liste_equipe: la soupe du fichier xml récapitulant les stat du match
    :return liste_stat_equipe: les deux statistiques
    """

    # Initialisation de données liées au match
    id_match = match[0]
    equipe_domicile = match[1]
    equipe_ext = match[2]
    liste_stat_joueurs = []

    for i, soup_equipe in enumerate(soup_liste_equipe):
        if i == 0:
            code_equipe = equipe_domicile
        else:
            code_equipe = equipe_ext

        for stat_joueur in soup_equipe.find_all("joueur"):

            id_joueur_site_equipe = stat_joueur["id"]
            id_joueur = get_id_joueur_by_id_site_equipe_fromDB(id_joueur_site_equipe, conn)
            if(id_joueur_site_equipe == ""):
                print("Cette statistique n'a pas d'id technique pour le joueur : {}".format(stat_joueur))
                continue

            try:
                if id_joueur is None:
                    add_joueur(id_joueur_site_equipe, conn)
                    id_joueur = get_id_joueur_by_id_site_equipe_fromDB(id_joueur_site_equipe, conn)

                liste_stat_joueurs.append(get_stat_one_joueur(id_joueur, id_match, code_equipe, stat_joueur))

            except:
                print(
                    "Le joueur {} pour le match {} n'a pas pu être ajouté dans la base".format(stat_joueur["nom"],
                                                                                                    id_match))

    return liste_stat_joueurs

# Récupération de tous les matchs sans stat associées
liste_match = get_match_with_no_stat_joueur_fromDB(conn)

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

    liste_stat_joueur = get_stat_joueurs_for_a_day(match, soup_liste_equipe)
    # Création des stats dans la base
    for stat_joueur in liste_stat_joueur:
        try:
            stat_joueur.create_stat(conn)
        except:
            print("Erreur lors de l'insertion en base pour la stat d'id_match {} et pour le joueur {}".format(
                stat_joueur.id_match, stat_joueur.id_joueur))

"""


numero_match = "292564"
match = ['4189', 'ev', 'so', '/Football/FootballFicheMatch45019_292564.html']

try:
    xml_match = url_equipe + url_result + "/" + numero_match + ".xml"
    page_match = req.urlopen(xml_match).read().decode('utf-8', 'ignore')
    soup_match = BeautifulSoup(page_match, "lxml")
    soup_liste_equipe = soup_match.find_all("equipe")
except:
    print("La page {} n'existe pas".format(xml_match))

liste_stat_joueur = get_stat_joueurs_for_a_day(match, soup_liste_equipe)

# Création des stats dans la base
for stat_joueur in liste_stat_joueur:
    stat_joueur.create_stat(conn)
"""

conn.close()
