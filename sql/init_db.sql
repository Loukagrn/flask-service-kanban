-- On crée la base de données si elle n'existe pas déjà
CREATE DATABASE IF NOT EXISTS flask_kanban;

-- On sélectionne cette base pour travailler dedans
USE flask_kanban;

-- On crée la table "donnees" si elle n'existe pas déjà
CREATE TABLE IF NOT EXISTS donnees (
    id          INT AUTO_INCREMENT PRIMARY KEY,  -- Numéro unique auto-généré pour chaque ligne
    nom_serie   VARCHAR(100) NOT NULL,           -- Nom de la série (obligatoire, max 100 caractères)
    valeur      FLOAT NOT NULL,                  -- Valeur numérique (obligatoire)
    categorie   VARCHAR(100),                    -- Catégorie (optionnelle)
    date_mesure DATE                             -- Date de la mesure (optionnelle)
);