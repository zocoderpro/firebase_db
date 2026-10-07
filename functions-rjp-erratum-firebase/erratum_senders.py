"""Email senders — email d'erratum RJP 2026 (précision localisation)."""
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
_MAPS_LINK = "https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5"

# Contenu HTML inline
_ERRATUM_BODY_HTML = """<p style="margin:0 0 16px 0;">Suite à notre précédent message concernant la <strong>RJP 2026</strong>, nous souhaitons vous apporter une <strong>précision importante</strong> concernant le lieu exact de l'événement.</p>

<p style="margin:0 0 16px 0;">Le lieu exact est le suivant :</p>

<p style="margin:0 0 16px 0;">Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au <strong>dernier étage</strong>.</p>

<p style="margin:0 0 0 0;">Nous vous prions de nous excuser pour ce rectificatif et restons à votre disposition pour toute question.</p>"""


def _load_rjp_jpm_image_bytes():
    path = os.path.join(_RJP_ASSET_DIR, "jpm.png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def send_rjp_erratum(
    email: str,
):
    """Envoie l'email d'erratum RJP 2026 (précision sur la localisation)."""

    salutation = "Bonjour,"

    subject = f"[Erratum] RJP 2026 - Précision sur la localisation"

    formule_politesse = "Bien cordialement,"

    # Rendu HTML
    template_path = os.path.join(os.path.dirname(__file__), "templates", "erratum.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    envelope_open = render_fragment("envelope_open", PREHEADER=subject, PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    html_content = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{BODY_TEXT}}": _ERRATUM_BODY_HTML,
        "{{SIGN_OFF}}": formule_politesse,
        "{{YEAR}}": str(datetime.now().year),
    }
    for k, v in replacements.items():
        html_content = html_content.replace(k, v)

    # Version texte
    text_body = f"""RJP via Athena Event – Erratum localisation

{salutation}

Suite à notre précédent message concernant la RJP 2026, nous souhaitons vous apporter une précision importante concernant le lieu exact de l'événement.

Le lieu exact est le suivant :

Vous trouverez ici la localisation du Patio Ivato : {_MAPS_LINK}

Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au dernier étage.

Nous vous prions de nous excuser pour ce rectificatif et restons à votre disposition pour toute question.

Bien cordialement,
L'équipe RJP 2026

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
    logging.info(f"Email d'erratum RJP envoyé à {email}")
