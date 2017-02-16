import psycopg2


class Joueur:
    """Classe définissant une équipe caractérisée par :
    - son nom ;
    - son poste ;
    - sa date de naissance ;
    - sa taille ;
    - son poids """

    def __init__(self, nom, poste, date_naissance, taille, poids, id_site_equipe):
        self.nom = nom
        self.poste = poste
        self.date_naissance = date_naissance
        self.taille = taille
        self.poids = poids
        self.id_site_equipe = id_site_equipe

    def create_joueur(self, conn):
        """Méthode appelée quand on souhaite ajouter une équipe dans la base"""
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO joueur (nom_complet, poste, date_naissance, taille, poids, id_joueur_site_equipe) VALUES (%s, %s, %s, %s, %s, %s)",
                (self.nom, self.poste, self.date_naissance, self.taille, self.poids, self.id_site_equipe))

            conn.commit()
            cur.close()
        except psycopg2.Error as e:
            print(e.pgerror)

def get_joueur_by_nom_fromDB(nom, date_naissance, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT nom_complet, poste, date_naissance, taille, poids, id_joueur_site_equipe "
        "FROM joueur WHERE nom_complet = (%s) and date_naissance = (%s)",
        (nom, date_naissance))

    try:
        joueur = cur.fetchone()
        cur.close()
        return Joueur(joueur[0], joueur[1], joueur[2], joueur[3], joueur[4], joueur[5])

    except:
        print("Le joueur {} ( {} ) n'existe pas en base".format(nom, date_naissance))


def get_joueur_by_id_site_equipe_fromDB(id_site_equipe, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT nom_complet, poste, date_naissance, taille, poids, id_joueur_site_equipe "
        "FROM joueur WHERE id_joueur_site_equipe = (%s)",
        [id_site_equipe])

    try:
        joueur = cur.fetchone()
        cur.close()
        return Joueur(joueur[0], joueur[1], joueur[2], joueur[3], joueur[4], joueur[5])

    except:
        print("Le joueur d'id du site de l'equip {} n'existe pas en base".format(id_site_equipe))


def get_id_joueur_by_id_site_equipe_fromDB(id_site_equipe, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute(
        "SELECT id_joueur "
        "FROM joueur WHERE id_joueur_site_equipe = (%s)",
        [id_site_equipe])

    try:
        id_joueur = cur.fetchone()[0]
        cur.close()
        return id_joueur

    except:
        print("Le joueur d'id du site de l'equip {} n'existe pas en base".format(id_site_equipe))