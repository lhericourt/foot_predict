from bs4 import BeautifulSoup
import urllib.request as req
import psycopg2
import re
from script.import_match import get_all_match_for_a_day, get_all_url_day_for_a_season

# Connection à la base de données
conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
liste_actions = set()

saisons = {
    "2016": "/Football/ligue-1-resultats.html",
    #"2015": "/Football/FootballResultat52242.html",
    #"2014": "/Football/FootballResultat48028.html",
    #"2013": "/Football/FootballResultat45056.html",
}

url_equipe = "http://www.lequipe.fr"
url_result = "/base/football/opta/matchs"
url_match = "/Football/match"

liste_url_match = get_all_url_day_for_a_season("http://www.lequipe.fr/Football/ligue-1-resultats.html")
# Pour chaque des journée on récupère les matche
# et on les ajoute en base
for url in liste_url_match:
    liste_match = get_all_match_for_a_day(url, "2016")
    for match in liste_match:
        if "-" not in match.score:
            print("Le match n'est pas encore joué")
        else:
            numero_match = re.findall(r"_(\d+).html", match.url)[0]
            xml_match = url_equipe + url_result + "/" + numero_match + ".xml"
            page_match = req.urlopen(xml_match).read().decode('utf-8', 'ignore')
            soup_match = BeautifulSoup(page_match, "lxml")
            soup_liste_joueur = soup_match.find_all("joueur")

            for index, joueur in enumerate(soup_liste_joueur):
                liste_stat = soup_liste_joueur[index].find_all("stat")
                for stat in liste_stat:
                    liste_actions.add(stat["type"])

print(liste_actions)


conn.close()