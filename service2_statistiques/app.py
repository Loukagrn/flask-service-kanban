from flask import Flask, request, jsonify
import numpy as np
import scipy.stats as stats

# on lance la machine flask
app = Flask(__name__)

# notre fonction magique pour pas répéter 50 fois les mêmes vérifications
def check_data(json_data, key='data'):
    # d'abord on regarde si le mec a envoyé un truc vide ou s'il a oublié la clé (comme 'data' ou 'x')
    if not json_data or key not in json_data:
        # si c'est pété, on lève une erreur qui va stopper le code ici
        raise ValueError(f"Clé '{key}' manquante dans le JSON.")
    
    # on extrait la liste qui est cachée derrière la clé
    liste = json_data[key]
    
    # là on vérifie deux trucs : est-ce que c'est bien un tableau [] (isinstance list) et est-ce qu'il est pas vide
    if not isinstance(liste, list) or len(liste) == 0:
        # si c'est pas un tableau ou que c'est vide, bim erreur
        raise ValueError(f"'{key}' doit être une liste non vide.")
        
    # c'est ici que ça inspecte le contenu : on prend les éléments un par un (le fameux 'for x in liste')
    for x in liste:
        # on vérifie si l'élément 'x' n'est PAS un entier (int) et n'est PAS un nombre à virgule (float)
        if not isinstance(x, (int, float)):
            # si y a un intrus (genre du texte "un"), on bloque tout direct avec une erreur de type
            raise TypeError("La liste doit contenir uniquement des nombres.")
            
    # si le code est arrivé jusqu'ici sans planter, c'est que la liste est parfaite, donc on la renvoie
    return liste


# route 1 : cette route sert à sortir toutes les statistiques de base d'un tableau de chiffres (moyenne, médiane, min, max, etc.)
@app.route('/stats/describe', methods=['POST'])
def get_describe():
    # on intercepte le json qui arrive dans la requête post du client
    req = request.get_json()
    
    # le gros bloc try/except : on teste les calculs, si un truc lève une erreur, on saute direct au bloc except en bas
    try:
        # on envoie les données reçues à notre fonction check_data pour isoler la liste sous la clé 'data'
        data = check_data(req, 'data')
        
        # la fonction stats.describe de scipy mouline le tableau et calcule automatiquement le min, le max et la variance
        res_scipy = stats.describe(data)
        
        # on utilise numpy pour calculer la moyenne et la médiane, et on force le type en float classique pour éviter les bugs d'encodage json de flask
        moyenne = float(np.mean(data))
        mediane = float(np.median(data))
        
        # sécurité mathématique : impossible de calculer une variance ou un écart-type si on n'a pas au moins 2 nombres
        if len(data) > 1:
            # np.std calcule l'écart-type. ddof=1 c'est pour calculer l'écart-type sur un échantillon (formule statistique standard)
            std_dev = float(np.std(data, ddof=1))
            variance = float(res_scipy.variance)
        else:
            # si l'utilisateur n'a envoyé qu'un seul nombre, on met l'écart-type et la variance à 0 pour pas que l'application plante
            std_dev, variance = 0.0, 0.0
        
        # si tout s'est bien passé, on package les résultats dans un dictionnaire et on renvoie ça au format json avec le code http 200
        return jsonify({
            'operation': 'statistiques_descriptives',
            'total_elements': len(data),
            'resultats': {
                'minimum': float(res_scipy.minmax[0]), # le min est stocké tout au début du tuple minmax renvoyé par scipy
                'maximum': float(res_scipy.minmax[1]), # le max est stocké juste après à l'indice 1
                'moyenne': round(moyenne, 4), # le round(..., 4) sert à limiter l'affichage à 4 chiffres après la virgule
                'mediane': round(mediane, 4),
                'variance': round(variance, 4),
                'ecart_type': round(std_dev, 4)
            }
        }), 200
        
    # si jamais check_data ou nos calculs ont levé une valueerror ou une typeerror, python s'arrête et atterrit ici
    except (ValueError, TypeError) as e:
        # on attrape le message de l'erreur stocké dans 'e', on le convertit en texte et on le renvoie proprement en json avec un code http 400
        return jsonify({'erreur': str(e)}), 400


# route 2 : cette route sert à mesurer la relation statistique entre deux listes de chiffres différentes (le coefficient de pearson)
@app.route('/stats/correlation', methods=['POST'])
def get_correlation():
    # on récupère le package json envoyé par l'utilisateur
    req = request.get_json()
    
    try:
        # pour faire une corrélation il nous faut deux variables, donc on extrait et on valide d'un côté la clé 'x' et de l'autre la clé 'y'
        x = check_data(req, 'x')
        y = check_data(req, 'y')
        
        # règle mathématique obligatoire : les deux listes de données doivent impérativement avoir le même nombre d'éléments pour être comparées point par point
        if len(x) != len(y):
            raise ValueError("Les listes 'x' and 'y' doivent faire la même taille.")
            
        # deuxième règle : il faut au minimum 2 points distincts dans l'espace pour pouvoir tracer une tendance ou une droite de corrélation
        if len(x) < 2:
            raise ValueError("Il faut au moins 2 éléments pour calculer la corrélation.")
            
        # la fonction pearsonr de scipy calcule d'un coup le coefficient de corrélation (r) et la p-value (la fiabilité mathématique du test)
        r_coeff, p_val = stats.pearsonr(x, y)
        
        # on renvoie les deux indicateurs calculés au format json avec le code de succès http 200
        return jsonify({
            'operation': 'correlation_pearson',
            'taille_listes': len(x),
            'resultats': {
                'coefficient_r': round(float(r_coeff), 4), # r proche de 1 veut dire que quand x monte, y monte aussi
                'p_value': round(float(p_val), 4) # p-value proche de 0 veut dire que le résultat est super fiable
            }
        }), 200
        
    # si les tailles diffèrent, s'il manque une clé ou s'il y a du texte dans les listes, on gère l'erreur proprement ici
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# route 3 : cette route exécute le test de shapiro-wilk pour vérifier si la distribution de nos données ressemble à une courbe en cloche (loi normale)
@app.route('/stats/normalite', methods=['POST'])
def get_normalite():
    # on extrait le dictionnaire json de la requête post
    req = request.get_json()
    
    try:
        # on valide que la liste d'entrée sous la clé 'data' est correcte et ne contient que des nombres
        data = check_data(req, 'data')
        
        # contrainte technique de la formule de shapiro-wilk : l'algorithme a mathématiquement besoin d'au moins 3 valeurs pour calculer des probabilités cohérentes
        if len(data) < 3:
            raise ValueError("Le test de Shapiro-Wilk nécessite au moins 3 valeurs.")
            
        # la fonction shapiro de scipy calcule la statistique de test (w) et l'indicateur de probabilité (la p-value)
        w_stat, p_val = stats.shapiro(data)
        
        # la règle d'or en statistiques : si la p-value est strictement supérieure au seuil classique de 0.05 (5%), on valide que les données suivent bien une loi normale (true)
        suit_loi_normale = bool(p_val > 0.05)
        
        # on retourne la réponse structurée avec notre indicateur booléen (true ou false) et un code http 200
        return jsonify({
            'operation': 'test_normalite_shapiro',
            'total_elements': len(data),
            'resultats': {
                'statistique_w': round(float(w_stat), 4), # l'indicateur de forme du test de shapiro
                'p_value': round(float(p_val), 4), # le niveau de significativité statistique
                'suit_une_loi_normale': suit_loi_normale # renvoie true si c'est normal, false si ça l'est pas
            }
        }), 200
        
    # si la validation échoue ou s'il y a moins de 3 éléments, on intercepte le crash et on renvoie le message d'erreur avec un code http 400
    except (ValueError, TypeError) as e:
        return jsonify({'erreur': str(e)}), 400


# point d'entrée principal du script python
if __name__ == '__main__':
    # host='0.0.0.0' configure le serveur pour accepter les requêtes de n'importe quelle adresse réseau locale
    # port=5002 définit le canal d'écoute de notre api de statistiques
    # debug=True active le mode de développement qui recharge automatiquement le code en direct à chaque sauvegarde de fichier
    app.run(host='0.0.0.0', port=5002, debug=True)