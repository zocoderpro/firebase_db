"""
Configuration centralisee pour la fonction newsletter JPM.
Meme compte SMTP que les autres fonctions email de ce projet (Zoho).
"""
import os

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "noreply@athena-event.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

NEWSLETTER_TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "templates", "newsletter_rjp.html"
)
