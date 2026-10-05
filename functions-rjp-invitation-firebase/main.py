import logging

from firebase_admin import initialize_app
from firebase_functions import pubsub_fn

from invitation_senders import send_rjp_invitation, send_rjp_invitation_batch

# Initialiser Firebase Admin
initialize_app()


# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ZONE LOGIQUE — NE PAS MODIFIER SAUF DEV CONFIRMÉ          ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝


@pubsub_fn.on_message_published(topic="prod-rjp-invitation")
def process_invitation(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    logging.info("=" * 80)
    logging.info("MESSAGE REÇU SUR PUB/SUB - prod-rjp-invitation")
    logging.info("=" * 80)

    try:
        data = event.data.message.json
        logging.info(f"Type: {type(data)}, Champs: {len(data)}")
        for key, value in data.items():
            logging.info(f"   '{key}': '{value}' (type: {type(value).__name__})")
        logging.info("=" * 80)
    except (ValueError, AttributeError) as e:
        logging.error(f"Message invalide: {e}")
        return

    email_type = data.get("type")

    if not email_type:
        logging.error("Champ 'type' manquant")
        return

    logging.info(f"Type détecté: {email_type}")

    # ── Validation dynamique selon le type ──
    if email_type == "RJP_INVITATION":
        required_fields = ["type", "email", "firstName", "lastName"]
        email_field = data.get("email", "")

    elif email_type == "RJP_INVITATION_BATCH":
        required_fields = ["type", "email", "firstName", "lastName", "qrTokens", "qrCodes"]
        email_field = data.get("email", "")

    else:
        logging.warning(f"Type inconnu: {email_type}")
        return

    missing = [f for f in required_fields if f not in data]
    if missing:
        logging.error(f"Champs manquants: {missing}")
        return

    # ── Dispatch selon le type ──
    if email_type == "RJP_INVITATION":
        send_rjp_invitation(
            email=email_field,
            first_name=data["firstName"],
            last_name=data["lastName"],
            qr_token=data.get("qrToken", ""),
            fonction=data.get("fonction", ""),
            entite=data.get("entite", ""),
            genre=data.get("genre", "H"),
        )

    elif email_type == "RJP_INVITATION_BATCH":
        send_rjp_invitation_batch(
            email=email_field,
            first_name=data["firstName"],
            last_name=data["lastName"],
            qr_tokens=data["qrTokens"],
            qr_codes=data["qrCodes"],
            fonction=data.get("fonction", ""),
            entite=data.get("entite", ""),
            genre=data.get("genre", "H"),
            maps_link=data.get("maps_link", "https://maps.app.goo.gl/example"),
        )
