from flask import Flask, request, jsonify
import numpy as np
import scipy.stats as stats

app = Flask(__name__)

# --- Fonction pour vérifier le JSON reçu ---
def valider_les_donnees(structure_json, cle_a_verifier='data'):
    # On check si le JSON est vide ou si la clé 'data' n'existe pas
    if not structure_json or cle_a_verifier not in structure_json:
        raise ValueError(f"Erreur : Il manque la clé '{cle_a_verifier}' dans le JSON envoyé.")
    
    # On extrait la liste de la clé demandée
    liste_nombres = structure_json[cle_a_verifier]
    
    # On check si c'est bien un format liste et qu'elle n'est pas vide
    if not isinstance(liste_nombres, list) or len(liste_nombres) == 0:
        raise ValueError(f"Erreur : '{cle_a_verifier}' doit être une liste avec des valeurs.")
        
    # Boucle pour vérifier chaque élément de la liste
    for element in liste_nombres:
        if not isinstance(element, (int, float)):
            raise TypeError("Erreur : La liste ne doit contenir que des nombres !")
            
    return liste_nombres


# --- Route 1 : Calcul des stats descriptives ---
@app.route('/stats/describe', methods=['POST'])
def calculer_les_stats_de_base():
    donnees_recues = request.get_json()
    
    try:
        mes_nombres = valider_les_donnees(donnees_recues, 'data')
        infos_scipy = stats.describe(mes_nombres)
        la_moyenne = float(np.mean(mes_nombres))
        la_mediane = float(np.median(mes_nombres))
        
        if len(mes_nombres) > 1:
            l_ecart_type = float(np.std(mes_nombres, ddof=1))
            la_variance = float(infos_scipy.variance)
        else:
            l_ecart_type = 0.0
            la_variance = 0.0
        
        reponse_json = {
            'operation': 'statistiques_descriptives',
            'total_elements': len(mes_nombres),
            'resultats': {
                'minimum': float(infos_scipy.minmax[0]),
                'maximum': float(infos_scipy.minmax[1]),
                'moyenne': round(la_moyenne, 4),
                'mediane': round(la_mediane, 4),
                'variance': round(la_variance, 4),
                'ecart_type': round(l_ecart_type, 4)
            }
        }
        return jsonify(reponse_json), 200
        
    except (ValueError, TypeError) as erreur_detectee:
        return jsonify({'erreur': str(erreur_detectee)}), 400


# --- Route 2 : Coefficient de corrélation de Pearson ---
@app.route('/stats/correlation', methods=['POST'])
def calculer_la_correlation():
    donnees_recues = request.get_json()
    
    try:
        # On valide les deux listes séparément
        liste_x = valider_les_donnees(donnees_recues, 'x')
        liste_y = valider_les_donnees(donnees_recues, 'y')
        
        # On vérifie qu'elles ont la même longueur
        if len(liste_x) != len(liste_y):
            raise ValueError("Erreur : Les listes 'x' et 'y' doivent avoir la même taille.")
            
        # Il faut au moins 2 éléments
        if len(liste_x) < 2:
            raise ValueError("Erreur : Il faut au moins 2 éléments dans les listes.")
            
        # Calcul du coefficient r et de la p-value
        coefficient_r, p_value = stats.pearsonr(liste_x, liste_y)
        
        reponse_json = {
            'operation': 'correlation_pearson',
            'taille_listes': len(liste_x),
            'resultats': {
                'coefficient_r': round(float(coefficient_r), 4),
                'p_value': round(float(p_value), 4)
            }
        }
        return jsonify(reponse_json), 200
        
    except (ValueError, TypeError) as erreur_detectee:
        return jsonify({'erreur': str(erreur_detectee)}), 400

# --- Route 3 : Test de normalité de Shapiro-Wilk (Issue #10) ---
@app.route('/stats/normalite', methods=['POST'])
def verifier_la_normalite():
    donnees_recues = request.get_json()
    
    try:
        # On valide la liste de nombres avec notre fonction de sécurité
        mes_nombres = valider_les_donnees(donnees_recues, 'data')
        
        # Sécurité : Shapiro-Wilk demande entre 3 et 5000 individus
        if len(mes_nombres) < 3:
            raise ValueError("Erreur : Le test de Shapiro-Wilk nécessite au moins 3 nombres.")
            
        # SciPy calcule la statistique W et la p-value
        statistique_w, p_value = stats.shapiro(mes_nombres)
        
        # Si la p-value est supérieure à 0.05, les données suivent une loi normale
        est_normale = bool(p_value > 0.05)
        
        reponse_json = {
            'operation': 'test_normalite_shapiro',
            'total_elements': len(mes_nombres),
            'resultats': {
                'statistique_w': round(float(statistique_w), 4),
                'p_value': round(float(p_value), 4),
                'suit_une_loi_normale': est_normale
            }
        }
        return jsonify(reponse_json), 200
        
    except (ValueError, TypeError) as erreur_detectee:
        return jsonify({'erreur': str(erreur_detectee)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)