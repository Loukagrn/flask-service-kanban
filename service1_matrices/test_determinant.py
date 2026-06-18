import requests

url = 'http://localhost:5001/matrices/determinant'

# Test avec une matrice carrée 2x2
payload_ok = {"A": [[1, 2], [3, 4]]}

print("--- Test Déterminant (Matrice Carrée) ---")
response = requests.post(url, json=payload_ok)
print(f"Statut HTTP : {response.status_code}")
print(f"Résultat : {response.json()}")

# Test avec une matrice non carrée pour vérifier l'erreur 400
payload_err = {"A": [[1, 2, 3], [4, 5, 6]]}
response_err = requests.post(url, json=payload_err)
print("\n--- Test Déterminant (Matrice Non Carrée) ---")
print(f"Statut HTTP (Attendu 400) : {response_err.status_code}")
print(f"Réponse : {response_err.json()}")