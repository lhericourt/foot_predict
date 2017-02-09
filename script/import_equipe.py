import psycopg2
import pandas as pd
from objets.equipe import Equipe, get_equipe_fromDB
from objets import *

# Connection à la base de données
conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
equipes = pd.read_csv(filepath_or_buffer="./../data/equipes.csv", sep=";", names=['code', 'libelle'])


for i, eq in equipes.iterrows():
    if (get_equipe_fromDB(eq["code"], conn)):
        print("Equipe {} déjà existante".format(eq["libelle"]))
    else:
        Equipe(eq["code"], eq["libelle"]).create_equipe(conn)

conn.close()
