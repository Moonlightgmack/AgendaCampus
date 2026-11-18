"""Schémas d'échange : ce qui entre dans l'application et ce qui en sort.

Pydantic vérifie automatiquement chaque donnée reçue (type, longueur,
bornes). Le client n'envoie jamais l'identifiant : c'est le serveur qui
l'attribue, d'où deux schémas distincts pour la création et la lecture.
"""
from pydantic import BaseModel, Field, NaiveDatetime

MOTIF_EMAIL = r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"


class EvenementCreation(BaseModel):
    titre: str = Field(min_length=3, max_length=120)
    description: str = Field(default="", max_length=2000)
    lieu: str = Field(min_length=2, max_length=120)
    debut: NaiveDatetime
    capacite: int = Field(ge=1, le=1000)


class EvenementLecture(EvenementCreation):
    id: int
    places_restantes: int


class InscriptionCreation(BaseModel):
    nom: str = Field(min_length=2, max_length=80)
    email: str = Field(pattern=MOTIF_EMAIL, max_length=120)


class InscriptionLecture(InscriptionCreation):
    id: int
    evenement_id: int
    places_restantes: int
