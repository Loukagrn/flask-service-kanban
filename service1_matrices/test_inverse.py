import requests

url = 'http://localhost:5001/matrices/inverse'

# Test 1 : Matrice inversible
payload_ok = {"A": [[1, 2], [3, 4]]}
print("--- Test Inverse (Matrice OK) ---")
response = requests.post(url, json=payload_ok)
print(f"Statut : {response.status_code}")
print(f"Résultat : {response.json()}\n")

# Test 2 : Matrice non inversible (déterminant = 0)
payload_zero = {"A": [[2, 4], [1, 2]]}
print("--- Test Inverse (Déterminant Nul) ---")
response_zero = requests.post(url, json=payload_zero)
print(f"Statut (Attendu 400) : {response_zero.status_code}")
print(f"Erreur : {response_zero.json()}")