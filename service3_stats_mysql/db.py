# db.py — Nous gérons ici toute la logique de connexion à la base de données MySQL

import mysql.connector
from dotenv import load_dotenv
import os

# Nous chargeons les variables d'environnement depuis le fichier .env
load_dotenv()


def get_connection():
    """
    Nous retournons une connexion MySQL configurée
    à partir des variables d'environnement.
    """
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )


def fetch_series(nom_serie):
    """
    Nous récupérons toutes les valeurs d'une série
    depuis la table 'donnees', triées par date.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Nous utilisons %s pour éviter les injections SQL
    cursor.execute(
        'SELECT valeur FROM donnees WHERE nom_serie = %s ORDER BY date_mesure',
        (nom_serie,)
    )

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Nous signalons clairement si la série n'existe pas
    if not rows:
        raise ValueError(f"Aucune donnée trouvée pour la série '{nom_serie}'")

    return [float(row[0]) for row in rows]


def fetch_all_series_names():
    """
    Nous retournons la liste des noms de séries disponibles.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT nom_serie FROM donnees ORDER BY nom_serie')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]