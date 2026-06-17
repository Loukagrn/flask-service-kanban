import requests

url = 'http://localhost:5001/matrices/add'
payload = {
    "A": [[1, 2], [3, 4]],
    "B": [[5, 6], [7, 8]]
}

print("Envoi de la requête au serveur...")
response = requests.post(url, json=payload)

print(f"Statut HTTP : {response.status_code}")
print(f"Résultat JSON : {response.json()}")