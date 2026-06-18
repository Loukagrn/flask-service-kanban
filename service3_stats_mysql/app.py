# app.py — Nous exposons ici les routes REST du Service 3

from flask import Flask, request, jsonify
import numpy as np
from scipy import stats
from db import fetch_series, fetch_all_series_names

app = Flask(__name__)


# Route 1 — GET /db/stats/describe?serie=serie_A
@app.route('/db/stats/describe', methods=['GET'])
def db_describe():
    """
    Nous calculons les statistiques descriptives d'une série depuis MySQL.
    """
    nom_serie = request.args.get('serie')

    if not nom_serie:
        return jsonify({'erreur': "Paramètre 'serie' manquant dans l'URL"}), 400

    try:
        values = np.array(fetch_series(nom_serie))

        result = {
            'serie':      nom_serie,
            'n':          int(len(values)),
            'moyenne':    round(float(np.mean(values)), 4),
            'mediane':    round(float(np.median(values)), 4),
            'ecart_type': round(float(np.std(values, ddof=1)), 4),
            'variance':   round(float(np.var(values, ddof=1)), 4),
            'minimum':    round(float(np.min(values)), 4),
            'maximum':    round(float(np.max(values)), 4),
            'q1':         round(float(np.percentile(values, 25)), 4),
            'q3':         round(float(np.percentile(values, 75)), 4),
        }

        return jsonify({'source': 'mysql', 'resultat': result})

    except ValueError as e:
        return jsonify({'erreur': str(e)}), 404

    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500


# Route 2 — GET /db/stats/correlation?serie_x=serie_A&serie_y=serie_B
@app.route('/db/stats/correlation', methods=['GET'])
def db_correlation():
    """
    Nous calculons la corrélation de Pearson entre deux séries depuis MySQL.
    """
    serie_x = request.args.get('serie_x')
    serie_y = request.args.get('serie_y')

    if not serie_x or not serie_y:
        return jsonify({'erreur': 'Paramètres serie_x et serie_y requis'}), 400

    try:
        x = np.array(fetch_series(serie_x))
        y = np.array(fetch_series(serie_y))

        n = min(len(x), len(y))
        x, y = x[:n], y[:n]

        r, p_value = stats.pearsonr(x, y)

        interpretation = (
            'forte'   if abs(r) > 0.7 else
            'modérée' if abs(r) > 0.4 else
            'faible'
        )

        return jsonify({
            'source': 'mysql',
            'series': {'x': serie_x, 'y': serie_y, 'n_points': n},
            'resultat': {
                'r':              round(float(r), 4),
                'p_value':        round(float(p_value), 6),
                'interpretation': interpretation,
                'significatif':   bool(p_value < 0.05)
            }
        })

    except ValueError as e:
        return jsonify({'erreur': str(e)}), 404

    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500


# Route bonus — GET /db/series
@app.route('/db/series', methods=['GET'])
def list_series():
    """Nous listons toutes les séries disponibles dans la BDD."""
    try:
        series = fetch_all_series_names()
        return jsonify({'series': series, 'total': len(series)})
    except Exception as e:
        return jsonify({'erreur': 'Erreur base de données', 'detail': str(e)}), 500


# Route santé — GET /health
@app.route('/health', methods=['GET'])
def health():
    """Nous vérifions rapidement que le service tourne."""
    return jsonify({'statut': 'ok', 'service': 'Service 3', 'port': 5003})


if __name__ == '__main__':
    app.run(debug=True, port=5003)