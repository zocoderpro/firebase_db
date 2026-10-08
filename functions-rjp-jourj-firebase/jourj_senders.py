"""Email senders — email Jour J RJP 2026."""
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
_JOURJ_BODY_HTML = """<p style="margin:0 0 16px 0;"><strong>RJP 2026 : Jour J !</strong> Nous avons hâte de vous retrouver ce soir.</p>

<p style="margin:0 0 16px 0;">Nous souhaitons vous rappeler le lieu exact de l'événement :</p>

<p style="margin:0 0 16px 0;">Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au <strong>dernier étage</strong>.</p>

<p style="margin:0 0 0 0;">Nous vous prions de nous excuser pour ce second message et restons à votre disposition pour toute question.</p>

<p style="margin:0 0 0 0;">À ce soir,</p>"""


def _load_rjp_jpm_image_bytes():
    path = os.path.join(_RJP_ASSET_DIR, "jpm.png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def send_rjp_jourj(
    email: str,
):
    """Envoie l'email Jour J RJP 2026."""
    salutation = "Bonjour,"

    subject = f"RJP 2026 : Jour J !"

    formule_politesse = "Bien cordialement,"

    # Rendu HTML
    template_path = os.path.join(os.path.dirname(__file__), "templates", "jourj.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    envelope_open = render_fragment("envelope_open", PREHEADER=subject, PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    html_content = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{BODY_TEXT}}": _JOURJ_BODY_HTML,
        "{{SIGN_OFF}}": formule_politesse,
        "{{YEAR}}": str(datetime.now().year),
    }
    for k, v in replacements.items():
        html_content = html_content.replace(k, v)

    # Version texte
    text_body = f"""RJP via Athena Event — Jour J

{salutation}

RJP 2026 : Jour J ! Nous avons hâte de vous retrouver ce soir.

Nous souhaitons vous rappeler le lieu exact de l'événement :

Vous trouverez ici la localisation du Patio Ivato : {_MAPS_LINK}

Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au dernier étage.

Nous vous prions de nous excuser pour ce second message et restons à votre disposition pour toute question.

À ce soir,
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
    logging.info(f"Email Jour J RJP envoyé à {email}")
