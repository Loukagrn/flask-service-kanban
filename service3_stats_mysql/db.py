# db.py — Nous gérons ici toute la logique de connexion à la base de données MySQL

# Nous importons le connecteur officiel MySQL pour Python
import mysql.connector
# Nous importons load_dotenv pour lire les variables du fichier .env
from dotenv import load_dotenv
# Nous importons os pour accéder aux variables d'environnement
import os

# Nous chargeons les variables d'environnement depuis le fichier .env
load_dotenv()


def get_connection():
    """
    Nous retournons une connexion MySQL configurée
    à partir des variables d'environnement.
    """
    # Nous créons et retournons une connexion MySQL avec les paramètres du fichier .env
    return mysql.connector.connect(
        # Nous récupérons l'adresse du serveur MySQL, localhost par défaut
        host=os.getenv('DB_HOST', 'localhost'),
        # Nous récupérons le port MySQL, 3306 par défaut
        port=int(os.getenv('DB_PORT', 3306)),
        # Nous récupérons le nom d'utilisateur MySQL depuis le fichier .env
        user=os.getenv('DB_USER'),
        # Nous récupérons le mot de passe MySQL depuis le fichier .env
        password=os.getenv('DB_PASSWORD'),
        # Nous récupérons le nom de la base de données depuis le fichier .env
        database=os.getenv('DB_NAME')
    )


def fetch_series(nom_serie):
    """
    Nous récupérons toutes les valeurs d'une série
    depuis la table 'donnees', triées par date.
    """
    # Nous ouvrons une connexion à la base de données
    conn = get_connection()
    # Nous créons un curseur pour exécuter nos requêtes SQL
    cursor = conn.cursor()

    # Nous utilisons %s pour éviter les injections SQL
    # Nous sélectionnons toutes les valeurs de la série demandée triées par date
    cursor.execute(
        'SELECT valeur FROM donnees WHERE nom_serie = %s ORDER BY date_mesure',
        (nom_serie,)
    )

    # Nous récupérons toutes les lignes retournées par la requête
    rows = cursor.fetchall()
    # Nous fermons le curseur pour libérer les ressources
    cursor.close()
    # Nous fermons la connexion à la base de données
    conn.close()

    # Nous signalons clairement si la série n'existe pas dans la BDD
    if not rows:
        raise ValueError(f"Aucune donnée trouvée pour la série '{nom_serie}'")

    # Nous convertissons chaque ligne en float et retournons la liste de valeurs
    return [float(row[0]) for row in rows]


def fetch_all_series_names():
    """
    Nous retournons la liste des noms de séries disponibles.
    """
    # Nous ouvrons une connexion à la base de données
    conn = get_connection()
    # Nous créons un curseur pour exécuter notre requête SQL
    cursor = conn.cursor()
    # Nous sélectionnons tous les noms de séries distincts triés alphabétiquement
    cursor.execute('SELECT DISTINCT nom_serie FROM donnees ORDER BY nom_serie')
    # Nous récupérons toutes les lignes retournées par la requête
    rows = cursor.fetchall()
    # Nous fermons le curseur pour libérer les ressources
    cursor.close()
    # Nous fermons la connexion à la base de données
    conn.close()
    # Nous retournons une liste avec uniquement les noms de séries
    return [row[0] for row in rows]