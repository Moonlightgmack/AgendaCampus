"""Point d'entrée de l'application AgendaCampus.

Lancement (depuis le dossier agendacampus) :
    uvicorn app.main:app --reload
puis ouvrir http://127.0.0.1:8000 (pages) et http://127.0.0.1:8000/docs (API).
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.docs_hors_ligne import activer_docs_hors_ligne
<<<<<<< HEAD
from app.config import NOM_APPLICATION
from app.demo import inserer_donnees_demo
from app.routers import api, pages
from app.database import creer_tables
=======
from app.config import NOM_APPLICATION,SECRET_KEY
from app.database import creer_tables
from app.demo import inserer_donnees_demo
from app.routers import api, pages,auth
from starlette.middleware.sessions import SessionMiddleware
>>>>>>> be0ad84 (seance 4: securite)


@asynccontextmanager
async def cycle_de_vie(app: FastAPI):
<<<<<<< HEAD
    creer_tables()
    # Exécuté une fois au démarrage du serveur
=======
    # Exécuté une fois au démarrage du serveur
    creer_tables()
>>>>>>> be0ad84 (seance 4: securite)
    inserer_donnees_demo()
    yield


<<<<<<< HEAD
=======

>>>>>>> be0ad84 (seance 4: securite)
app = FastAPI(title=f"API {NOM_APPLICATION}", version="1.0", lifespan=cycle_de_vie)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
activer_docs_hors_ligne(app)   # /docs fonctionne sans Internet
app.include_router(api.router)
<<<<<<< HEAD
=======
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, same_site="lax", 
https_only=False)
app.include_router(auth.router) 
>>>>>>> be0ad84 (seance 4: securite)
app.include_router(pages.router)
