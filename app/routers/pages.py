"""Pages HTML rendues côté serveur (Jinja2).

Les pages utilisent la même couche métier (services) que l'API JSON :
deux « présentations » différentes, une seule logique.
"""
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from app import services
from app.schemas import EvenementCreation, InscriptionCreation
from app.templating import templates
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session

router = APIRouter(include_in_schema=False)


MESSAGES = {
    "missing": "Ce champ est obligatoire.",
    "string_too_short": "Au moins {min_length} caractères.",
    "string_too_long": "Au plus {max_length} caractères.",
    "greater_than_equal": "La valeur doit être supérieure ou égale à {ge}.",
    "less_than_equal": "La valeur doit être inférieure ou égale à {le}.",
    "int_parsing": "Un nombre entier est attendu.",
    "datetime_parsing": "Date et heure invalides.",
    "datetime_from_date_parsing": "Date et heure invalides.",
    "string_pattern_mismatch": "Format invalide.",
}


def erreurs_lisibles(exc: ValidationError) -> dict[str, str]:
    """Transforme les erreurs Pydantic en {champ: message en français} pour le gabarit."""
    erreurs = {}
    for e in exc.errors():
        modele = MESSAGES.get(e["type"], e["msg"])
        erreurs[str(e["loc"][0])] = modele.format(**e.get("ctx", {}))
    return erreurs


@router.get("/")
def accueil(
    request: Request,
    q: str | None = None, session: Session = Depends(get_session)
):
    evenements = services.lister_evenements(session,q,True)
    places = {e.id: services.places_restantes(session,e) for e in evenements}
    return templates.TemplateResponse(
        request, "index.html",
        {"evenements": evenements, "places": places, "q": q or ""},
    )


@router.get("/evenements/nouveau")
def formulaire_creation(request: Request):
    return templates.TemplateResponse(
        request, "evenement_form.html", {"valeurs": {}, "erreurs": {}}
    )


@router.post("/evenements/nouveau")
def creer_evenement(
    request: Request,
    titre: str = Form(""),
    description: str = Form(""),
    lieu: str = Form(""),
    debut: str = Form(""),
    capacite: str = Form(""),
    session: Session = Depends(get_session)
):
    valeurs = {"titre": titre, "description": description, "lieu": lieu, "debut": debut, "capacite": capacite}
    try:
        donnees = EvenementCreation(**valeurs)
    except ValidationError as exc:
        # On ré-affiche le formulaire AVEC les valeurs saisies et les erreurs : 422.
        return templates.TemplateResponse(
            request, "evenement_form.html",
            {"valeurs": valeurs, "erreurs": erreurs_lisibles(exc)},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )
    evenement = services.creer_evenement(donnees)
    # Post/Redirect/Get : après un POST réussi, on redirige (303) vers une page GET.
    return RedirectResponse(f"/evenements/{evenement.id}?message=cree", status.HTTP_303_SEE_OTHER)


@router.get("/evenements/{evenement_id}")
def detail_evenement(
    request: Request,
    evenement_id: int,
    message: str | None = None,
    session: Session = Depends(get_session)
):
    try:
        evenement = services.obtenir_evenement(session,evenement_id)
    except services.EvenementIntrouvable:
        return templates.TemplateResponse(
            request, "404.html", {}, status_code=status.HTTP_404_NOT_FOUND
        )
    return templates.TemplateResponse(
        request, "evenement.html",
        {
            "evenement": evenement,
            "places": services.places_restantes(session,evenement),
            "message": message,
            "erreurs": {},
            "valeurs": {},
        },
    )


@router.post("/evenements/{evenement_id}/inscription")
def inscription_formulaire(
    request: Request,
    evenement_id: int,
    nom: str = Form(""),
    email: str = Form(""),
    session: Session = Depends(get_session)
):
    valeurs = {"nom": nom, "email": email}
    erreurs: dict[str, str] = {}
    try:
        services.inscrire(session,evenement_id, InscriptionCreation(**valeurs))
        return RedirectResponse(f"/evenements/{evenement_id}?message=inscrit", status.HTTP_303_SEE_OTHER)
    except services.EvenementIntrouvable:
        return templates.TemplateResponse(
            request, "404.html", {}, status_code=status.HTTP_404_NOT_FOUND
        )
    except ValidationError as exc:
        erreurs, code = erreurs_lisibles(exc), status.HTTP_422_UNPROCESSABLE_CONTENT
    except services.EvenementComplet:
        erreurs, code = {"general": "Désolé, cet événement est complet."}, status.HTTP_409_CONFLICT
    except services.DejaInscrit:
        erreurs, code = {"email": "Cette adresse est déjà inscrite à cet événement."}, status.HTTP_409_CONFLICT
    evenement = services.obtenir_evenement(session,evenement_id)
    return templates.TemplateResponse(
        request, "evenement.html",
        {
            "evenement": evenement,
            "places": services.places_restantes(session,evenement),
            "message": None,
            "erreurs": erreurs,
            "valeurs": valeurs,
        },
        status_code=code,
    )

