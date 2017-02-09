from bs4 import BeautifulSoup
import urllib.request as req
from objets.match import Match, get_match_fromDB
import pandas as pd
from objets.equipe import get_all_equipes_fromDB
import psycopg2
import re

url_equipe = "http://www.lequipe.fr"

# On récupère les match du site lequipe.fr
saisons = {
    "2016": "/Football/ligue-1-resultats.html",
    "2015": "/Football/FootballResultat52242.html",
    "2014": "/Football/FootballResultat48028.html",
    "2013": "/Football/FootballResultat45056.html",
}



def get_all_match_for_a_day(url, saison):
    """
    En entrée il s'agit d'une url de l'équipe sous format beautiful soup
    Exemple : <option value="/Football/FootballResultat52207.html" type="1">2e journée</option>
    :param url:
    :param saison:
    :return liste_match: il s'agit de la liste des match sous formes d'objets
    """

    liste_match = []
    url_match = url_equipe + url["value"]
    journee = re.findall(r"(\d+)", url.text)[0]
    page_match = req.urlopen(url_match).read().decode('utf-8', 'ignore')
    soup_match = BeautifulSoup(page_match, "html.parser")
    soup_match = soup_match.find_all("div", class_=["bb-color"])

    for match in soup_match:
        eq_dom = match.find("div", class_="equipeDom").find("img")["alt"].lower().replace(" ", "")
        eq_ext = match.find("div", class_="equipeExt").find("img")["alt"].lower().replace(" ", "")
        score = match.find("div", class_="score").find("a").text
        url_match = ""
        try:
            url_match =  match.find("div", class_="score").find("a")["href"]
        except:
            pass
        #url_confrontation = match.find("div", class_="archives_conf").find("a")["href"]
        #url_match = get_url_match(url_confrontation, saison, journee)

        # On teste que les deux équipes sont connues du référentiel
        if (len(liste_equipes[liste_equipes["libelle"] == eq_dom]) > 0 and len(
                liste_equipes[liste_equipes["libelle"] == eq_ext]) > 0):
            eq_dom = liste_equipes[liste_equipes["libelle"] == eq_dom]["code"].iloc[0]
            eq_ext = liste_equipes[liste_equipes["libelle"] == eq_ext]["code"].iloc[0]
            match_obj = Match(eq_dom, eq_ext, saison, journee, score, url_match)
            liste_match.append(match_obj)
        else:
            print("L'équipe {} ou l'équipe {} n'existe pas en base".format(eq_dom, eq_ext))
    return liste_match


def get_all_url_day_for_a_season(url_saison):
    """
    On retrouve les url de chaque journée
    :param url_saison: url d'une saison sur le site de l'équipe
    :return liste_url_match: les url de match sous forme de soupe
    """
    page_match = req.urlopen(url_saison).read().decode('utf-8', 'ignore')
    soup_match = BeautifulSoup(page_match, "html.parser")
    liste_url_match = soup_match.find("select", class_="filtregroupes").find_all("option")
    return liste_url_match


# On récupère la table de référence des équipes de la base
conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
liste_equipes = get_all_equipes_fromDB(conn)
liste_equipes = pd.DataFrame(liste_equipes, columns=["code", "libelle"])
liste_equipes["libelle"] = liste_equipes.apply(axis=1, func=lambda x: x["libelle"].replace(" ", ""))

for annee in saisons:
    liste_url_match = get_all_url_day_for_a_season(url_equipe + saisons[annee])
    # Pour chaque des journée on récupère les matche
    # et on les ajoute en base
    for url in liste_url_match:
        liste_match = get_all_match_for_a_day(url, annee)
        for match in liste_match:
            if "-" not in match.score:
                print("Le match n'est pas encore joué")
            elif get_match_fromDB(match.saison, match.journee, match.equipe_dom, conn):
                print("Le match {} {} {} existe déjà".format(match.saison, match.journee, match.equipe_dom))
            else:
                match.create_match(conn)

conn.close()



"""
Fonction inutile en fin de compte
def get_url_match(url_confrontation, saison, journee):
    \"""
    Retourne la page de match
    :param url_confrontation: url avec la liste de toutes les confrontations
    :param saison:
    :param journee:
    :return:
    \"""
    try:
        page_confrontation = req.urlopen(url_equipe + url_confrontation).read().decode('utf-8', 'ignore')
        soup_confrontation = BeautifulSoup(page_confrontation, "html.parser")
        soup_confrontation = soup_confrontation.find_all("div", class_=["alternante"])
    except:
        print("Page de la confrontation {} non trouvée".format(url_confrontation))
        return ""

    for confrontation in soup_confrontation:
        saison_conf = confrontation.find("div", class_="col-200").text[:4]
        journee_conf = re.findall(r"(\d+)", confrontation.find("div", class_="col-250").text)[0]
        url_match = ""
        try:
            url_match = confrontation.find("div", class_="col-172").find("a")["href"]
        except:
            pass

        if (saison == saison_conf and journee == journee_conf):
            return url_match

"""
