import psycopg2
import pandas as pd
from script.import_joueur import add_joueur

# Connection à la base de données
conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")
add_joueur("5000000000000000000010658", conn)
conn.close()