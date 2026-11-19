"""Tests automatisés de l'API (séance 4).

Lancement depuis le dossier agendacampus :   python -m pytest -v
Chaque test utilise une base SQLite EN MÉMOIRE, neuve et vide :
les tests ne touchent jamais à votre base de développement.
"""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app

DEMAIN = (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat()


@pytest.fixture
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def session_de_test():
        with Session(engine) as session:
            yield session

    # On remplace la dépendance get_session par notre base de test
    app.dependency_overrides[get_session] = session_de_test
    # TestClient sans « with » : le cycle de vie (création des tables de
    # développement, données de démo) n'est pas déclenché.
    yield TestClient(app)
    app.dependency_overrides.clear()


def connecter(client: TestClient, email: str = "orga@uac.cm") -> None:
    client.post("/compte/creer", data={"nom": "Orga", "email": email, "mot_de_passe": "motdepasse123"})


def creer_evenement(client: TestClient, capacite: int = 2) -> dict:
    reponse = client.post("/api/evenements", json={
        "titre": "Atelier Git", "lieu": "LAB1", "debut": DEMAIN, "capacite": capacite,
    })
    assert reponse.status_code == 201
    return reponse.json()


def test_sante(client):
    assert client.get("/api/sante").json() == {"statut": "ok"}


def test_creation_sans_connexion_refusee(client):
    reponse = client.post("/api/evenements", json={"titre": "X" * 5, "lieu": "LAB1", "debut": DEMAIN, "capacite": 3})
    assert reponse.status_code == 401


def test_creation_puis_lecture(client):
    connecter(client)
    reponse = client.post("/api/evenements", json={"titre": "Atelier Git", "lieu": "LAB1", "debut": DEMAIN, "capacite": 2})
    assert reponse.status_code == 201
    assert reponse.headers["Location"] == f"/api/evenements/{reponse.json()['id']}"
    lu = client.get(reponse.headers["Location"])
    assert lu.status_code == 200
    assert lu.json()["places_restantes"] == 2


def test_validation_422(client):
    connecter(client)
    reponse = client.post("/api/evenements", json={"titre": "A", "lieu": "LAB1", "debut": DEMAIN, "capacite": 0})
    assert reponse.status_code == 422


def test_evenement_inexistant_404(client):
    assert client.get("/api/evenements/9999").status_code == 404


def test_inscription_et_capacite(client):
    connecter(client)
    e = creer_evenement(client, capacite=1)
    url = f"/api/evenements/{e['id']}/inscriptions"
    premier = client.post(url, json={"nom": "Awa", "email": "awa@uac.cm"})
    assert premier.status_code == 201
    assert premier.json()["places_restantes"] == 0
    second = client.post(url, json={"nom": "Paul", "email": "paul@uac.cm"})
    assert second.status_code == 409          # complet


def test_double_inscription_409(client):
    connecter(client)
    e = creer_evenement(client, capacite=5)
    url = f"/api/evenements/{e['id']}/inscriptions"
    assert client.post(url, json={"nom": "Awa", "email": "awa@uac.cm"}).status_code == 201
    assert client.post(url, json={"nom": "Awa", "email": "AWA@uac.cm"}).status_code == 409


def test_seul_l_organisateur_supprime(client):
    connecter(client, "a@uac.cm")
    e = creer_evenement(client)
    client.post("/deconnexion")
    connecter(client, "b@uac.cm")
    assert client.delete(f"/api/evenements/{e['id']}").status_code == 403
    client.post("/deconnexion")
    client.post("/connexion", data={"email": "a@uac.cm", "mot_de_passe": "motdepasse123"})
    assert client.delete(f"/api/evenements/{e['id']}").status_code == 204
    assert client.get(f"/api/evenements/{e['id']}").status_code == 404


def test_xss_echappe_dans_la_page(client):
    connecter(client)
    reponse = client.post("/api/evenements", json={
        "titre": "Soirée", "lieu": "LAB1", "debut": DEMAIN, "capacite": 3,
        "description": "<script>alert('pirate')</script>",
    })
    page = client.get(f"/evenements/{reponse.json()['id']}").text
    assert "<script>alert" not in page
    assert "&lt;script&gt;" in page


# TODO (partie F) : écrivez au moins deux tests supplémentaires, par exemple :
#   - un PUT sur un événement sans être connecté renvoie 401 ;
#   - une inscription avec une adresse e-mail mal formée renvoie 422.
