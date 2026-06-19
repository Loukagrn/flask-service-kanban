
# Service 4 — Chargement CSV vers MySQL

## Description

Le Service 4 permet d'importer des données depuis un fichier CSV vers une base de données MySQL. Les données chargées sont ensuite utilisées par le Service 3 pour réaliser des calculs statistiques.

Technologies utilisées :

* Flask
* Pandas
* MySQL Connector Python
* Python Dotenv
* MySQL

---

## Installation

### 1. Créer l'environnement virtuel

```bash
python -m venv venv
```

### 2. Activer l'environnement

Sous Windows :

```bash
venv\Scripts\activate
```

Sous Linux/Mac :

```bash
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## Configuration

Créer un fichier `.env` :

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=mot_de_passe
DB_NAME=flask_stats
```

⚠️ Ne jamais envoyer le fichier `.env` sur GitHub.

Ajouter dans `.gitignore` :

```text
.env
venv/
```

---

## Structure du projet

```text
service4_csv_mysql/
│
├── app.py
├── requirements.txt
├── test_client.html
├── .env
│
└── data/
    ├── donnees_exemple.csv
    └── mauvais.csv
```

---

## Lancement du service

```bash
python app.py
```

Le serveur démarre sur :

```text
http://localhost:5004
```

---

## Routes disponibles

### POST /upload/csv

Permet de charger un fichier CSV dans la table MySQL `donnees`.

Exemple avec curl :

```bash
curl -X POST http://localhost:5004/upload/csv \
     -F "file=@data/donnees_exemple.csv"
```

Réponse :

```json
{
  "statut": "success",
  "lignes_inserees": 22,
  "lignes_invalides_ignorees": 0,
  "message": "22 ligne(s) chargée(s) dans la table donnees"
}
```

---

### GET /upload/series

Retourne la liste des séries disponibles dans la base de données.

Exemple :

```bash
curl http://localhost:5004/upload/series
```

Réponse :

```json
{
  "series": [
    {
      "serie": "serie_A",
      "n_points": 8
    }
  ],
  "total": 3
}
```

---

## Interface de test

Une interface HTML de test est disponible :

```text
test_client.html
```

Elle permet :

* d'envoyer un fichier CSV ;
* d'afficher la réponse JSON ;
* de consulter les séries enregistrées.

---

# Questions de vérification

## Q1. Quels contrôles de validation effectuez-vous avant d'insérer les données dans MySQL ?

Les contrôles effectués sont :

* présence du fichier ;
* nom du fichier non vide ;
* extension `.csv` ;
* taille maximale de 5 Mo ;
* lecture correcte du CSV ;
* présence des colonnes obligatoires (`nom_serie`, `valeur`) ;
* conversion de `valeur` en nombre ;
* suppression des lignes invalides ;
* vérification qu'il reste au moins une ligne valide.

---

## Q2. Que se passe-t-il si le CSV contient des valeurs non numériques dans la colonne « valeur » ?

Les valeurs non numériques sont converties en `NaN` grâce à :

```python
pd.to_numeric(df['valeur'], errors='coerce')
```

Les lignes concernées sont supprimées avant l'insertion dans MySQL.

Le nombre de lignes rejetées est indiqué dans :

```json
{
  "lignes_invalides_ignorees": 1
}
```

---

## Q3. Comment avez-vous coordonné le schéma MySQL avec l'Étudiant C (Service 3) ?

Le Service 3 et le Service 4 utilisent la même table MySQL :

```sql
donnees
```

avec les colonnes :

* nom_serie
* valeur
* categorie
* date_mesure

Cette coordination permet au Service 3 d'utiliser directement les données importées par le Service 4.

---

## Q4. Testez l'envoi d'un CSV avec une colonne « valeur » manquante. Quelle réponse obtenez-vous ?

Fichier utilisé :

```csv
nom_serie,categorie
serie_X,test
```

Réponse obtenue :

```json
{
  "erreur": "Colonnes obligatoires manquantes",
  "manquantes": ["valeur"]
}
```

Code HTTP :

```text
400 Bad Request
```

---

## Q5. Après avoir chargé donnees_exemple.csv, utilisez le Service 3 pour calculer la description de serie_C. Quel est le résultat ?

Route utilisée :

```text
GET /db/stats/describe?serie=serie_C
```

Résultat :

```json
{
  "source": "mysql",
  "resultat": {
    "serie": "serie_C",
    "n": 6,
    "moyenne": 223.15,
    "mediane": 224.45,
    "ecart_type": 17.52,
    "minimum": 198.2,
    "maximum": 245.1
  }
}
```

Cette réponse montre que les données importées par le Service 4 sont correctement exploitées par le Service 3.

