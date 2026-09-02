"""Client pour l'API SMS Befiana (SMS by Befiana, api.befiana.cloud).

Contrairement a MAPI, l'authentification est une simple cle API statique
passee dans le header "Authorization" (sans prefixe "Bearer") -- pas de
login, pas de token a renouveler, pas de notion de session. Ce module est
donc volontairement plus simple que clients/mapi_sms_client.py (pas de
cache de token, pas de retry sur 401). Copie a l'identique de
cloud-functions/source/befiana_sms_test_code/clients/befiana_sms_client.py
-- garder les deux synchronisees en cas de modification.

Contrat verifie par appels reels le 2026-09-02 (la documentation publique
etait imprecise/erronee sur plusieurs points, corriges ici) :
  - POST /api/smsko/v1/send/ , body JSON {"phone_number": "...", "message": "..."},
    Content-Type: application/json (pas multipart/form-data comme MAPI).
  - Le numero doit faire exactement 9 chiffres et commencer par "3" (donc
    sans le 0 initial madagascar, ex: "0341234567" -> "341234567") --
    valide aussi cote serveur, avec un message d'erreur explicite si le
    format est incorrect.
  - Reponse succes : {"message": "SMS sent successfully.", "address":
    "+261...", "clientCorrelator": "...", "callbackData": "..."}.
  - Reponse erreur (cle invalide, numero invalide, solde insuffisant...) :
    {"error": "..."} -- PAS {"message": "..."} comme indique dans la doc.
  - Cle API invalide -> 403 (pas 401 comme indique dans la doc).
  - GET /api/smsko/v1/balance/ -> {"balance": <int>, "last_updated":
    "<ISO 8601>", "validity": "YYYY-MM-DD"} -- pas de champ "user" comme
    indique dans la doc.

Aucune logique HTTP Firebase Function ne doit se trouver dans ce fichier :
il ne connait que l'API Befiana.
"""

import logging

import requests

from config import BEFIANA_API_KEY, BEFIANA_BASE_URL

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT_SECONDS = 15


class BefianaError(RuntimeError):
    """Erreur fonctionnelle renvoyee par l'API Befiana (numero invalide,
    cle invalide, solde insuffisant, etc.) -- distincte d'une erreur de
    transport HTTP."""


def _headers() -> dict:
    return {"Authorization": BEFIANA_API_KEY}


def normalize_phone(raw_phone: str) -> str:
    """Convertit un numero au format usuel (avec 0 initial, ex:
    "0341234567") vers le format exact attendu par Befiana ("341234567").

    Accepte aussi un numero deja au bon format, ou prefixe par +261/261.
    Ne valide pas la forme finale ici : Befiana le fait cote serveur avec
    un message d'erreur clair (voir send_sms), inutile de dupliquer cette
    logique -- on se contente de retirer les prefixes courants.
    """
    phone = raw_phone.strip().replace(" ", "")
    if phone.startswith("+261"):
        phone = phone[4:]
    elif phone.startswith("261") and len(phone) > 9:
        phone = phone[3:]
    if phone.startswith("0"):
        phone = phone[1:]
    return phone


def _mask_recipient(phone: str) -> str:
    """Masque partiellement un numero pour les logs (ex: 341234567 -> 34123****)."""
    if len(phone) <= 4:
        return "*" * len(phone)
    return phone[:-4] + "*" * 4


def send_sms(recipient: str, message: str) -> dict:
    """Envoie un SMS personnalise unique via /api/smsko/v1/send/.

    recipient : numero au format usuel (avec ou sans 0 initial, avec ou
    sans +261) -- normalise en interne via normalize_phone().

    Leve BefianaError pour tout echec fonctionnel (numero invalide, cle
    invalide, solde insuffisant...), avec le message renvoye par Befiana.
    Les erreurs de transport HTTP (reseau, 5xx) remontent via
    requests.HTTPError / requests.RequestException.
    """
    phone = normalize_phone(recipient)
    masked = _mask_recipient(phone)

    response = requests.post(
        f"{BEFIANA_BASE_URL}/api/smsko/v1/send/",
        headers=_headers(),
        json={"phone_number": phone, "message": message},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    try:
        payload = response.json()
    except ValueError:
        response.raise_for_status()
        raise BefianaError(f"Reponse Befiana non-JSON inattendue (statut {response.status_code}).")

    if response.status_code != 200 or "error" in payload:
        error_text = payload.get("error") or f"Echec Befiana (statut {response.status_code})."
        logger.warning("Echec envoi SMS vers %s : %s", masked, error_text)
        raise BefianaError(error_text)

    logger.info("SMS envoye avec succes vers %s.", masked)
    return payload


def get_balance() -> dict:
    """Consulte le solde de SMS disponible (GET /api/smsko/v1/balance/)."""
    response = requests.get(
        f"{BEFIANA_BASE_URL}/api/smsko/v1/balance/",
        headers=_headers(),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()
