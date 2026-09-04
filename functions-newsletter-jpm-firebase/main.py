"""
Point d'entree Firebase Function : envoi de la newsletter JPM (Rentree du
Jeune Patronat 2026), declenchee par un evenement Pub/Sub sur un topic
dedie -- specifique a JPM, independant des topics email generiques
(prod-registration-confirmed, prod-event-ended, prod-email-notifications).

Template 100% statique (aucune variable {{...}}) : templates/newsletter_rjp.html
est la copie exacte du fichier fourni par l'utilisateur (files/newsletter-rjp.html),
avec les 12 logos partenaires deja integres en base64 dans la section
"Nos Partenaires" (etait vide dans le fichier source). Convertis en pieces
jointes CID a l'envoi (voir email_sender._embed_base64_images), meme
mecanisme que functions-brochure-firebase.

Payload Pub/Sub attendu :
    {"recipients": ["email1@x.com", "email2@x.com"]}
"recipients" peut aussi etre une simple chaine (un seul destinataire).
"subject" est optionnel (sinon NEWSLETTER_SUBJECT ci-dessous est utilise --
meme principe que les autres emails de ce projet : le sujet est genere ici,
pas envoye par le backend).
"""
import logging

from firebase_admin import initialize_app
from firebase_functions import pubsub_fn, options

from email_sender import send_newsletter_jpm_smtp

initialize_app()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEWSLETTER_SUBJECT = "La newsletter du Jeune Patronat — Rentrée du Jeune Patronat 2026"


@pubsub_fn.on_message_published(
    topic="prod-newsletter-jpm",
    region="us-central1",
    memory=options.MemoryOption.MB_512,
    timeout_sec=540,
)
def send_newsletter_jpm(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    """Envoie la newsletter JPM aux destinataires fournis dans le message."""
    try:
        data = event.data.message.json
    except (ValueError, AttributeError) as error:
        logger.error("Message Pub/Sub invalide : %s", error)
        return

    recipients = data.get("recipients")
    if not recipients:
        logger.warning("Newsletter JPM ignoree, 'recipients' manquant : %s", data)
        return

    subject = data.get("subject") or NEWSLETTER_SUBJECT
    nb = 1 if isinstance(recipients, str) else len(recipients)

    logger.info("Envoi newsletter JPM a %s destinataire(s)", nb)
    send_newsletter_jpm_smtp(recipients, subject)
    logger.info("Newsletter JPM envoyee avec succes")
