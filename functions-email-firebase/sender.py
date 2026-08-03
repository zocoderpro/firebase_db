# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ZONE LOGIQUE — ENVOI SMTP                                  ║
# ║                                                              ║
# ║   Modifier ici peut casser la livraison des emails.         ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import logging
import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.jpeg")


def _load_logo_image_part() -> MIMEImage:
    """Charge le logo Athena Event depuis assets/logo.jpeg pour intégration CID.
    Content-ID "logo" — référencé par LOGO_URL="cid:logo" dans config.py, utilisé
    par templates/fragments/hero.html via {{LOGO_URL}}."""
    with open(_LOGO_PATH, "rb") as f:
        image = MIMEImage(f.read(), _subtype="jpeg")
    image.add_header("Content-ID", "<logo>")
    image.add_header("Content-Disposition", "inline", filename="logo.jpeg")
    return image


def _build_image_part(cid: str, image_bytes: bytes, subtype: str = "png") -> MIMEImage:
    """Construit une pièce image inline avec un Content-ID donné (ex: QR codes)."""
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
    x_mailer: str = "Athena Event Platform",
    x_priority: str = None,
    extra_images: list = None,
) -> MIMEMultipart:
    """
    Construit un message MIME complet : related > (alternative > texte+html) + logo
    (+ images additionnelles éventuelles). Le logo est systématiquement attaché en
    CID — c'est ce qui garantit qu'il ne dépend plus jamais d'un serveur externe.

    extra_images : liste de tuples (cid, bytes, subtype) pour des images
                   supplémentaires (ex: QR code) à attacher en plus du logo.
    """
    outer = MIMEMultipart('related')
    alt = MIMEMultipart('alternative')
    alt.attach(MIMEText(text_content, 'plain', 'utf-8'))
    alt.attach(MIMEText(html_content, 'html', 'utf-8'))
    outer.attach(alt)
    outer.attach(_load_logo_image_part())

    for cid, image_bytes, subtype in (extra_images or []):
        outer.attach(_build_image_part(cid, image_bytes, subtype))

    outer['Subject'] = subject
    outer['From'] = f"Athena Event <{SMTP_USER}>"
    outer['To'] = to_addr
    if reply_to:
        outer['Reply-To'] = reply_to
    if message_id:
        outer['Message-ID'] = message_id
    if x_mailer:
        outer['X-Mailer'] = x_mailer
    if x_priority:
        outer['X-Priority'] = x_priority
    return outer


def _send_email(msg: MIMEMultipart) -> None:
    """
    Envoi SMTP centralisé — SMTP simple + STARTTLS (port 587).
    Toutes les fonctions send_xxx() passent par ici.
    """
    if not SMTP_PASSWORD:
        raise ValueError("SMTP_PASSWORD manquant — vérifier les variables d'environnement")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"❌ Erreur SMTP ({SMTP_HOST}:{SMTP_PORT}) : {e}")
        raise


def _format_expiry(expires_at_ms: int) -> str:
    """Convertit un timestamp en millisecondes en date lisible."""
    return datetime.fromtimestamp(expires_at_ms / 1000).strftime('%d %B %Y à %H:%M')
