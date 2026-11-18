"""API REST (JSON), niveau 2 du modèle de Richardson.

Ressources : /api/evenements et /api/evenements/{id}/inscriptions.
Chaque erreur métier devient un code HTTP explicite, jamais un 200 déguisé.
"""
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Response, status

from app import services
from app.schemas import EvenementCreation, EvenementLecture, InscriptionCreation, InscriptionLecture
from app.services import Evenement
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session

router = APIRouter(prefix="/api", tags=["API"])


def vers_lecture(evenement: Evenement,session: Session = Depends(get_session)) -> EvenementLecture:
    return EvenementLecture(**evenement.model_dump(), places_restantes=services.places_restantes(evenement))


def charger_ou_404(evenement_id: int,session: Session = Depends(get_session)) -> Evenement:
    try:
        return services.obtenir_evenement(evenement_id)
    except services.EvenementIntrouvable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Événement introuvable")


@router.get("/sante")
def sante():
    return {"statut": "ok"}


@router.get("/evenements", response_model=list[EvenementLecture])
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


@router.post(
    "/evenements/{evenement_id}/inscriptions",
    response_model=InscriptionLecture,
    status_code=status.HTTP_201_CREATED,
)
def inscrire(evenement_id: int, donnees: InscriptionCreation,session: Session = Depends(get_session)):
    try:
        inscription = services.inscrire(evenement_id, donnees)
    except services.EvenementIntrouvable:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Événement introuvable")
    except services.EvenementComplet:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cet événement est complet")
    except services.DejaInscrit:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Cette adresse est déjà inscrite")
    evenement = services.obtenir_evenement(evenement_id)
    return InscriptionLecture(
        id=inscription.id, evenement_id=evenement_id, nom=inscription.nom, email=inscription.email,
        places_restantes=services.places_restantes(evenement),
    )
