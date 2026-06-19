import requests
import json

# adresse locale de la route de calcul de correlation de pearson
url_route = "http://127.0.0.1:5002/stats/correlation"

# deux listes de meme taille envoyees pour verifier la dependance lineaire
donnees_envoi = {"x": [1, 2, 3], "y": [2, 4, 6]}

print("execution du test pour la route correlation...")

# envoi du dictionnaire contenant les deux variables x et y
reponse_serveur = requests.post(url_route, json=donnees_envoi)

# extraction des donnees json calculees par scipy
resultat_json = reponse_serveur.json()

# creation du fichier json local contenant le resultat de la requete
with open("resultat_correlation.json", "w", encoding="utf-8") as fichier_json:
    json.dump(resultat_json, fichier_json, indent=4, ensure_ascii=False)

# generation de l'interface html pour presenter le resultat de la correlation
contenu_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>rapport de test - correlation</title>
</head>
<body style="font-family: sans-serif; margin: 30px; background-color: #fafafa;">
    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2>test de la route : /stats/correlation</h2>
        <p>code de statut http : <strong>{reponse_serveur.status_code}</strong></p>
        
        <h3>donnees envoyees par le client :</h3>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px;">{json.dumps(donnees_envoi)}</pre>
        
        <h3>reponse de l'api :</h3>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px;">{json.dumps(resultat_json, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>"""

# enregistrement de la page html de resultat
with open("resultat_correlation.html", "w", encoding="utf-8") as fichier_html:
    fichier_html.write(contenu_html)

print("fichiers de rapport correlation generes avec succes.")