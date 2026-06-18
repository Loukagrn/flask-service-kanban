# Service 3 — Statistiques depuis MySQL

API REST Flask qui calcule des statistiques sur des séries stockées en base MySQL.

## Installation

```bash
cd service3_stats_mysql
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crée un fichier `.env` avec tes identifiants MySQL :

DB_HOST=localhost

DB_PORT=3306

DB_USER=root

DB_PASSWORD=1234

DB_NAME=flask_stats

## Lancement

```bash
python app.py
```
Le service écoute sur http://localhost:5003

## Routes

### GET /db/stats/describe?serie=NOM
Retourne les statistiques descriptives d'une série.

Exemple :
```bash
curl "http://localhost:5003/db/stats/describe?serie=serie_A"
```

### GET /db/stats/correlation?serie_x=NOM_X&serie_y=NOM_Y
Retourne le coefficient de corrélation de Pearson entre deux séries.

Exemple :
```bash
curl "http://localhost:5003/db/stats/correlation?serie_x=serie_A&serie_y=serie_B"
```

### GET /db/series
Liste toutes les séries disponibles dans la BDD.

### GET /health
Vérifie que le service est opérationnel.

## Codes HTTP
- 200 — Succès
- 400 — Paramètre manquant
- 404 — Série introuvable
- 500 — Erreur base de données.