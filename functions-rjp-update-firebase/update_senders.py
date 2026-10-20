"""Email senders — email de mise à jour du programme RJP 2026."""
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
_PDF_PATH = os.path.join(os.path.dirname(__file__), "assets", "programme_rjp_update.pdf")
_RJP2026_EVENT_TITLE = "Rentrée du Jeune Patronat 2026"

# Contenu HTML inline
_UPDATE_BODY_HTML = """<p style="margin:0 0 16px 0;">Suite à notre précédent message, nous souhaitons vous informer d'une <strong>modification du programme</strong> de la RJP 2026, qui a lieu ce soir.</p>

<p style="margin:0 0 16px 0;">Le discours de l'Ambassadeur est <strong>annulé</strong>.</p>

<p style="margin:0 0 16px 0;">Le programme a donc été ajusté en conséquence :</p>

<p style="margin:0 0 16px 0;">Vous trouverez en pièce jointe le programme mis à jour.</p>

<p style="margin:0 0 0 0;">Nous vous prions de nous excuser pour ce changement et restons à votre disposition pour toute question.</p>

<p style="margin:0 0 0 0;">À ce soir,</p>"""


def _load_pdf_attachment():
    if not os.path.exists(_PDF_PATH):
        logging.warning(f"PDF introuvable: {_PDF_PATH}")
        return None
    with open(_PDF_PATH, "rb") as f:
        return ("Programme RJP 2026 - Mis à jour.pdf", f.read(), "pdf")


def _load_rjp_jpm_image_bytes():
    path = os.path.join(_RJP_ASSET_DIR, "jpm.png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def send_rjp_update(
    email: str,
):
    """Envoie l'email de mise à jour du programme RJP 2026."""
    salutation = "Bonjour,"

    subject = f"RJP 2026 : Mise à jour du programme"

    formule_politesse = "Bien cordialement,"

    # Rendu HTML
    template_path = os.path.join(os.path.dirname(__file__), "templates", "update.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    envelope_open = render_fragment("envelope_open", PREHEADER=subject, PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    html_content = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{BODY_TEXT}}": _UPDATE_BODY_HTML,
        "{{SIGN_OFF}}": formule_politesse,
        "{{YEAR}}": str(datetime.now().year),
    }
    for k, v in replacements.items():
        html_content = html_content.replace(k, v)

    # Version texte
    text_body = f"""RJP via Athena Event – Mise à jour du programme

{salutation}

Suite à notre précédent message, nous souhaitons vous informer d'une modification du programme de la RJP 2026, qui a lieu ce soir.

Le discours de l'Ambassadeur est annulé.

Le programme a donc été ajusté en conséquence :

Vous trouverez en pièce jointe le programme mis à jour.

Nous vous prions de nous excuser pour ce changement et restons à votre disposition pour toute question.

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

    # PDF en pièce jointe
    pdf_attachment = _load_pdf_attachment()
    attachments = [pdf_attachment] if pdf_attachment else []

    msg = _build_message(
        subject=subject,
        to_addr=email,
        text_content=text_body,
        html_content=html_content,
        extra_images=extra_images,
        attach_logo=False,
        from_name="RJP via Athena Event",
        attachments=attachments,
    )

    _send_email(msg)
    logging.info(f"Email de mise à jour du programme RJP envoyé à {email}")
