"""Modèles persistants (tables) de l'application."""
from datetime import datetime

from pydantic import NaiveDatetime
from sqlmodel import Field, SQLModel, UniqueConstraint


<<<<<<< HEAD
=======
class Utilisateur(SQLModel, table=True):
    """Un organisateur d'événements (séance 4)."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=120)
    nom: str = Field(max_length=80)
    mot_de_passe_hash: str


>>>>>>> be0ad84 (seance 4: securite)
class Evenement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titre: str = Field(max_length=120)
    description: str = Field(default="", max_length=2000)
    lieu: str = Field(max_length=120)
    # Heure locale (Douala), sans fuseau : choix assumé pour ce cours.
    # Une application multi-pays stockerait plutôt des dates UTC.
    debut: NaiveDatetime = Field(index=True)
    capacite: int
<<<<<<< HEAD
=======
    organisateur_id: int | None = Field(default=None, foreign_key="utilisateur.id")
>>>>>>> be0ad84 (seance 4: securite)


class Inscription(SQLModel, table=True):
    # Une même adresse ne peut s'inscrire qu'une fois au même événement :
    # la règle est garantie par la base, pas seulement par le code Python.
    __table_args__ = (UniqueConstraint("evenement_id", "email"),)

    id: int | None = Field(default=None, primary_key=True)
    evenement_id: int = Field(foreign_key="evenement.id", index=True)
    nom: str = Field(max_length=80)
    email: str = Field(max_length=120)
    cree_le: NaiveDatetime = Field(default_factory=datetime.now)
