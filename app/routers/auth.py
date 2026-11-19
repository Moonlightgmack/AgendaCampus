"""Création de compte, connexion et déconnexion des organisateurs (séance 4)."""
import re

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models import Utilisateur
from app.schemas import MOTIF_EMAIL
from app.securite import authentifier, hacher_mot_de_passe
from app.templating import templates

router = APIRouter(include_in_schema=False)


def chemin_sur(suivant: str | None) -> str:
    # Évite la « redirection ouverte » : on n'accepte qu'un chemin interne.
    if suivant and suivant.startswith("/") and not suivant.startswith("//"):
        return suivant
    return "/"


@router.get("/compte/creer")
def formulaire_compte(request: Request):
    return templates.TemplateResponse(request, "compte_form.html", {"valeurs": {}, "erreurs": {}})


@router.post("/compte/creer")
def creer_compte(
    request: Request,
    nom: str = Form(""),
    email: str = Form(""),
    mot_de_passe: str = Form(""),
    session: Session = Depends(get_session),
):
    email = email.strip().lower()
    erreurs: dict[str, str] = {}
    if len(nom.strip()) < 2:
        erreurs["nom"] = "Le nom doit contenir au moins 2 caractères."
    if not re.match(MOTIF_EMAIL, email):
        erreurs["email"] = "Adresse e-mail invalide."
    elif session.exec(select(Utilisateur).where(Utilisateur.email == email)).first():
        erreurs["email"] = "Un compte existe déjà avec cette adresse."
    if len(mot_de_passe) < 8:
        erreurs["mot_de_passe"] = "Le mot de passe doit contenir au moins 8 caractères."
    if erreurs:
        return templates.TemplateResponse(
            request, "compte_form.html",
            {"valeurs": {"nom": nom, "email": email}, "erreurs": erreurs},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    utilisateur = Utilisateur(nom=nom.strip(), email=email, mot_de_passe_hash=hacher_mot_de_passe(mot_de_passe))
    session.add(utilisateur)
    session.commit()
    session.refresh(utilisateur)
    request.session["utilisateur_id"] = utilisateur.id
    return RedirectResponse("/", status.HTTP_303_SEE_OTHER)


@router.get("/connexion")
def formulaire_connexion(request: Request, suivant: str | None = None):
    return templates.TemplateResponse(request, "connexion.html", {"erreur": None, "email": "", "suivant": suivant or ""})


@router.post("/connexion")
def connexion(
    request: Request,
    email: str = Form(""),
    mot_de_passe: str = Form(""),
    suivant: str = Form(""),
    session: Session = Depends(get_session),
):
    utilisateur = authentifier(session, email.strip(), mot_de_passe)
    if utilisateur is None:
        # Message volontairement vague : on ne révèle pas si l'adresse existe.
        return templates.TemplateResponse(
            request, "connexion.html",
            {"erreur": "Identifiants incorrects.", "email": email, "suivant": suivant},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    request.session["utilisateur_id"] = utilisateur.id
    return RedirectResponse(chemin_sur(suivant), status.HTTP_303_SEE_OTHER)


@router.post("/deconnexion")
def deconnexion(request: Request):
    request.session.clear()
    return RedirectResponse("/", status.HTTP_303_SEE_OTHER)
