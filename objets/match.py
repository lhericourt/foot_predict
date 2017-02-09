import psycopg2


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
    print(" les params sont : {}, {}, {}".format(saison, journee, equipe_dom))
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
