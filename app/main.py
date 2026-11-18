"""Point d'entrée de l'application AgendaCampus.

Lancement (depuis le dossier agendacampus) :
    uvicorn app.main:app --reload
puis ouvrir http://127.0.0.1:8000 (pages) et http://127.0.0.1:8000/docs (API).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.docs_hors_ligne import activer_docs_hors_ligne
from app.config import NOM_APPLICATION
from app.demo import inserer_donnees_demo
from app.routers import api, pages
from app.database import creer_tables


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
    creer_tables()
    # Exécuté une fois au démarrage du serveur
    inserer_donnees_demo()
    yield


app = FastAPI(title=f"API {NOM_APPLICATION}", version="1.0", lifespan=cycle_de_vie)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
activer_docs_hors_ligne(app)   # /docs fonctionne sans Internet
app.include_router(api.router)
app.include_router(pages.router)
