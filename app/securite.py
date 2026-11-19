"""Authentification des organisateurs (séance 4).

- Les mots de passe ne sont JAMAIS stockés en clair : on stocke un hachage
  lent et salé (PBKDF2-SHA256, fourni par la bibliothèque standard).
- L'utilisateur connecté est mémorisé dans un cookie de session signé
  (SessionMiddleware) : le client peut le lire, mais pas le falsifier.
"""
import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Utilisateur

ITERATIONS = 600_000


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    sel = secrets.token_hex(16)
    empreinte = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode(), bytes.fromhex(sel), ITERATIONS)
    return f"pbkdf2_sha256${ITERATIONS}${sel}${empreinte.hex()}"


def verifier_mot_de_passe(mot_de_passe: str, hachage: str) -> bool:
    """Vérifie un mot de passe saisi contre le hachage enregistré.

    TODO (partie B) :
      1. découper le hachage en ses 4 parties (séparateur « $ ») ;
         si le format est invalide, renvoyer False
      2. recalculer l'empreinte du mot de passe saisi avec le MÊME sel et le
         MÊME nombre d'itérations
      3. comparer avec hmac.compare_digest() (et non avec ==)
    """

    _, iterations, sel, attendu = hachage.split("$")
    calcule = hashlib.pbkdf2_hmac("sha256", mot_de_passe.encode(), bytes.fromhex(sel), int(iterations))
    return hmac.compare_digest(calcule.hex(), attendu)
    raise NotImplementedError


def authentifier(session: Session, email: str, mot_de_passe: str) -> Utilisateur | None:
    utilisateur = session.exec(select(Utilisateur).where(Utilisateur.email == email.lower())).first()
    if utilisateur and verifier_mot_de_passe(mot_de_passe, utilisateur.mot_de_passe_hash):
        return utilisateur
    return None


def utilisateur_optionnel(request: Request, session: Session = Depends(get_session)) -> Utilisateur | None:
    utilisateur_id = request.session.get("utilisateur_id")
    if utilisateur_id is None:
        return None
    return session.get(Utilisateur, utilisateur_id)


def utilisateur_requis(utilisateur: Utilisateur | None = Depends(utilisateur_optionnel)) -> Utilisateur:
    """Pour l'API : 401 si personne n'est connecté."""
    if utilisateur is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authentification requise")
    return utilisateur
