"""Points d'entree Firebase Function pour l'envoi de SMS via Befiana (SMS by Befiana).

Version "emulateur local" de cloud-functions/source/befiana_sms_test_code --
meme client (clients/befiana_sms_client.py, copie a l'identique).

Deux declencheurs independants, meme client sous-jacent :
  - send_sms_befiana_test_http     : HTTP direct (curl/Postman), reponse
                              synchrone immediate -- outil de test manuel.
  - send_sms_befiana_pubsub : evenementiel, declenche par un message publie
                              sur le topic Pub/Sub
                              "prod-sms-befiana-notifications" -- pour une
                              integration backend fire-and-forget, sur le
                              meme modele que process_email/
                              send_event_ticket/send_brochure_email et
                              send_sms_mapi_pubsub. Payload attendu :
                              {"phone": "...", "message": "..."} -- meme
                              convention que sms_sender_code (Orange) et
                              mapi_sms_test_code, pour ne pas imposer un
                              format different au backend qui publie.

Ce fichier ne contient volontairement aucune logique Befiana : il valide
l'entree (cle partagee + champs requis pour l'HTTP, champs requis pour le
Pub/Sub) puis delegue a clients.befiana_sms_client.

Exemple d'appel HTTP (emulateur, port 5001, projet demo-event-app) :
    curl -X POST "http://localhost:5001/demo-event-app/us-central1/send_sms_befiana_test_http" \\
        -H "Content-Type: application/json" \\
        -H "X-Api-Key: <API_SHARED_KEY>" \\
        -d '{"recipient":"0341234567","message":"Texte de test"}'

Exemple de publication Pub/Sub (emulateur, port 8085) :
    curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-sms-befiana-notifications:publish" \\
        -H "Content-Type: application/json" \\
        -d "{\\"messages\\":[{\\"data\\":\\"$(echo -n '{"phone":"0341234567","message":"Texte de test"}' | base64 -w0)\\"}]}"
"""

import json
import logging

from firebase_admin import initialize_app
from firebase_functions import https_fn, pubsub_fn
import requests

from clients.befiana_sms_client import BefianaError, send_sms
from config import API_SHARED_KEY, BEFIANA_API_KEY

initialize_app()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _json_response(body: dict, status: int) -> https_fn.Response:
    return https_fn.Response(json.dumps(body), status=status, content_type="application/json")


@https_fn.on_request()
def send_sms_befiana_test_http(req: https_fn.Request) -> https_fn.Response:
    """Envoie un SMS de test personnalise via Befiana.

    Body JSON attendu : {"recipient": "0341234567", "message": "..."}
    Header requis : X-Api-Key: <API_SHARED_KEY> -- protection minimale,
    pour eviter qu'un tiers ne declenche des envois et ne consomme le
    credit SMS (voir config.API_SHARED_KEY).

    config.py ne verifie plus la presence des variables d'environnement a
    l'import (contrainte de l'emulateur, voir config.py) : on la verifie
    donc ici, au moment de traiter la requete.
    """
    if not API_SHARED_KEY or not BEFIANA_API_KEY:
        logger.error("Configuration manquante dans .env.local (API_SHARED_KEY/BEFIANA_API_KEY).")
        return _json_response(
            {"status": False, "result": "Fonction mal configuree (.env.local incomplet)."}, 500
        )

    if req.headers.get("X-Api-Key") != API_SHARED_KEY:
        return _json_response({"status": False, "result": "Cle API invalide ou manquante."}, 401)

    data = req.get_json(silent=True) or {}
    recipient = (data.get("recipient") or "").strip()
    message = (data.get("message") or "").strip()

    if not recipient or not message:
        return _json_response(
            {"status": False, "result": "Champs 'recipient' et 'message' requis."}, 400
        )

    try:
        result = send_sms(recipient, message)
        return _json_response({"status": True, "result": result.get("message", result)}, 200)

    except BefianaError as error:
        logger.warning("Echec fonctionnel Befiana : %s", error)
        return _json_response({"status": False, "result": str(error)}, 409)

    except requests.HTTPError as error:
        logger.error("Erreur HTTP Befiana : %s", error)
        return _json_response({"status": False, "result": "Erreur de communication avec Befiana."}, 502)

    except requests.RequestException as error:
        logger.error("Erreur reseau vers Befiana : %s", error)
        return _json_response({"status": False, "result": "Befiana injoignable."}, 502)

    except Exception:
        logger.exception("Erreur inattendue lors de l'envoi SMS de test")
        return _json_response({"status": False, "result": "Erreur interne."}, 500)


@pubsub_fn.on_message_published(topic="prod-sms-befiana-notifications")
def send_sms_befiana_pubsub(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    """Envoie un SMS via Befiana, declenche par un evenement Pub/Sub.

    Payload attendu : {"phone": "0341234567", "message": "..."} -- meme
    convention que cloud-functions/source/sms_sender_code (Orange) et
    mapi_sms_test_code.

    Fire-and-forget par nature (Pub/Sub) : aucune reponse synchrone
    possible pour l'appelant, tout est logue. Une exception non rattrapee
    ici (ex: BefianaError, erreur HTTP) remonte au runtime Pub/Sub --
    meme comportement que send_sms_mapi_pubsub, volontairement pas de
    try/except large ici pour ne pas avaler silencieusement un echec
    d'envoi.
    """
    try:
        data = event.data.message.json
    except (ValueError, AttributeError) as error:
        logger.error("Message Pub/Sub invalide : %s", error)
        return

    if not BEFIANA_API_KEY:
        logger.error("Cle API Befiana manquante (.env.local), SMS non envoye.")
        return

    phone = data.get("phone")
    message = data.get("message")

    if not phone or not message:
        logger.warning("SMS ignore, 'phone' ou 'message' manquant : %s", data)
        return

    logger.info("Envoi SMS (Befiana, evenement Pub/Sub) vers %s", phone)
    result = send_sms(phone, message)
    logger.info("SMS Befiana envoye avec succes : %s", result)
