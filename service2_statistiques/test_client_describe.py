import requests
import json

# adresse locale de la route des statistiques descriptives
url_route = "http://127.0.0.1:5002/stats/describe"

# donnees du tableau a tester transmises dans la requete
donnees_envoi = {"data": [10, 20, 30, 40]}

print("execution du test pour la route describe...")

# envoi de la requete post au serveur avec les donnees json
reponse_serveur = requests.post(url_route, json=donnees_envoi)

# recuperation du dictionnaire json renvoye par le serveur flask
resultat_json = reponse_serveur.json()

# sauvegarde de la reponse brute dans un fichier json de resultat
with open("resultat_describe.json", "w", encoding="utf-8") as fichier_json:
    json.dump(resultat_json, fichier_json, indent=4, ensure_ascii=False)

# construction de la page html pour afficher le rendu graphique du test
contenu_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>rapport de test - describe</title>
</head>
<body style="font-family: sans-serif; margin: 30px; background-color: #fafafa;">
    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2>test de la route : /stats/describe</h2>
        <p>code de statut http : <strong>{reponse_serveur.status_code}</strong></p>
        
        <h3>donnees envoyees par le client :</h3>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px;">{json.dumps(donnees_envoi)}</pre>
        
        <h3>reponse de l'api :</h3>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px;">{json.dumps(resultat_json, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>"""

# ecriture du fichier html sur le disque pour consultation
with open("resultat_describe.html", "w", encoding="utf-8") as fichier_html:
    fichier_html.write(contenu_html)

print("fichiers de rapport describe generes avec succes.")