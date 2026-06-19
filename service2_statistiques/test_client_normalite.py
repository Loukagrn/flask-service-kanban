import requests
import json

# adresse de la route effectuant le test de normalite de shapiro-wilk
url_route = "http://127.0.0.1:5002/stats/normalite"

# echantillon de valeurs transmis pour l'analyse de distribution
donnees_envoi = {"data": [5, 5, 5]}

print("execution du test pour la route normalite...")

# envoi de la requete post vers l'url du test statistique
reponse_serveur = requests.post(url_route, json=donnees_envoi)

# conversion de la reponse brute en dictionnaire exploitable
resultat_json = reponse_serveur.json()

# creation du rapport au format json standard pour l'historique
with open("resultat_normalite.json", "w", encoding="utf-8") as fichier_json:
    json.dump(resultat_json, fichier_json, indent=4, ensure_ascii=False)

# generation de la structure html pour le rendu visuel du test
contenu_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>rapport de test - normalite</title>
</head>
<body style="font-family: sans-serif; margin: 30px; background-color: #fafafa;">
    <div style="background: white; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
        <h2>test de la route : /stats/normalite</h2>
        <p>code de statut http : <strong>{reponse_serveur.status_code}</strong></p>
        
        <h3>donnees envoyees par le client :</h3>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px;">{json.dumps(donnees_envoi)}</pre>
        
        <h3>reponse de l'api :</h3>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 3px;">{json.dumps(resultat_json, indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>"""

# ecriture du fichier html final
with open("resultat_normalite.html", "w", encoding="utf-8") as fichier_html:
    fichier_html.write(contenu_html)

print("fichiers de rapport normalite generes avec succes.")