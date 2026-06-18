# app.py — Nous exposons ici les routes REST du Service 3

# Nous importons Flask et les outils nécessaires pour créer notre API REST
from flask import Flask, request, jsonify
# Nous importons CORS pour autoriser les requêtes depuis le navigateur
from flask_cors import CORS
# Nous importons numpy pour les calculs mathématiques sur les tableaux
import numpy as np
# Nous importons scipy.stats pour les calculs statistiques avancés
from scipy import stats
# Nous importons nos fonctions de connexion à la base de données MySQL
from db import fetch_series, fetch_all_series_names

# Nous créons l'application Flask
app = Flask(__name__)

# Nous activons le CORS pour autoriser les requêtes depuis le navigateur
CORS(app)


# Route 1 — GET /db/stats/describe?serie=serie_A
@app.route('/db/stats/describe', methods=['GET'])
def db_describe():
    """
    Nous calculons les statistiques descriptives d'une série depuis MySQL.
    """
    # Nous récupérons le paramètre 'serie' passé dans l'URL
    nom_serie = request.args.get('serie')

    # Nous vérifions que le paramètre est bien présent, sinon on retourne une erreur 400
    if not nom_serie:
        return jsonify({'erreur': "Paramètre 'serie' manquant dans l'URL"}), 400

    try:
        # Nous récupérons les valeurs de la série depuis MySQL et on les convertit en tableau numpy
        values = np.array(fetch_series(nom_serie))

        # Nous calculons toutes les statistiques descriptives de la série
        result = {
            # Nous stockons le nom de la série
            'serie':      nom_serie,
            # Nous comptons le nombre de valeurs dans la série
            'n':          int(len(values)),
            # Nous calculons la moyenne de la série
            'moyenne':    round(float(np.mean(values)), 4),
            # Nous calculons la médiane de la série
            'mediane':    round(float(np.median(values)), 4),
            # Nous calculons l'écart-type non biaisé (ddof=1) de la série
            'ecart_type': round(float(np.std(values, ddof=1)), 4),
            # Nous calculons la variance non biaisée (ddof=1) de la série
            'variance':   round(float(np.var(values, ddof=1)), 4),
            # Nous trouvons la valeur minimale de la série
            'minimum':    round(float(np.min(values)), 4),
            # Nous trouvons la valeur maximale de la série
            'maximum':    round(float(np.max(values)), 4),
            # Nous calculons le premier quartile (25%) de la série
            'q1':         round(float(np.percentile(values, 25)), 4),
            # Nous calculons le troisième quartile (75%) de la série
            'q3':         round(float(np.percentile(values, 75)), 4),
        }

        # Nous retournons le résultat en JSON avec la source mysql
        return jsonify({'source': 'mysql', 'resultat': result})

    except ValueError as e:
        # Nous retournons une erreur 404 si la série n'existe pas dans la BDD
        return jsonify({'erreur': str(e)}), 404

    except Exception as e:
        # Nous retournons une erreur 500 si une erreur inattendue se produit
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500


# Route 2 — GET /db/stats/correlation?serie_x=serie_A&serie_y=serie_B
@app.route('/db/stats/correlation', methods=['GET'])
def db_correlation():
    """
    Nous calculons la corrélation de Pearson entre deux séries depuis MySQL.
    """
    # Nous récupérons les deux noms de séries passés en paramètres dans l'URL
    serie_x = request.args.get('serie_x')
    serie_y = request.args.get('serie_y')

    # Nous vérifions que les deux paramètres sont bien présents sinon on retourne une erreur 400
    if not serie_x or not serie_y:
        return jsonify({'erreur': 'Paramètres serie_x et serie_y requis'}), 400

    try:
        # Nous récupérons les valeurs des deux séries depuis MySQL
        x = np.array(fetch_series(serie_x))
        y = np.array(fetch_series(serie_y))

        # Nous alignons les deux séries sur la longueur de la plus courte
        n = min(len(x), len(y))
        x, y = x[:n], y[:n]

        # Nous calculons le coefficient de corrélation de Pearson et la p-value
        r, p_value = stats.pearsonr(x, y)

        # Nous interprétons la force de la corrélation selon la valeur de r
        interpretation = (
            # Nous considérons la corrélation forte si r > 0.7
            'forte'   if abs(r) > 0.7 else
            # Nous considérons la corrélation modérée si r > 0.4
            'modérée' if abs(r) > 0.4 else
            # Nous considérons la corrélation faible sinon
            'faible'
        )

        # Nous retournons le résultat complet en JSON
        return jsonify({
            # Nous indiquons que les données viennent de MySQL
            'source': 'mysql',
            # Nous indiquons les noms des séries et le nombre de points utilisés
            'series': {'x': serie_x, 'y': serie_y, 'n_points': n},
            'resultat': {
                # Nous retournons le coefficient de corrélation arrondi à 4 décimales
                'r':              round(float(r), 4),
                # Nous retournons la p-value arrondie à 6 décimales
                'p_value':        round(float(p_value), 6),
                # Nous retournons l'interprétation textuelle de la corrélation
                'interpretation': interpretation,
                # Nous indiquons si la corrélation est statistiquement significative
                'significatif':   bool(p_value < 0.05)
            }
        })

    except ValueError as e:
        # Nous retournons une erreur 404 si une des séries n'existe pas dans la BDD
        return jsonify({'erreur': str(e)}), 404

    except Exception as e:
        # Nous retournons une erreur 500 si une erreur inattendue se produit
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500


# Route bonus — GET /db/series
@app.route('/db/series', methods=['GET'])
def list_series():
    """Nous listons toutes les séries disponibles dans la BDD."""
    try:
        # Nous récupérons tous les noms de séries depuis MySQL
        series = fetch_all_series_names()
        # Nous retournons la liste des séries et leur nombre total
        return jsonify({'series': series, 'total': len(series)})
    except Exception as e:
        # Nous retournons une erreur 500 si une erreur inattendue se produit
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500


# Route santé — GET /health
@app.route('/health', methods=['GET'])
def health():
    """Nous vérifions rapidement que le service tourne."""
    # Nous retournons un simple message de confirmation que le service est actif
    return jsonify({'statut': 'ok', 'service': 'Service 3', 'port': 5003})


# Nous lançons le serveur Flask sur le port 5003 en mode debug
if __name__ == '__main__':
    app.run(debug=True, port=5003)