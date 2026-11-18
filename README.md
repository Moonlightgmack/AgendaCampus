# AgendaCampus, état à la fin de la séance 2

Application web de gestion des événements du campus, construite pas à pas
pendant le cours **Conception Web 1** (Licence 3 Informatique, Université
Adventiste Cosendai).

Couche métier (en mémoire), API REST JSON documentée, formulaires HTML
validés côté serveur. Les données sont perdues à chaque redémarrage.

## Lancer l'application SANS Docker (chemin par défaut)

Prérequis : Python 3.10 ou plus récent (3.11 à 3.14 pour l'installation hors ligne).

```bash
# 1. Se placer dans le dossier du projet
cd agendacampus

# 2. Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate            # Windows (PowerShell ou cmd)
source .venv/bin/activate           # Linux / macOS

# 3. Installer les dépendances, sans Internet, avec le dossier wheelhouse fourni par l'enseignant
pip install --no-index --find-links=../wheelhouse -r requirements.txt
#    avec une connexion Internet, ceci suffit :
pip install -r requirements.txt

# 4. Démarrer le serveur (rechargement automatique à chaque modification)
uvicorn app.main:app --reload
```

Ouvrir ensuite http://127.0.0.1:8000
et la documentation interactive de l'API sur http://127.0.0.1:8000/docs
(elle fonctionne sans Internet : son interface est servie depuis app/static/docs)

## Lancer l'application AVEC Docker (option)

Prérequis : Docker Desktop (Windows/macOS) ou Docker Engine (Linux).

```bash
cd agendacampus
docker compose up --build
```

Ouvrir http://localhost:8000. Arrêt : `Ctrl+C`, puis `docker compose down`.

Les deux chemins font tourner **le même code** : seule la façon de
l'exécuter change.
