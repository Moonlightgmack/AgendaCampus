"""Accès à la base de données : moteur SQLModel et session par requête."""
from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL

# check_same_thread=False : SQLite refuse par défaut qu'une connexion soit
# utilisée par un autre thread que celui qui l'a créée ; FastAPI, lui,
# peut traiter une requête sur un thread différent.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
<<<<<<< HEAD
engine = create_engine(DATABASE_URL, connect_args=connect_args)
=======
engine = create_engine(DATABASE_URL, connect_args=connect_args,echo=False)
>>>>>>> be0ad84 (seance 4: securite)


def creer_tables() -> None:
    """Crée les tables manquantes (suffisant pour ce cours ; en production,
    on utiliserait un outil de migration comme Alembic)."""
    from app import models  # noqa: F401  (enregistre les modèles)

    SQLModel.metadata.create_all(engine)


def get_session():
    """Dépendance FastAPI : une session par requête, fermée automatiquement."""
    with Session(engine) as session:
        yield session
