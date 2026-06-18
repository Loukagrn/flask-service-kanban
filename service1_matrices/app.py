# Importation de Flask (pour créer le serveur web), request (pour lire les données reçues) et jsonify (pour formater la réponse)
from flask import Flask, request, jsonify
# Importation de CORS pour autoriser les requêtes web locales (évite les blocages de sécurité du navigateur)
from flask_cors import CORS
# Importation de NumPy, la puissante bibliothèque de calcul mathématique, renommée "np" pour aller plus vite
import numpy as np

# Création de l'application (le serveur web en lui-même)
app = Flask(__name__)
# Application des règles CORS à notre serveur
CORS(app)

# Définition d'une fonction d'aide pour transformer le JSON reçu en véritable matrice mathématique
def parse_matrix(data, key):
    """Convertit une liste de listes en tableau NumPy."""
    # On "essaie" de faire la conversion
    try:
        # On extrait la matrice (ex: 'A') des données et on la force à devenir un tableau de nombres à virgule (float)
        return np.array(data[key], dtype=float)
    # Si la clé 'A' n'existe pas, ou si les données ne sont pas des nombres
    except (KeyError, ValueError) as e:
        # On déclenche une erreur claire pour avertir que la matrice est invalide
        raise ValueError(f"Matrice '{key}' invalide : {e}")

# --- ROUTE 1 : ADDITION ---
# On crée la porte d'entrée pour l'addition, accessible uniquement en envoyant des données (POST)
@app.route('/matrices/add', methods=['POST'])
def add_matrices():
    # On récupère le "colis" JSON envoyé par le client (le navigateur ou le test)
    data = request.get_json()
    try:
        # On utilise notre fonction d'aide pour transformer les données "A" et "B" en tableaux NumPy
        A = parse_matrix(data, 'A')
        B = parse_matrix(data, 'B')
        # Règle mathématique : pour additionner, les deux matrices doivent avoir exactement la même taille (shape)
        if A.shape != B.shape:
            # Si les tailles sont différentes, on renvoie une erreur 400 au client
            return jsonify({'erreur': 'Dimensions incompatibles'}), 400
        # On fait l'addition avec NumPy, et on retransforme le résultat en liste Python classique (.tolist())
        result = (A + B).tolist()
        # On renvoie la réponse finale au client au format JSON (statut 200 par défaut)
        return jsonify({'operation': 'addition', 'resultat': result})
    # Si parse_matrix a déclenché une erreur plus haut, on l'attrape ici
    except (ValueError, TypeError) as e:
        # On renvoie l'erreur au client
        return jsonify({'erreur': str(e)}), 400


# --- ROUTE 2 : MULTIPLICATION ---
# Création de la route pour multiplier deux matrices
@app.route('/matrices/multiply', methods=['POST'])
def multiply_matrices():
    # Lecture des données JSON reçues
    data = request.get_json()
    try:
        # Extraction et conversion des matrices A et B
        A = parse_matrix(data, 'A')
        B = parse_matrix(data, 'B')
        # Règle mathématique : le nombre de colonnes de A (shape[1]) doit être égal au nombre de lignes de B (shape[0])
        if A.shape[1] != B.shape[0]:
            # Si la règle n'est pas respectée, la multiplication est impossible : on renvoie une erreur
            return jsonify({'erreur': 'Colonnes(A) doit egalerLignes(B)'}), 400
        # On utilise la fonction dot() de NumPy pour faire le produit matriciel, puis on le convertit en liste
        result = np.dot(A, B).tolist()
        # On renvoie le résultat formaté en JSON
        return jsonify({'operation': 'multiplication', 'resultat': result})
    # Capture des erreurs de conversion ou de format
    except (ValueError, TypeError) as e:
        # Renvoi du message d'erreur avec le code HTTP 400
        return jsonify({'erreur': str(e)}), 400


# --- ROUTE 3 : TRANSPOSITION ---
# Création de la route pour transposer une matrice (inverser lignes et colonnes)
@app.route('/matrices/transpose', methods=['POST'])
def transpose_matrix():
    # Lecture des données JSON
    data = request.get_json()
    try:
        # Ici, on n'a besoin que d'une seule matrice : on extrait seulement 'A'
        A = parse_matrix(data, 'A')
        # On utilise la propriété .T de NumPy qui calcule instantanément la transposée, puis on convertit en liste
        result = A.T.tolist()
        # On renvoie le résultat JSON
        return jsonify({'operation': 'transposee', 'resultat': result})
    # Gestion des erreurs
    except (ValueError, TypeError) as e:
        # Renvoi de l'erreur au client
        return jsonify({'erreur': str(e)}), 400
    

# --- ROUTE 4 : DÉTERMINANT ---
# Création de la route pour calculer le déterminant
@app.route('/matrices/determinant', methods=['POST'])
def determinant_matrix():
    # Lecture des données JSON
    data = request.get_json()
    try:
        # On extrait la matrice 'A'
        A = parse_matrix(data, 'A')
        # Règle mathématique : un déterminant ne se calcule que sur une matrice carrée (lignes == colonnes)
        if A.shape[0] != A.shape[1]:
            # Si elle n'est pas carrée, on stoppe tout et on renvoie une erreur
            return jsonify({'erreur': 'La matrice doit etre carree'}), 400
        # On utilise le module d'algèbre linéaire (linalg) de NumPy pour calculer le déterminant
        det = np.linalg.det(A)
        # On renvoie le résultat arrondi à 6 chiffres après la virgule pour que ce soit propre
        return jsonify({'operation': 'determinant', 'resultat': round(det, 6)})
    # Gestion des erreurs
    except (ValueError, TypeError) as e:
        # Renvoi de l'erreur
        return jsonify({'erreur': str(e)}), 400


# --- ROUTE 5 : INVERSE ---
# Création de la route pour calculer l'inverse d'une matrice
@app.route('/matrices/inverse', methods=['POST'])
def inverse_matrix():
    # Lecture des données JSON
    data = request.get_json()
    try:
        # On extrait la matrice 'A'
        A = parse_matrix(data, 'A')
        
        # Vérification 1 : La matrice est-elle carrée ? (Même règle que pour le déterminant)
        if A.shape[0] != A.shape[1]:
            # Refus du calcul si elle n'est pas carrée
            return jsonify({'erreur': 'La matrice doit etre carree'}), 400
            
        # Vérification 2 : On calcule le déterminant
        det = np.linalg.det(A)
        # Si le déterminant vaut 0, la matrice est "singulière" et ne peut mathématiquement pas être inversée
        if round(det, 6) == 0:
            # On bloque le calcul et on explique pourquoi au client
            return jsonify({'erreur': 'La matrice n est pas inversible (determinant nul)'}), 400
            
        # Si toutes les vérifications sont bonnes, on utilise NumPy pour calculer la matrice inverse
        inv = np.linalg.inv(A).tolist()
        # On renvoie le résultat JSON
        return jsonify({'operation': 'inverse', 'resultat': inv})
        
    # Gestion des erreurs (mauvais format, pas de données...)
    except (ValueError, TypeError) as e:
        # Renvoi de l'erreur
        return jsonify({'erreur': str(e)}), 400
    
# Condition qui vérifie si ce fichier est le programme principal exécuté par Python
if __name__ == '__main__':
    # Démarrage du serveur Flask sur le port 5001. debug=True permet de recharger automatiquement le code si on le modifie.
    app.run(debug=True, port=5001)