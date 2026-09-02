"""Client pour l'API SMS MAPI (agregateur malgache, messaging.mapi.mg).

Ce module gere :
  - l'authentification par login/mot de passe -> token JWT, avec mise en
    cache en memoire du token entre les invocations d'une meme instance
    de Cloud Function (warm start) ;
  - le renouvellement automatique du token, y compris le cas d'un 401
    recu en cours de route (token expire entre deux appels malgre le
    cache) ;
  - le logout defensif avant chaque login : MAPI n'autorise qu'une seule
    session active a la fois par compte, un login direct echouerait donc
    si une session precedente (autre instance, cold start anterieur...)
    est encore ouverte ;
  - l'envoi d'un SMS unique personnalise via /api/msg/send et la
    consultation du solde via /api/smsoffer/available.

Aucune logique HTTP Firebase Function ne doit se trouver dans ce fichier :
il ne connait que l'API MAPI. Copie a l'identique de
cloud-functions/source/mapi_sms_test_code/clients/mapi_sms_client.py --
garder les deux synchronisees en cas de modification de la logique MAPI.

Limite connue : le cache de token est en memoire de processus, donc pas
partage entre plusieurs instances actives simultanement (scaling
horizontal). Le logout defensif limite le risque, mais ne l'elimine pas
totalement. Acceptable pour un outil de test a faible volume.
"""

import logging
import time

import requests

from config import MAPI_BASE_URL, MAPI_PASSWORD, MAPI_USERNAME

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 15

# Duree de vie annoncee d'un token MAPI (15 minutes). On se re-authentifie
# un peu avant l'expiration reelle pour eviter d'utiliser un token perime.
TOKEN_TTL_SECONDS = 900
TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS = 60

# Cache en memoire du token courant, partage entre toutes les invocations
# traitees par la meme instance de Cloud Function.
_token_cache = {"token": None, "expires_at": 0.0}


class MapiError(RuntimeError):
    """Erreur fonctionnelle renvoyee par l'API MAPI (numero malforme, plus
    de credit SMS, etc.) -- distincte d'une erreur de transport HTTP."""


def _token_is_valid() -> bool:
    return (
        _token_cache["token"] is not None
        and time.time() < _token_cache["expires_at"] - TOKEN_EXPIRY_SAFETY_MARGIN_SECONDS
    )


def _clear_token_cache() -> None:
    _token_cache["token"] = None
    _token_cache["expires_at"] = 0.0


def _logout_defensive() -> None:
    """Ferme une session potentiellement encore active aupres de MAPI.

    Best-effort : un logout qui echoue (pas de session active, timeout...)
    n'empeche pas de tenter le login qui suit, il ne fait que reduire le
    risque de l'erreur "L'utilisateur est encore en cours de session.".
    """
    if not _token_cache["token"]:
        return
    try:
        requests.post(
            f"{MAPI_BASE_URL}/api/authentication/logout",
            headers={"Authorization": _token_cache["token"]},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.RequestException:
        logger.warning("Logout defensif MAPI en echec, on tente quand meme le login.")
    finally:
        _clear_token_cache()


def _login() -> str:
    """Authentifie aupres de MAPI (multipart/form-data) et met le token en
    cache. Retourne le token obtenu."""
    _logout_defensive()

    response = requests.post(
        f"{MAPI_BASE_URL}/api/authentication/login",
        files={
            "Username": (None, MAPI_USERNAME),
            "Password": (None, MAPI_PASSWORD),
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    token = response.json()["token"]

    _token_cache["token"] = token
    _token_cache["expires_at"] = time.time() + TOKEN_TTL_SECONDS
    return token


def get_token() -> str:
    """Retourne un token JWT valide, en reutilisant le cache si possible."""
    if _token_is_valid():
        return _token_cache["token"]
    return _login()


def _mask_recipient(recipient: str) -> str:
    """Masque partiellement un numero pour les logs (ex: 0341234567 -> 034123****)."""
    if len(recipient) <= 4:
        return "*" * len(recipient)
    return recipient[:-4] + "*" * 4


def send_sms(recipient: str, message: str, *, _retry_on_auth_error: bool = True) -> dict:
    """Envoie un SMS personnalise unique via /api/msg/send.

    Retente automatiquement une fois en cas de 401 (token expire ou
    invalide) : un nouveau login est declenche -- en passant par _login()
    directement (pas juste _clear_token_cache()) pour que le logout
    defensif ferme reellement la session cote serveur avant de retenter,
    plutot que de simplement oublier le token localement (ce qui laisserait
    la session ouverte cote MAPI et ferait echouer le login de retry avec
    "session deja active", masquant l'erreur d'origine) -- puis l'envoi est
    retente. Leve MapiError pour tout autre echec fonctionnel (numero
    malforme, plus de credit SMS...), avec le message renvoye par MAPI. Les
    erreurs de transport HTTP (reseau, 5xx) remontent via requests.HTTPError
    / requests.RequestException.
    """
    token = get_token()
    masked = _mask_recipient(recipient)

    response = requests.post(
        f"{MAPI_BASE_URL}/api/msg/send",
        headers={"Authorization": token},
        files={
            "Recipient": (None, recipient),
            "Message": (None, message),
            "Channel": (None, "sms"),
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    if response.status_code == 401 and _retry_on_auth_error:
        logger.info("Token MAPI refuse (401) pour %s, relogin puis nouvel essai.", masked)
        _login()
        return send_sms(recipient, message, _retry_on_auth_error=False)

    try:
        payload = response.json()
    except ValueError:
        response.raise_for_status()
        raise MapiError(f"Reponse MAPI non-JSON inattendue (statut {response.status_code}).")

    if not payload.get("status", False):
        error_text = payload.get("result") or payload.get("message") or f"Echec MAPI (statut {response.status_code})."
        logger.warning("Echec envoi SMS vers %s : %s", masked, error_text)
        raise MapiError(error_text)

    logger.info("SMS envoye avec succes vers %s.", masked)
    return payload


def get_available_offer() -> dict:
    """Consulte le solde de SMS disponible (GET /api/smsoffer/available)."""
    token = get_token()
    response = requests.get(
        f"{MAPI_BASE_URL}/api/smsoffer/available",
        headers={"Authorization": token},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
