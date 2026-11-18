"""Configuration de l'application, lue dans les variables d'environnement.

Principe : le code ne change pas d'un environnement à l'autre (poste de
l'étudiant, conteneur Docker, serveur) ; seule la configuration change.
"""
import os

# Base de données : SQLite par défaut (aucune installation nécessaire),
# PostgreSQL quand on lance l'application avec docker compose.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agendacampus.db")

NOM_APPLICATION = "AgendaCampus"
