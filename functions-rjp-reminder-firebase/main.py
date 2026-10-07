import logging

from firebase_admin import initialize_app
from firebase_functions import pubsub_fn

from reminder_senders import send_rjp_reminder

# Initialiser Firebase Admin
initialize_app()


# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ZONE LOGIQUE — NE PAS MODIFIER SAUF DEV CONFIRMÉ          ║
# ║                                                              ║
# ║   Contient : écoute Pub/Sub Firebase, validation,           ║
# ║              dispatch par type, SMTP.                       ║
# ║   Modifier ici peut casser la livraison des emails.         ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝


@pubsub_fn.on_message_published(topic="prod-rjp-reminder")
def process_reminder(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    logging.info("=" * 80)
    logging.info("MESSAGE REÇU SUR PUB/SUB - prod-rjp-reminder")
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
    if email_type == "RJP_REMINDER_BOTH_DAYS":
        required_fields = ["type", "email", "lastName"]
        email_field = data.get("email", "")

    elif email_type == "RJP_REMINDER_DAY2":
        required_fields = ["type", "email", "lastName"]
        email_field = data.get("email", "")

    else:
        logging.warning(f"Type inconnu: {email_type}")
        return

    missing = [f for f in required_fields if f not in data]
    if missing:
        logging.error(f"Champs manquants: {missing}")
        return

    # ── Dispatch selon le type ──
    if email_type == "RJP_REMINDER_BOTH_DAYS":
        send_rjp_reminder(
            email=email_field,
            last_name=data["lastName"],
            reminder_type="BOTH_DAYS",
            genre=data.get("genre", "H"),
        )

    elif email_type == "RJP_REMINDER_DAY2":
        send_rjp_reminder(
            email=email_field,
            last_name=data["lastName"],
            reminder_type="DAY2",
            genre=data.get("genre", "H"),
        )
