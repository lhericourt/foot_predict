from bs4 import BeautifulSoup
import urllib.request as req
from objets.joueur import Joueur, get_joueur_fromDB
import psycopg2

conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")

# Récupération de la liste des urls des équipes de L1
url = "http://www.lequipe.fr/Football/EQ_D1.html"
page_equipes = req.urlopen(url).read().decode('utf-8', 'ignore')
soup_equipes = BeautifulSoup(page_equipes, "html.parser")

div_equipe = soup_equipes.find_all("div", class_ ="club-left")
liste_url_equipe = []

for eq in div_equipe:
    nom = eq.find("a")["title"]
    lien = eq.find("a")["href"]
    liste_url_equipe.append((nom, lien))


# Récupération de la liste des joueurs, et insertion en base

for eq in liste_url_equipe:
    url_equipe = "http://www.lequipe.fr" + eq[1]
    page_joueurs = req.urlopen(url_equipe).read().decode('utf-8', 'ignore')
    soup_joueurs = BeautifulSoup(page_joueurs, "html.parser")
    div_equipe = soup_joueurs.find(id="club_effectif_club").find_all("tr")

    for joueur in div_equipe:

        if(joueur.find("td", class_="nom")):

            nom = joueur.find("td", class_="nom").find("a")["title"]
            proprietes = joueur.find_all("td", class_="fc_data")
            poste = proprietes[0].text[1:4]

            date_naissance = proprietes[1]["data-annee"] + "-" + proprietes[1]["data-mois"] + "-" + proprietes[1]["data-jour"]
            # Prise en compte du cas où la date n'est pas renseignée
            if date_naissance == "--":
                date_naissance = "1900-01-01"

            taille = proprietes[2].text[:-1].replace(".", "")
            # Prise en compte du cas où la taille n'est pas renseignée
            if (taille == ""):
                taille = 0

            poids = proprietes[3].text
            # Prise en compte du cas où le poids n'est pas renseignée
            if (poids == "-"):
                poids = 0

            joueur_obj = Joueur(nom, poste, date_naissance, taille, poids)
            print(nom)
            if (get_joueur_fromDB(nom, date_naissance, conn)):
                print("Le joueur {} existe déjà".format(nom))
            else:
                joueur_obj.create_joueur(conn)

            #test_joueur = Joueur("nom", "post", "1987-09-1", "33", "123")
#test_joueur.create_joueur(conn)

#if(get_joueur_fromDB("nom", "1987-09-1", conn)):
    #print("joueur trouvé")

conn.close()