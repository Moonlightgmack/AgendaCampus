"""API REST (JSON), niveau 2 du modèle de Richardson.

Ressources : /api/evenements et /api/evenements/{id}/inscriptions.
Chaque erreur métier devient un code HTTP explicite, jamais un 200 déguisé.
"""
<<<<<<< HEAD
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Response, status

from app import services
from app.schemas import EvenementCreation, EvenementLecture, InscriptionCreation, InscriptionLecture
from app.services import Evenement
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
=======
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app import services
from app.database import get_session
from app.models import Evenement, Utilisateur
from app.schemas import (
    EvenementCreation,
    EvenementLecture,
    InscriptionCreation,
    InscriptionLecture,
)
from app.securite import utilisateur_requis
>>>>>>> be0ad84 (seance 4: securite)

router = APIRouter(prefix="/api", tags=["API"])


<<<<<<< HEAD
def vers_lecture(evenement: Evenement,session: Session = Depends(get_session)) -> EvenementLecture:
    return EvenementLecture(**evenement.model_dump(), places_restantes=services.places_restantes(evenement))


def charger_ou_404(evenement_id: int,session: Session = Depends(get_session)) -> Evenement:
    try:
        return services.obtenir_evenement(evenement_id)
    except services.EvenementIntrouvable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Événement introuvable")

=======

def vers_lecture(session: Session, evenement: Evenement) -> EvenementLecture:
    return EvenementLecture(
        **evenement.model_dump(),
        places_restantes=services.places_restantes(session, evenement),
    )


def charger_ou_404(session: Session, evenement_id: int) -> Evenement:
    try:
        return services.obtenir_evenement(session, evenement_id)
    except services.EvenementIntrouvable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Événement introuvable")

def verifier_proprietaire(evenement: Evenement, utilisateur: Utilisateur) -> None:
    if evenement.organisateur_id != utilisateur.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Vous n'êtes pas l'organisateur de cet événement")
>>>>>>> be0ad84 (seance 4: securite)

@router.get("/sante")
def sante():
    return {"statut": "ok"}


@router.get("/evenements", response_model=list[EvenementLecture])
<<<<<<< HEAD
def lister(q: str | None = None, a_venir: bool = True,session: Session = Depends(get_session)):
    return [vers_lecture(e) for e in services.lister_evenements(q, a_venir)]


@router.get("/evenements/{evenement_id}", response_model=EvenementLecture)
def detail(evenement_id: int):
    return vers_lecture(charger_ou_404(evenement_id))


@router.post("/evenements", response_model=EvenementLecture, status_code=status.HTTP_201_CREATED)
def creer(donnees: EvenementCreation, response: Response,session: Session = Depends(get_session)):
    evenement = services.creer_evenement(donnees)
    response.headers["Location"] = f"/api/evenements/{evenement.id}"
    return vers_lecture(evenement)


@router.put("/evenements/{evenement_id}", response_model=EvenementLecture)
def modifier(evenement_id: int, donnees: EvenementCreation,session: Session = Depends(get_session)):
    charger_ou_404(evenement_id)
    return vers_lecture(services.modifier_evenement(evenement_id, donnees))


@router.delete("/evenements/{evenement_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(evenement_id: int,session: Session = Depends(get_session)):
    charger_ou_404(evenement_id)
    services.supprimer_evenement(evenement_id)
=======
def lister(q: str | None = None, a_venir: bool = True, session: Session = Depends(get_session)):
    return [vers_lecture(session, e) for e in services.lister_evenements(session, q, a_venir)]


@router.get("/evenements/{evenement_id}", response_model=EvenementLecture)
def detail(evenement_id: int, session: Session = Depends(get_session)):
    return vers_lecture(session, charger_ou_404(session, evenement_id))


@router.post("/evenements", response_model=EvenementLecture, status_code=status.HTTP_201_CREATED)
def creer(
    donnees: EvenementCreation,
    response: Response,
    session: Session = Depends(get_session),
    utilisateur: Utilisateur = Depends(utilisateur_requis)
):
    evenement = services.creer_evenement(session, donnees,organisateur_id=utilisateur.id)
    response.headers["Location"] = f"/api/evenements/{evenement.id}"
    return vers_lecture(session, evenement)


@router.put("/evenements/{evenement_id}", response_model=EvenementLecture)
def modifier(
    evenement_id: int,
    donnees: EvenementCreation,
    session: Session = Depends(get_session),
    utilisateur: Utilisateur = Depends(utilisateur_requis)
):
    charger_ou_404(session, evenement_id)
    return vers_lecture(session, services.modifier_evenement(session, evenement_id, donnees))


@router.delete("/evenements/{evenement_id}", status_code=status.HTTP_204_NO_CONTENT)
def supprimer(
    evenement_id: int,
    session: Session = Depends(get_session),
    utilisateur: Utilisateur = Depends(utilisateur_requis)
):
    evenement = charger_ou_404(session, evenement_id)

    verifier_proprietaire(evenement, utilisateur)

    services.supprimer_evenement(session, evenement_id)
>>>>>>> be0ad84 (seance 4: securite)


@router.post(
    "/evenements/{evenement_id}/inscriptions",
    response_model=InscriptionLecture,
    status_code=status.HTTP_201_CREATED,
)
<<<<<<< HEAD
def inscrire(evenement_id: int, donnees: InscriptionCreation,session: Session = Depends(get_session)):
    try:
        inscription = services.inscrire(evenement_id, donnees)
=======
def inscrire(evenement_id: int, donnees: InscriptionCreation, session: Session = Depends(get_session)):
    try:
        inscription = services.inscrire(session, evenement_id, donnees)
>>>>>>> be0ad84 (seance 4: securite)
    except services.EvenementIntrouvable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Événement introuvable")
    except services.EvenementComplet:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cet événement est complet")
    except services.DejaInscrit:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cette adresse est déjà inscrite")
<<<<<<< HEAD
    evenement = services.obtenir_evenement(evenement_id)
    return InscriptionLecture(
        id=inscription.id, evenement_id=evenement_id, nom=inscription.nom, email=inscription.email,
        places_restantes=services.places_restantes(evenement),
=======
    evenement = services.obtenir_evenement(session, evenement_id)
    return InscriptionLecture(
        **inscription.model_dump(include={"id", "evenement_id", "nom", "email"}),
        places_restantes=services.places_restantes(session, evenement),
>>>>>>> be0ad84 (seance 4: securite)
    )
