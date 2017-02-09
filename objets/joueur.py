import psycopg2


class Joueur:
    """Classe définissant une équipe caractérisée par :
    - son nom ;
    - son poste ;
    - sa date de naissance ;
    - sa taille ;
    - son poids """

    def __init__(self, nom, poste, date_naissance, taille, poids):
        self.nom = nom
        self.poste = poste
        self.date_naissance = date_naissance
        self.taille = taille
        self.poids = poids

    def create_joueur(self, conn):
        """Méthode appelée quand on souhaite ajouter une équipe dans la base"""
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO joueur (nom_complet, poste, date_naissance, taille, poids) VALUES (%s, %s, %s, %s, %s)",
            (self.nom, self.poste, self.date_naissance, self.taille, self.poids))
        conn.commit()
        cur.close()


def get_joueur_fromDB(nom, date_naissance, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT nom_complet, poste, date_naissance, taille, poids FROM joueur WHERE nom_complet = (%s) and date_naissance = (%s)",
        (nom, date_naissance))

    try:
        joueur = cur.fetchone()
        cur.close()
        return Joueur(joueur[0], joueur[1], joueur[2], joueur[3], joueur[4])

    except:
        print("Le joueur n'existe pas en base")
