import os

# ──────────────────────────────────────────────────────────────
# CONFIG VISUELLE
# Les deux seules valeurs à changer quand tu as tes vrais assets
# ──────────────────────────────────────────────────────────────

# Image de fond du hero — recommandé : 1200×400px, hébergée sur GCS/Firebase
HERO_IMAGE_URL = "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80&auto=format&fit=crop"

# Logo Athena Event — intégré en CID (assets/logo.jpeg), plus de dépendance à une
# URL externe. Voir email_sender.py::_load_logo_image_part().
LOGO_URL = "cid:logo"


# ──────────────────────────────────────────────────────────────
# CONFIG SMTP
# ──────────────────────────────────────────────────────────────

SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "noreply@athena-event.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
