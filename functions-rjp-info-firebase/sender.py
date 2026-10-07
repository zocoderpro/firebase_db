import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.jpeg")


def _load_logo_image_part() -> MIMEImage:
    """Charge le logo Athena Event depuis assets/logo.jpeg pour intégration CID."""
    with open(_LOGO_PATH, "rb") as f:
        image = MIMEImage(f.read(), _subtype="jpeg")
    image.add_header("Content-ID", "<logo>")
    image.add_header("Content-Disposition", "inline", filename="logo.jpeg")
    return image


def _build_image_part(cid: str, image_bytes: bytes, subtype: str = "png") -> MIMEImage:
    """Construit une pièce image inline avec un Content-ID donné."""
    image = MIMEImage(image_bytes, _subtype=subtype)
    image.add_header("Content-ID", f"<{cid}>")
    image.add_header("Content-Disposition", "inline", filename=f"{cid}.{subtype}")
    return image


def _build_message(
    subject: str,
    to_addr: str,
    text_content: str,
    html_content: str,
    reply_to: str = None,
    message_id: str = None,
    extra_images: list = None,
    attach_logo: bool = True,
    from_name: str = "Athena Event",
    attachments: list = None,
) -> MIMEMultipart:
    """
    Construits un message MIME complet : related > (alternative > texte+html) + logo
    + images additionnelles + pièces jointes optionnelles.
    """
    outer = MIMEMultipart('related')
    alt = MIMEMultipart('alternative')
    alt.attach(MIMEText(text_content, 'plain', 'utf-8'))
    alt.attach(MIMEText(html_content, 'html', 'utf-8'))
    outer.attach(alt)
    if attach_logo:
        outer.attach(_load_logo_image_part())

    for cid, image_bytes, subtype in (extra_images or []):
        outer.attach(_build_image_part(cid, image_bytes, subtype))

    # Pièces jointes (PDF, etc.)
    for filename, file_bytes, mime_type in (attachments or []):
        from email.mime.application import MIMEApplication
        attachment = MIMEApplication(file_bytes, _subtype=mime_type)
        attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        outer.attach(attachment)

    outer['Subject'] = subject
    outer['From'] = f"{from_name} <{SMTP_USER}>"
    outer['To'] = to_addr
    if reply_to:
        outer['Reply-To'] = reply_to
    if message_id:
        outer['Message-ID'] = message_id
    return outer


def _send_email(msg: MIMEMultipart) -> None:
    """Envoi SMTP centralisé — SMTP simple + STARTTLS (port 587)."""
    if not SMTP_PASSWORD:
        raise ValueError("SMTP_PASSWORD manquant — vérifier les variables d'environnement")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Erreur SMTP ({SMTP_HOST}:{SMTP_PORT}) : {e}")
        raise
