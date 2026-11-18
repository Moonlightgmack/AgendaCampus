"""Données de démonstration, insérées au premier démarrage si la base est vide."""
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.database import engine
from app.models import Evenement


def inserer_donnees_demo() -> None:
    with Session(engine) as session:
        if session.exec(select(Evenement)).first() is not None:
            return
        aujourdhui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        session.add_all([
            Evenement(
                titre="Atelier Git pour débutants",
                description="Versionner son code, créer un dépôt, faire ses premiers commits.",
                lieu="LAB1",
                debut=aujourdhui + timedelta(days=2, hours=14),
                capacite=25,
            ),
            Evenement(
                titre="Conférence : le métier de développeur web",
                description="Échanges avec d'anciens étudiants de la faculté.",
                lieu="Amphithéâtre principal",
                debut=aujourdhui + timedelta(days=5, hours=10),
                capacite=120,
            ),
            Evenement(
                titre="Tournoi de football inter-facultés",
                description="Inscription individuelle ; les équipes seront formées sur place.",
                lieu="Stade du campus",
                debut=aujourdhui + timedelta(days=9, hours=15, minutes=30),
                capacite=44,
            ),
        ])
        session.commit()
