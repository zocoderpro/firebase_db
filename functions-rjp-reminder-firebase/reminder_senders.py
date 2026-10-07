"""Email senders — logique métier des rappels RJP."""
import html
import logging
import os
from datetime import datetime

from sender import _build_message, _send_email
from templates_handler import render_fragment

# ──────────────────────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────────────────────
_RJP_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "rjp2026")
_RJP2026_EVENT_TITLE = "Rentrée du Jeune Patronat 2026"
_MAPS_LINK = "https://www.google.com/maps/place/LE+PATIO/@-18.9132406,47.5394938,942m/data=!3m1!1e3!4m9!3m8!1s0x21f07d09b37831e3:0x8832bf18c8e4cbd8!5m2!4m1!1i2!8m2!3d-18.9132406!4d47.5394938!16s%2Fg%2F11lxvqs8bl?entry=ttu&g_ep=EgoyMDI2MTAwNC4wIKXMDSoASAFQAw%3D%3D"

# Contenus inline
_REMINDER_BOTH_DAYS = """<p style="margin:0 0 16px 0;">Nous avons le plaisir de vous rappeler que la <strong>Rentrée du Jeune Patronat 2026</strong> approche à grands pas !</p>

<p style="margin:0 0 16px 0;">Cet événement se déroulera sur <strong>deux journées</strong> riches en échanges, en rencontres et en opportunités de networking avec l'ensemble de notre écosystème.</p>

<p style="margin:0 0 0 0;">Nous nous réjouissons de vous accueillir à cette édition 2026 et restons à votre disposition pour toute question.</p>"""

_REMINDER_DAY2 = """<p style="margin:0 0 16px 0;">Nous vous rappelons que la <strong>deuxième journée</strong> de la <strong>Rentrée du Jeune Patronat 2026</strong> aura lieu demain.</p>

<p style="margin:0 0 16px 0;">Cette journée sera l'occasion de poursuivre les échanges et de renforcer les liens avec l'ensemble de notre écosystème.</p>

<p style="margin:0 0 0 0;">Au plaisir de vous retrouver pour cette deuxième journée !</p>"""


def _load_rjp_jpm_image_bytes():
    path = os.path.join(_RJP_ASSET_DIR, "jpm.png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def send_rjp_reminder(
    email: str,
    last_name: str,
    reminder_type: str = "BOTH_DAYS",
    genre: str = "H",
):
    """Envoie un email de rappel RJP.

    reminder_type:
        "BOTH_DAYS" → rappel pour les 2 jours (J1 + J2)
        "DAY2"      → rappel pour la journée 2 uniquement
    """
    safe_last_name = html.escape(last_name or "")

    genre = (genre or "").strip().upper()
    if genre == "F":
        salutation = f"Madame {safe_last_name}"
        titre_politesse = "Madame"
    elif genre == "H":
        salutation = f"Monsieur {safe_last_name}"
        titre_politesse = "Monsieur"
    else:
        salutation = f"Madame/Monsieur {safe_last_name}"
        titre_politesse = "Madame/Monsieur"

    # Contenu selon le type de rappel
    if reminder_type == "DAY2":
        body_text = _REMINDER_DAY2
        subject = f"Rappel — {_RJP2026_EVENT_TITLE} (Journée 2)"
    else:
        body_text = _REMINDER_BOTH_DAYS
        subject = f"Rappel — {_RJP2026_EVENT_TITLE} (J1 & J2)"

    formule_politesse = f"Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, {titre_politesse}, l'expression de nos salutations distinguées."

    # Rendu HTML
    template_path = os.path.join(os.path.dirname(__file__), "templates", "reminder.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    envelope_open = render_fragment("envelope_open", PREHEADER=f"Rappel — {_RJP2026_EVENT_TITLE}", PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    html_content = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{BODY_TEXT}}": body_text,
        "{{SIGN_OFF}}": formule_politesse,
        "{{YEAR}}": str(datetime.now().year),
    }
    for k, v in replacements.items():
        html_content = html_content.replace(k, v)

    # Version texte
    if reminder_type == "DAY2":
        text_body = f"""RJP via Athena Event – Rappel Journée 2

{salutation}

Nous vous rappelons que la deuxième journée de la Rentrée du Jeune Patronat 2026 aura lieu demain.

Cette journée sera l'occasion de poursuivre les échanges et de renforcer les liens avec l'ensemble de notre écosystème.

Au plaisir de vous retrouver pour cette deuxième journée !

Vous trouverez ici la localisation du Patio Ivato : {_MAPS_LINK}

{formule_politesse}

Bien cordialement,
L'équipe de la Rentrée du Jeune Patronat 2026

---
Athena Event by Clearmind Analytics
Antananarivo, Madagascar
athena-event.com"""
    else:
        text_body = f"""RJP via Athena Event – Rappel J1 & J2

{salutation}

Nous avons le plaisir de vous rappeler que la Rentrée du Jeune Patronat 2026 approche à grands pas !

Cet événement se déroulera sur deux journées riches en échanges, en rencontres et en opportunités de networking avec l'ensemble de notre écosystème.

Nous nous réjouissons de vous accueillir à cette édition 2026 et restons à votre disposition pour toute question.

Vous trouverez ici la localisation du Patio Ivato : {_MAPS_LINK}

{formule_politesse}

Bien cordialement,
L'équipe de la Rentrée du Jeune Patronat 2026

---
Athena Event by Clearmind Analytics
Antananarivo, Madagascar
athena-event.com"""

    # Images
    extra_images = []
    jpm_bytes = _load_rjp_jpm_image_bytes()
    if jpm_bytes:
        extra_images.append(("rjp_jpm", jpm_bytes, "png"))

    msg = _build_message(
        subject=subject,
        to_addr=email,
        text_content=text_body,
        html_content=html_content,
        extra_images=extra_images,
        attach_logo=False,
        from_name="RJP via Athena Event",
        attachments=[],
    )

    _send_email(msg)
    logging.info(f"Email de rappel RJP ({reminder_type}) envoyé à {email}")
