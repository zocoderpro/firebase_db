"""
Configuration centralisée pour la fonction brochure email.
Modifier ici pour changer les paramètres globaux.
"""
import os

# Configuration SMTP
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "noreply@athena-event.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

# Configuration Firebase Storage
BUCKET_NAME = os.environ.get("BUCKET_NAME", "athena-event-prod")

# Marque affichée dans le bandeau d'en-tête de templates/email.html
BRAND_NAME = "Athena Event"
BRAND_KICKER = "by Clearmind Analytics"
