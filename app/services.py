"""Couche métier : les règles de l'application, indépendantes de HTTP.

Les routeurs (pages HTML comme API JSON) appellent ces fonctions ; ils ne
parlent jamais directement à la base. Les erreurs métier sont des
exceptions Python, que chaque routeur traduit à sa façon (code HTTP pour
l'API, message affiché pour les pages).
"""
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, col, func, or_, select

from app.models import Evenement, Inscription
from app.schemas import EvenementCreation, InscriptionCreation


class EvenementIntrouvable(Exception):
    pass


class EvenementComplet(Exception):
    pass


class DejaInscrit(Exception):
    pass


def nombre_inscrits(session: Session, evenement_id: int) -> int:
    requete = select(func.count()).select_from(Inscription).where(
        Inscription.evenement_id == evenement_id
    )
    return session.exec(requete).one()


def places_restantes(session: Session, evenement: Evenement) -> int:
    return evenement.capacite - nombre_inscrits(session, evenement.id)


def lister_evenements(session: Session, q: str | None = None, a_venir: bool = True) -> list[Evenement]:
    requete = select(Evenement)
    if a_venir:
        requete = requete.where(Evenement.debut >= datetime.now())
    if q:
        motif = f"%{q}%"
        # Requête paramétrée : la saisie de l'utilisateur n'est jamais
        # concaténée dans le SQL (protection contre l'injection SQL).
        requete = requete.where(or_(col(Evenement.titre).ilike(motif), col(Evenement.lieu).ilike(motif)))
    return list(session.exec(requete.order_by(Evenement.debut)).all())


def obtenir_evenement(session: Session, evenement_id: int) -> Evenement:
    evenement = session.get(Evenement, evenement_id)
    if evenement is None:
        raise EvenementIntrouvable(evenement_id)
    return evenement


def creer_evenement(session: Session, donnees: EvenementCreation) -> Evenement:
    evenement = Evenement(**donnees.model_dump())
    session.add(evenement)
    session.commit()
    session.refresh(evenement)
    return evenement


def modifier_evenement(session: Session, evenement_id: int, donnees: EvenementCreation) -> Evenement:
    evenement = obtenir_evenement(session, evenement_id)
    for champ, valeur in donnees.model_dump().items():
        setattr(evenement, champ, valeur)
    session.add(evenement)
    session.commit()
    session.refresh(evenement)
    return evenement


def supprimer_evenement(session: Session, evenement_id: int) -> None:
    evenement = obtenir_evenement(session, evenement_id)
    for inscription in session.exec(select(Inscription).where(Inscription.evenement_id == evenement_id)):
        session.delete(inscription)
    session.delete(evenement)
    session.commit()


def inscrire(session: Session, evenement_id: int, donnees: InscriptionCreation) -> Inscription:
    evenement = obtenir_evenement(session, evenement_id)
    if places_restantes(session, evenement) <= 0:
        raise EvenementComplet(evenement_id)
    # TODO (partie C) :
    #   1. créer l'objet Inscription (adresse e-mail en minuscules)
    #   2. l'ajouter à la session et valider (commit)
    #   3. si la base refuse l'écriture (IntegrityError : contrainte d'unicité),
    #      annuler (rollback) et lever DejaInscrit
    #   4. rafraîchir l'objet (refresh) et le renvoyer
    inscription = Inscription(evenement_id=evenement_id, nom=donnees.nom, 
     email=donnees.email.lower())
    session.add(inscription)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise DejaInscrit(donnees.email)
    session.refresh(inscription)

    return inscription
    raise NotImplementedError
