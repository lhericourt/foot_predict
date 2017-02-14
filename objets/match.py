import psycopg2
import pandas as pd

class Match:
    """Classe définissant une équipe caractérisée par :
    - son nom ;
    - son poste ;
    - sa date de naissance ;
    - sa taille ;
    - son poids """

    def __init__(self, equipe_dom, equipe_ext, saison, journee, score, url):
        self.equipe_dom = equipe_dom
        self.equipe_ext = equipe_ext
        self.saison = saison
        self.journee = journee
        self.score = score
        self.url = url

    def create_match(self, conn):
        """Méthode appelée quand on souhaite ajouter un match dans la base"""
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO match (saison, journee, code_equipe_dom, code_equipe_ext, score, url_equipe)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (self.saison, self.journee, self.equipe_dom, self.equipe_ext, self.score, self.url))
        conn.commit()
        cur.close()


def get_match_fromDB(saison, journee, equipe_dom, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT saison, journee, code_equipe_dom, code_equipe_ext, score, url_equipe "
        "FROM match WHERE saison = (%s) and journee = (%s) and code_equipe_dom = (%s)",
        [saison, journee, equipe_dom])

    try:
        match = cur.fetchone()
        cur.close()
        return Match(match[0], match[1], match[2], match[3], match[4], match[5])

    except:
        print("Le Match n'existe pas en base")


def get_match_with_no_stat_fromDB(conn):
    cur = conn.cursor()
    cur.execute("SELECT match.id_match, code_equipe_dom, code_equipe_ext, url_equipe, score, saison, journee "
                "FROM match LEFT OUTER JOIN stat_equipe_par_match "
                "ON match.id_match = stat_equipe_par_match.id_match WHERE victoire IS NULL")
    liste_match = cur.fetchall()
    cur.close
    return liste_match


def get_all_match_fromDB(conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT id_match, saison, journee, code_equipe_dom, code_equipe_ext, score, url_equipe FROM match LIMIT 10")

    all_match = cur.fetchall()
    cur.close()
    all_match = pd.DataFrame(all_match, columns=["id_match", "saison", "journee", "code_equipe_dom", "code_equipe_ext", "score", "url_equipe"])
    return all_match
