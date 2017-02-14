import psycopg2

class Equipe:
    """Classe définissant une équipe caractérisée par :
    - son code ;
    - son libelle ;"""

    def __init__(self, code, libelle):
        """Constructeur de notre classe"""
        self.code = code
        self.libelle = libelle

    def create_equipe(self, conn):
        """Méthode appelée quand on souhaite ajouter une équipe dans la base"""
        cur = conn.cursor()
        cur.execute("INSERT INTO equipe (code, libelle) VALUES (%s, %s)", (self.code, self.libelle))
        conn.commit()
        cur.close()


def get_equipe_by_code_fromDB(code, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute("SELECT code, libelle FROM equipe WHERE code = (%s)", [code])

    try:
        equipe = cur.fetchone()
        cur.close()
        return Equipe(equipe[0], equipe[1])

    except:
        print("L'équipe n'existe pas")


def get_equipe_by_libelle_fromDB(libelle, conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute("SELECT code, libelle FROM equipe WHERE libelle = (%s)", [libelle])

    try:
        equipe = cur.fetchone()
        cur.close()
        return Equipe(equipe[0], equipe[1])

    except:
        print("L'équipe n'existe pas")


def get_all_equipes_fromDB(conn):
    """Méthode pour récupérer une équipe de la base"""
    cur = conn.cursor()
    cur.execute("SELECT code, libelle FROM equipe")

    try:
        equipes = cur.fetchall()
        cur.close()
        return equipes

    except:
        print("Aucune equipe n'est dans la base")

