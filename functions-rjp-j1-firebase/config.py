"""
Configuration centralisee pour la fonction "Participants J1" (RJP 2026).

Meme compte SMTP que les autres fonctions email de ce projet (Zoho/ZeptoMail).
Copie volontaire de functions-email-firebase/config.py : chaque codebase
Firebase est independant (pas d'import cross-dossier).
"""
import os

# ──────────────────────────────────────────────────────────────
# CONFIG VISUELLE
# ──────────────────────────────────────────────────────────────

# Image de fond du hero — utilisee par _hero() uniquement. Ce template passe
# par _rjp2026_header(), donc la valeur n'est pas utilisee, mais elle est
# requise par l'import de templates/components.py au chargement.
HERO_IMAGE_URL = "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=600&q=80&auto=format&fit=crop"

# Logo Athena Event — integre en CID (assets/logo.jpeg). Non utilise par le
# bandeau RJP 2026, mais requis par l'import de components.py.
LOGO_URL = "cid:logo"


# ──────────────────────────────────────────────────────────────
# CONFIG SMTP
# ──────────────────────────────────────────────────────────────

SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER     = os.environ.get("SMTP_USER", "noreply@athena-event.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")


# ──────────────────────────────────────────────────────────────
# CONFIG RJP 2026 — template figé, propre à cet événement
# ──────────────────────────────────────────────────────────────

# Localisation du Patio Ivato (lien fourni par l'organisateur).
RJP_MAP_URL = "https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5"

# Espace WhatsApp RJP — actualités et rappels sur le téléphone.
RJP_WHATSAPP_URL = "https://chat.whatsapp.com/Dsj23q5yNWZ1Sz28YXn4ad?mode=gi_t"

# Numéro de contact avant l'événement.
RJP_PHONE = "+261 34 04 105 06"

# Sujet par défaut (le backend peut le surcharger via le champ "subject").
RJP_SUBJECT = "RJP 2026 : Préparez votre venue le 8 octobre"

# Nom affiché dans l'expéditeur (template co-brandé JPM).
RJP_FROM_NAME = "RJP via Athena Event"

# Configuration Firebase Storage (pour les pièces jointes gs://).
BUCKET_NAME = os.environ.get("BUCKET_NAME", "athena-event-prod")
