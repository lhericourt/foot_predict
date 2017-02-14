from bs4 import BeautifulSoup
import urllib.request as req
from objets.equipe import get_equipe_by_libelle_fromDB
from objets.joueur import Joueur, get_joueur_by_nom_fromDB
import psycopg2
import re


if __name__ == "__main__":

    conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")

    # Récupération de la liste des urls des équipes de L1
    url = "http://www.lequipe.fr/Football/EQ_D1.html"
    page_equipes = req.urlopen(url).read().decode('utf-8', 'ignore')
    soup_equipes = BeautifulSoup(page_equipes, "html.parser")

    div_equipe = soup_equipes.find_all("div", class_="club-left")
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

            if (joueur.find("td", class_="nom")):

                id_site_equipe = re.findall(r"/(\d+)/", joueur.find("img")["src"])[0]

                nom = joueur.find("td", class_="nom").find("a")["title"].lower().strip()
                proprietes = joueur.find_all("td", class_="fc_data")
                poste = proprietes[0].text[1:4]

                date_naissance = proprietes[1]["data-annee"] + "-" + proprietes[1]["data-mois"] + "-" + proprietes[1][
                    "data-jour"]
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

                joueur_obj = Joueur(nom, poste, date_naissance, taille, poids, id_site_equipe)

                if (get_joueur_by_nom_fromDB(nom, date_naissance, conn)):
                    print("Le joueur {} existe déjà".format(nom))
                else:
                    print("Insertion de {} avec l'id {}".format(nom, id_site_equipe))
                    joueur_obj.create_joueur(conn)

    conn.close()


def add_joueur(id_joueur_site_equipe, conn):
    url_joueur = "http://www.lequipe.fr/Football/FootballFicheJoueur" + id_joueur_site_equipe + ".html"
    page_joueur = req.urlopen(url_joueur).read().decode('utf-8', 'ignore')
    soup_joueur = BeautifulSoup(page_joueur, "html.parser")
    div_joueur = soup_joueur.find("div", class_="zP_infPlay")

    # Nom du joueur
    nom = soup_joueur.find("h1").text.lower().strip()

    # Date de naissance du joueur
    date_naissance = "1900-01-01"
    try:
        date_naissance = div_joueur.find("td", class_="calcage")["ddn"]
        date_naissance_decomposee = re.findall(r"(\d+)", date_naissance)
        jour = date_naissance_decomposee[1]
        mois = date_naissance_decomposee[0]
        annee = date_naissance_decomposee[2]
        date_naissance = annee + "-" + mois + "-" + jour
    except:
        print("Le joueur {} n'a pas de date de naissance".format(nom))

    # Taille du joueur
    taille = 0
    try:
        taille = div_joueur.find_all("tr")[5].find_all("td")[1].text.replace("m", "")
    except:
        print("Le joueur {} n'a pas de date de naissance".format(nom))

    # Poids du joueur
    poids = 0
    try:
        poids = re.findall(r"(\d+)", div_joueur.find_all("tr")[6].find_all("td")[1].text)[0]
    except:
        print("Le joueur {} n'a pas de poids".format(nom))

    # Poste du joueur
    poste = "NC"
    try:
        libelle_poste = div_joueur.find_all("tr")[7].find_all("td")[1].text.lower().strip()
        if libelle_poste == "défenseur":
            poste = "DEF"
        elif libelle_poste == "attaquant":
            poste = "ATT"
        elif libelle_poste == "milieur":
            poste = "MIL"
        elif libelle_poste == "gardien":
            poste = "GAR"
    except:
        print("Le joueur {} n'a pas de poste de défini".format(nom))

    joueur_obj = Joueur(nom, poste, date_naissance, taille, poids, id_joueur_site_equipe)

    if (get_joueur_by_nom_fromDB(nom, date_naissance, conn)):
        print("Le joueur {} existe déjà".format(nom))
    else:
        print("Insertion de {} avec l'id {}".format(nom, id_joueur_site_equipe))
        joueur_obj.create_joueur(conn)
