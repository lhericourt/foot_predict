import psycopg2
import pandas as pd
from objets  import *

# Connection à la base de données
conn = psycopg2.connect(host="localhost", dbname="foot_dev", user="foot", password="torche")