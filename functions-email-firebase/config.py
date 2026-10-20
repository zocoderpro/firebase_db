import os

# ──────────────────────────────────────────────────────────────
# CONFIG VISUELLE
# ──────────────────────────────────────────────────────────────

# Logo Athena Event — intégré en CID (assets/logo.jpeg), plus de dépendance à une
# URL externe. Voir sender.py::_load_logo_image_part().
LOGO_URL = "cid:logo"

# Marque affichée dans le bandeau d'en-tête de templates/email.html
BRAND_NAME   = "Athena Event"
BRAND_KICKER = "by Clearmind Analytics"


# ──────────────────────────────────────────────────────────────
# CONFIG SMTP & APP
# Centralisées ici — ne pas redéclarer dans chaque fonction
# ──────────────────────────────────────────────────────────────

SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "noreply@athena-event.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

APP_BASE_URL  = os.environ.get("APP_BASE_URL", "https://app.athena-event.com")
