"""
Point d'entree Firebase Function : email "Confirmez votre présence"
aux participants inscrits à la Rentrée du Jeune Patronat 2026.

Fonction volontairement isolee de functions-email-firebase (trop chargee) et
dediee a cet envoi ponctuel — meme modele que functions-newsletter-jpm-firebase
et functions-brochure-firebase : un topic dedie, un template figé.

Payload Pub/Sub attendu (topic "prod-rjp-email-confirmation") :
    {
      "type": "RJP_EMAIL_CONFIRMATION",
      "recipients": ["email1@x.com", "email2@x.com"],   # ou une simple chaine
      "subject": "..."                    # optionnel (sinon RJP_SUBJECT)
      "attachments": ["https://.../programme.pdf", "gs://bucket/plan.pdf"]  # optionnel
    }

"recipients" peut aussi etre remplace par "destinataire" ou "destEmail" (le
backend utilise ces noms selon les cas — meme tolerance que
functions-brochure-firebase).
"""
import logging

from firebase_admin import initialize_app
from firebase_functions import pubsub_fn

from attachments import load_attachments
from email_sender import send_rjp_email_confirmation as _send_rjp_email_confirmation

initialize_app()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pubsub_fn.on_message_published(topic="prod-rjp-email-confirmation")
def send_rjp_email_confirmation(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    """Envoie l'email de confirmation de présence RJP 2026 aux destinataires."""
    try:
        data = event.data.message.json
    except (ValueError, AttributeError) as error:
        logger.error("Message Pub/Sub invalide : %s", error)
        return

    if data.get("type") != "RJP_EMAIL_CONFIRMATION":
        logger.warning("Type ignore: %s (attendu RJP_EMAIL_CONFIRMATION)", data.get("type"))
        return

    recipients = (
        data.get("recipients")
        or data.get("destinataire")
        or data.get("destEmail")
        or data.get("email")
    )
    if not recipients:
        logger.warning("Email confirmation RJP ignore, 'email'/'recipients' manquant : %s", data)
        return

    # Nom du destinataire — optionnel. Accepte "name"/"fullName", ou
    # firstName + lastName (meme convention que les autres emails du projet).
    name = (
        data.get("name")
        or data.get("fullName")
        or " ".join(p for p in (data.get("firstName"), data.get("lastName")) if p)
        or None
    )

    subject = data.get("subject")
    attachments = load_attachments(data.get("attachments"))

    nb = 1 if isinstance(recipients, str) else len(recipients)
    logger.info("Envoi email confirmation RJP 2026 a %s destinataire(s), %s piece(s) jointe(s)",
                nb, len(attachments))
    _send_rjp_email_confirmation(recipients, name=name, subject=subject, attachments=attachments)
    logger.info("Email confirmation RJP 2026 envoye avec succes")
