from flask import Flask, request, jsonify
import numpy as np
import scipy.stats as stats

# On crée l'objet Flask en premier pour éviter le NameError
app = Flask(__name__)

# --- Fonction pour vérifier le JSON reçu ---
def valider_les_donnees(structure_json, cle_a_verifier='data'):
    # On check si le JSON est vide ou si la clé 'data' n'existe pas
    if not structure_json or cle_a_verifier not in structure_json:
        raise ValueError(f"Erreur : Il manque la clé '{cle_a_verifier}' dans le JSON envoyé.")
    
    # On extrait la liste de la clé 'data'
    liste_nombres = structure_json[cle_a_verifier]
    
    # On check si c'est bien un format liste et qu'elle n'est pas vide
    if not isinstance(liste_nombres, list) or len(liste_nombres) == 0:
        raise ValueError(f"Erreur : '{cle_a_verifier}' doit être une liste avec des valeurs.")
        
    # Boucle pour vérifier chaque élément de la liste
    for element in liste_nombres:
        # Si un élément n'est ni un entier ni un décimal, on bloque
        if not isinstance(element, (int, float)):
            raise TypeError("Erreur : La liste ne doit contenir que des nombres !")
            
    # Tout est bon, on renvoie la liste validée
    return liste_nombres


# --- Route 1 : Calcul des stats descriptives ---
@app.route('/stats/describe', methods=['POST'])
def calculer_les_stats_de_base():
    # Récupération du JSON brut envoyé en POST
    donnees_recues = request.get_json()
    
    try:
        # Envoi du JSON à la fonction de validation du dessus
        mes_nombres = valider_les_donnees(donnees_recues, 'data')
        
        # SciPy calcule min, max et variance d'un coup
        infos_scipy = stats.describe(mes_nombres)
        
        # NumPy calcule la moyenne (convertie en float standard)
        la_moyenne = float(np.mean(mes_nombres))
        
        # NumPy trouve la valeur centrale (médiane)
        la_mediane = float(np.median(mes_nombres))
        
        # Condition : calcul possible uniquement si on a au moins 2 nombres
        if len(mes_nombres) > 1:
            # Écart-type avec ddof=1 pour la formule d'échantillon
            l_ecart_type = float(np.std(mes_nombres, ddof=1))
            # Récupération de la variance calculée par SciPy
            la_variance = float(infos_scipy.variance)
        else:
            # Si 1 seul nombre, l'écart-type et la variance n'existent pas (0)
            l_ecart_type = 0.0
            la_variance = 0.0
        
        # Structure du dictionnaire de réponse
        reponse_json = {
            'operation': 'statistiques_descriptives',
            'total_elements': len(mes_nombres),
            'resultats': {
                # Extraction du min (index 0 de minmax)
                'minimum': float(infos_scipy.minmax[0]),
                # Extraction du max (index 1 de minmax)
                'maximum': float(infos_scipy.minmax[1]),
                # Arrondis à 4 décimales pour l'affichage
                'moyenne': round(la_moyenne, 4),
                'mediane': round(la_mediane, 4),
                'variance': round(la_variance, 4),
                'ecart_type': round(l_ecart_type, 4)
            }
        }
        # Renvoi de la réponse avec le code HTTP 200 (Succès)
        return jsonify(reponse_json), 200
        
    except (ValueError, TypeError) as erreur_detectee:
        # Capture de l'erreur et renvoi du message avec le code HTTP 400
        return jsonify({'erreur': str(erreur_detectee)}), 400


if __name__ == '__main__':
    # Configuration du serveur sur le port attribué (5002)
    app.run(host='0.0.0.0', port=5002, debug=True)