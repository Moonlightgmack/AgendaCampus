"""Configuration de l'application, lue dans les variables d'environnement.

Principe : le code ne change pas d'un environnement à l'autre (poste de
l'étudiant, conteneur Docker, serveur) ; seule la configuration change.
"""
import os

# Base de données : SQLite par défaut (aucune installation nécessaire),
# PostgreSQL quand on lance l'application avec docker compose.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agendacampus.db")

<<<<<<< HEAD
=======
# Clé utilisée pour signer le cookie de session (séance 4).
# En production, elle DOIT être fournie par l'environnement.
SECRET_KEY = os.getenv("SECRET_KEY", "cle-de-developpement-a-changer")

>>>>>>> be0ad84 (seance 4: securite)
NOM_APPLICATION = "AgendaCampus"
