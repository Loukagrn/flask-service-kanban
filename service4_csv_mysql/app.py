# On importe les outils dont on a besoin
from flask import Flask, request, jsonify  # Flask = créer le serveur web, request = lire ce qu'on reçoit, jsonify = renvoyer du JSON
import pandas as pd                         # pandas = lire et manipuler le fichier CSV
import mysql.connector                      # mysql.connector = se connecter à la base de données MySQL
from dotenv import load_dotenv              # load_dotenv = lire le fichier .env pour récupérer les identifiants
import os                                   # os = accéder aux variables d'environnement (.env)
import io                                   # io = lire le fichier CSV depuis la mémoire sans le sauvegarder sur le disque

# On charge le fichier .env qui contient DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
load_dotenv()
# On crée l'application Flask
app = Flask(__name__)

# Les colonnes OBLIGATOIRES dans le CSV (sans elles, on refuse le fichier)
COLONNES_REQUISES = {'nom_serie', 'valeur'}

# Toutes les colonnes qu'on accepte (les autres seront ignorées)
COLONNES_VALIDES = {'nom_serie', 'valeur', 'categorie', 'date_mesure'}

# Taille maximum autorisée pour le fichier CSV : 5 Mo
TAILLE_MAX_OCTETS = 5 * 1024 * 1024  # 5 Mo en octets

# --- FONCTION : Se connecter à MySQL ---
def get_connection():
    # On lit les identifiants depuis le fichier .env et on retourne une connexion MySQL
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),   # Adresse du serveur MySQL (localhost = sur ce PC)
        user=os.getenv('DB_USER'),                # Nom d'utilisateur MySQL (ex: root)
        password=os.getenv('DB_PASSWORD'),        # Mot de passe MySQL
        database=os.getenv('DB_NAME')             # Nom de la base de données (flask_kanban)
    )

# --- ROUTE 1 : Charger un fichier CSV dans MySQL ---
# Cette route reçoit un fichier CSV envoyé en POST et l'insère dans la table "donnees"
@app.route('/upload/csv', methods=['POST'])
def upload_csv():
    # -----------------------------------------------
    # ÉTAPE 1 : Vérifier que le fichier est bien envoyé
    # -----------------------------------------------

    # On vérifie que la requête contient bien une clé "file"
    if 'file' not in request.files:
        # Si non → on renvoie une erreur 400 (Bad Request)
        return jsonify({'erreur': 'Aucun fichier envoyé (clé "file" manquante)'}), 400

    # On récupère le fichier envoyé
    file = request.files['file']

    # On vérifie que le nom du fichier n'est pas vide
    if file.filename == '':
        return jsonify({'erreur': 'Nom de fichier vide'}), 400

    # On vérifie que le fichier se termine bien par ".csv"
    if not file.filename.endswith('.csv'):
        return jsonify({'erreur': 'Seuls les fichiers .csv sont acceptés'}), 400

    # -----------------------------------------------
    # ÉTAPE 2 : Lire le contenu du fichier CSV
    # -----------------------------------------------
    try:
        # On lit tous les octets (bytes) du fichier
        content = file.read()
        # On vérifie que le fichier ne dépasse pas 5 Mo
        if len(content) > TAILLE_MAX_OCTETS:
            return jsonify({'erreur': 'Fichier trop volumineux (max 5 Mo)'}), 413
        # On transforme les octets en tableau pandas (comme un Excel en mémoire)
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        # Si la lecture échoue (fichier corrompu etc.) → erreur 400
        return jsonify({'erreur': f'Lecture CSV impossible : {e}'}), 400

    # -----------------------------------------------
    # ÉTAPE 3 : Vérifier que les colonnes obligatoires sont présentes
    # -----------------------------------------------
    # On calcule quelles colonnes obligatoires sont absentes du CSV
    colonnes_manquantes = COLONNES_REQUISES - set(df.columns)
    if colonnes_manquantes:
        # Si des colonnes manquent → on renvoie une erreur avec la liste des colonnes manquantes
        return jsonify({
            'erreur': 'Colonnes obligatoires manquantes',
            'manquantes': list(colonnes_manquantes)
        }), 400

    # -----------------------------------------------
    # ÉTAPE 4 : Nettoyer les données
    # -----------------------------------------------
    # On garde seulement les colonnes qu'on connaît (on supprime les colonnes inconnues)
    df = df[[c for c in df.columns if c in COLONNES_VALIDES]]
    # On convertit la colonne "valeur" en nombre
    # Si une valeur n'est pas un nombre (ex: "abc"), elle devient NaN (vide)
    df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
    # On compte combien de lignes ont une valeur invalide (NaN)
    lignes_invalides = df['valeur'].isna().sum()
    # On supprime les lignes avec une valeur invalide
    df.dropna(subset=['valeur'], inplace=True)

    # Si après nettoyage il ne reste aucune ligne → erreur
    if df.empty:
        return jsonify({'erreur': 'Aucune ligne valide dans le CSV'}), 400

    # -----------------------------------------------
    # ÉTAPE 5 : Insérer les données dans MySQL
    # -----------------------------------------------
    try:
        # On ouvre la connexion à MySQL
        conn = get_connection()
        # On crée un curseur (outil pour exécuter des requêtes SQL)
        cursor = conn.cursor()
        # Compteur de lignes insérées
        insertions = 0
        # On parcourt chaque ligne du tableau pandas
        for _, row in df.iterrows():
            # On exécute une requête SQL INSERT pour insérer la ligne dans la table "donnees"
            cursor.execute(
                'INSERT INTO donnees (nom_serie, valeur, categorie, date_mesure)'
                ' VALUES (%s, %s, %s, %s)',
                (
                    str(row['nom_serie']),    # Nom de la série (ex: serie_A)
                    float(row['valeur']),     # Valeur numérique (ex: 12.50)
                    # Si la colonne "categorie" existe dans le CSV → on la met, sinon None (NULL en SQL)
                    str(row['categorie']) if 'categorie' in df.columns else None,
                    # Idem pour "date_mesure"
                    str(row['date_mesure']) if 'date_mesure' in df.columns else None,
                )
            )
            insertions += 1  # On incrémente le compteur
        # On valide toutes les insertions (sans ça, rien n'est sauvegardé)
        conn.commit()
        # On ferme le curseur et la connexion
        cursor.close()
        conn.close()
    except Exception as e:
        # Si une erreur SQL arrive → on renvoie une erreur 500
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500

    # -----------------------------------------------
    # ÉTAPE 6 : Renvoyer la réponse de succès
    # -----------------------------------------------
    return jsonify({
        'statut': 'success',                          # Tout s'est bien passé
        'lignes_inserees': insertions,                # Nombre de lignes insérées
        'lignes_invalides_ignorees': int(lignes_invalides),  # Lignes ignorées car invalides
        'message': f'{insertions} ligne(s) chargée(s) dans la table donnees'
    }), 201  # 201 = Created (ressource créée avec succès)

# --- ROUTE 2 : Lister les séries disponibles ---
# Cette route lit la table "donnees" et retourne un résumé de chaque série
@app.route('/upload/series', methods=['GET'])
def list_series():
    try:
        # On se connecte à MySQL
        conn = get_connection()
        cursor = conn.cursor()

        # On exécute une requête SQL qui regroupe les données par série
        # Pour chaque série : nombre de points, date de début, date de fin
        cursor.execute(
            'SELECT nom_serie, COUNT(*) AS n, MIN(date_mesure), MAX(date_mesure)'
            ' FROM donnees GROUP BY nom_serie ORDER BY nom_serie'
        )
        # On récupère tous les résultats
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # On transforme les résultats en liste de dictionnaires JSON
        series = [
            {
                'serie': r[0],       # Nom de la série
                'n_points': r[1],    # Nombre de mesures
                'debut': str(r[2]),  # Date de la première mesure
                'fin': str(r[3])     # Date de la dernière mesure
            }
            for r in rows
        ]
        # On renvoie la liste des séries + le nombre total
        return jsonify({'series': series, 'total': len(series)})
    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500

# --- LANCEMENT DU SERVEUR ---
if __name__ == '__main__':
    # On lance Flask sur le port 5004
    # debug=True = affiche les erreurs en détail (utile pendant le développement)
    app.run(debug=True, port=5004)
