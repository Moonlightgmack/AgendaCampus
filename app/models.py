"""Modèles persistants (tables) de l'application."""
from datetime import datetime

from pydantic import NaiveDatetime
from sqlmodel import Field, SQLModel, UniqueConstraint


class Evenement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    titre: str = Field(max_length=120)
    description: str = Field(default="", max_length=2000)
    lieu: str = Field(max_length=120)
    # Heure locale (Douala), sans fuseau : choix assumé pour ce cours.
    # Une application multi-pays stockerait plutôt des dates UTC.
    debut: NaiveDatetime = Field(index=True)
    capacite: int


class Inscription(SQLModel, table=True):
    # Une même adresse ne peut s'inscrire qu'une fois au même événement :
    # la règle est garantie par la base, pas seulement par le code Python.
    __table_args__ = (UniqueConstraint("evenement_id", "email"),)

    id: int | None = Field(default=None, primary_key=True)
    evenement_id: int = Field(foreign_key="evenement.id", index=True)
    nom: str = Field(max_length=80)
    email: str = Field(max_length=120)
    cree_le: NaiveDatetime = Field(default_factory=datetime.now)
