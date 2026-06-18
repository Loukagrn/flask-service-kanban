import requests

url = 'http://localhost:5001/matrices/multiply'
# Test avec deux matrices 3x3 pour valider la Q5 du TP
payload = {
    "A": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    "B": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
}

print("Envoi de la requête de multiplication...")
response = requests.post(url, json=payload)
print(f"Statut HTTP : {response.status_code}")
print(f"Résultat JSON : {response.json()}")