import requests
url = 'http://localhost:5001/matrices/transpose'
payload = {"A": [[1, 2], [3, 4]]}
response = requests.post(url, json=payload)
print(f"Statut : {response.status_code}, Résultat : {response.json()}")