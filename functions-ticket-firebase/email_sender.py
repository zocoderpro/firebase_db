# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU DE L'EMAIL                                         ║
# ║                                                              ║
# ║   C'est ici que tu modifies les textes et les données        ║
# ║   affichées dans l'email de confirmation. Le design (HTML)   ║
# ║   vit dans templates/email.html — aucun HTML ici.            ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import base64
import html
import logging
import os
import smtplib
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from templates_handler import render_email

_LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.jpeg")


def _load_logo_image_part() -> MIMEImage:
    """Charge le logo Athena Event depuis assets/logo.jpeg pour intégration CID.
    Content-ID "logo" — référencé par LOGO_URL="cid:logo" dans config.py."""
    with open(_LOGO_PATH, "rb") as f:
        image = MIMEImage(f.read(), _subtype="jpeg")
    image.add_header("Content-ID", "<logo>")
    image.add_header("Content-Disposition", "inline", filename="logo.jpeg")
    return image


def _row(label: str, value: str) -> dict:
    """Ligne « libellé / valeur » du récapitulatif de templates/email.html."""
    return {"LABEL": label, "VALUE": value}


def send_ticket_email_invited(
    email: str,
    destinateur_first_name: str,
    destinateur_last_name: str,
    badge_owner_first_name: str,
    badge_owner_last_name: str,
    event_title: str,
    event_start: str,
    event_location: str,
    qr_base64: str,
    registration_id: str,
    qr_token: str,
    event_image_url: str = None,
):
    """
    Email envoyé au commanditaire (emailDestinateur) pour un billet
    appartenant à une autre personne (userPropretaireBadge...).

    - greeting         → Bonjour {destinateur}
    - Participant card → badge_owner (la personne qui utilisera le billet)
    """
    SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
    SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER     = os.environ.get("SMTP_USER", "noreply@athena-event.com")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

    if not all([SMTP_USER, SMTP_PASSWORD]):
        logging.error("Variables SMTP manquantes")
        raise ValueError("Configuration SMTP incomplète")

    badge_owner_full = f"{badge_owner_first_name} {badge_owner_last_name}"

    safe_destinateur_first_name = html.escape(destinateur_first_name or "")
    safe_destinateur_last_name = html.escape(destinateur_last_name or "")
    safe_badge_owner_full = html.escape(badge_owner_full or "")
    safe_event_title = html.escape(event_title or "")
    safe_event_start = html.escape(str(event_start or ""))
    safe_event_location = html.escape(event_location or "")
    safe_qr_token = html.escape(qr_token or "")

    # event_image_url : accepté pour compatibilité avec le payload du backend, mais
    # plus utilisé — le hero du nouveau design est uni (pas d'image de fond).
    html_content = render_email(
        PREHEADER=f"Billet de {safe_badge_owner_full} confirmé — {safe_event_title}",
        EYEBROW="Billet événement",
        TITLE="Confirmation d'inscription",
        SUBTITLE=f"Billet pour {safe_event_title}",
        GREETING=f"Bonjour {safe_destinateur_first_name} {safe_destinateur_last_name},",
        INTRO=(
            f"Nous avons le plaisir de vous confirmer l'inscription de "
            f"<strong>{safe_badge_owner_full}</strong>. "
            "Veuillez lui transmettre cet email — "
            "il contient son code d'accès personnel à l'événement."
        ),
        FACTS=[
            {"LABEL": "Date", "VALUE": safe_event_start},
            {"LABEL": "Lieu", "VALUE": safe_event_location},
        ],
        INFO_TITLE="Détails de l'inscription",
        INFO_ROWS=[
            _row("Participant", safe_badge_owner_full),
            _row("Événement", safe_event_title),
        ],
        TICKET_EYEBROW="Billet événement",
        TICKET_TITLE=safe_event_title,
        TICKETS=[{
            "TICKET_LABEL": "Code d'accès personnel",
            "TICKET_NAME": safe_badge_owner_full,
            "CID": "qrcode",
            "TOKEN": safe_qr_token,
        }],
        ALERT_KIND="danger",
        ALERT_TITLE="Consignes de sécurité importantes",
        ALERT_ITEMS=[{"TEXT": item} for item in (
            f"Ce billet est au nom de <strong>{safe_badge_owner_full}</strong>",
            "<strong>Ne partagez pas ce QR code</strong> en dehors de la personne concernée",
            "Ce code est <strong>strictement personnel</strong> et identifie le participant de manière unique",
            "Toute personne en possession de ce code peut accéder à l'événement à sa place",
            "En cas de perte ou de vol, <strong>contactez-nous immédiatement</strong>",
        )],
        NOTE_END=(
            "Nous vous remercions pour votre confiance et restons à votre disposition "
            "pour toute question."
        ),
        SIGN_OFF="Cordialement,",
    )

    text_content = f"""Athena Event - Confirmation d'inscription

Bonjour {destinateur_first_name} {destinateur_last_name},

Nous avons le plaisir de vous confirmer l'inscription de {badge_owner_full}
à l'événement suivant.

DÉTAILS DE L'INSCRIPTION

Participant : {badge_owner_full}
Événement   : {event_title}
Date        : {event_start}
Lieu        : {event_location}

{qr_token}

CONSIGNES DE SÉCURITÉ :
- Ce billet est au nom de {badge_owner_full}
- Ne partagez pas ce QR code en dehors de la personne concernée
- Ce code est strictement personnel et identifie le participant de manière unique
- Toute personne en possession de ce code peut accéder à l'événement à sa place
- En cas de perte ou de vol, contactez-nous immédiatement

Cordialement,
L'équipe Athena Event

---
+261 38 32 046 13
sales@athena-event.com
www.athena-event.com

© {datetime.now().year} Athena Event by Clearmind Analytics
Antananarivo, Madagascar"""

    msg             = MIMEMultipart('related')
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_alternative.attach(MIMEText(text_content, 'plain', 'utf-8'))
    msg_alternative.attach(MIMEText(html_content, 'html',  'utf-8'))

    qr_bytes = base64.b64decode(qr_base64)
    qr_image = MIMEBase('image', 'png')
    qr_image.set_payload(qr_bytes)
    encoders.encode_base64(qr_image)
    qr_image.add_header('Content-ID', '<qrcode>')
    qr_image.add_header('Content-Disposition', 'inline', filename='qrcode.png')
    msg.attach(qr_image)
    msg.attach(_load_logo_image_part())

    msg['Subject']    = f"Billet de {badge_owner_full} — {event_title}"
    msg['From']       = f"Athena Event <{SMTP_USER}>"
    msg['To']         = email
    msg['Reply-To']   = SMTP_USER
    msg['Message-ID'] = f"<{registration_id}@athena-event.com>"
    msg['X-Mailer']   = "Athena Event Platform"

    try:
        with smtplib.SMTP(SMTP_HOST, 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info(f"Email billet invité envoyé à {email} (billet: {badge_owner_full})")
    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")
        raise


def send_ticket_email_with_qr(
    email: str,
    first_name: str,
    last_name: str,
    event_title: str,
    event_start: str,
    event_location: str,
    qr_base64: str,
    registration_id: str,
    qr_token: str,
    event_image_url: str = None,
):
    SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
    SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER     = os.environ.get("SMTP_USER", "noreply@athena-event.com")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

    if not all([SMTP_USER, SMTP_PASSWORD]):
        logging.error("Variables SMTP manquantes")
        raise ValueError("Configuration SMTP incomplète")

    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_email = html.escape(email or "")
    safe_event_title = html.escape(event_title or "")
    safe_event_start = html.escape(str(event_start or ""))
    safe_event_location = html.escape(event_location or "")
    safe_qr_token = html.escape(qr_token or "")

    # event_image_url : accepté pour compatibilité avec le payload du backend, mais
    # plus utilisé — le hero du nouveau design est uni (pas d'image de fond).
    html_content = render_email(
        PREHEADER=f"Votre billet est confirmé — {safe_event_title}",
        EYEBROW="Billet événement",
        TITLE="Confirmation d'inscription",
        SUBTITLE=f"Votre billet pour {safe_event_title}",
        GREETING=f"Bonjour {safe_first_name} {safe_last_name},",
        INTRO=(
            "Nous avons le plaisir de confirmer votre inscription. "
            "Veuillez conserver cet email précieusement — "
            "il contient votre code d'accès personnel à l'événement."
        ),
        FACTS=[
            {"LABEL": "Date", "VALUE": safe_event_start},
            {"LABEL": "Lieu", "VALUE": safe_event_location},
        ],
        INFO_TITLE="Détails de votre inscription",
        INFO_ROWS=[
            _row("Participant", f"{safe_first_name} {safe_last_name}"),
            _row("Email", safe_email),
            _row("Événement", safe_event_title),
        ],
        TICKET_EYEBROW="Billet événement",
        TICKET_TITLE=safe_event_title,
        TICKETS=[{
            "TICKET_LABEL": "Code d'accès personnel",
            "TICKET_NAME": f"{safe_first_name} {safe_last_name}",
            "CID": "qrcode",
            "TOKEN": safe_qr_token,
        }],
        ALERT_KIND="danger",
        ALERT_TITLE="Consignes de sécurité importantes",
        ALERT_ITEMS=[{"TEXT": item} for item in (
            "<strong>Ne partagez jamais ce QR code</strong> avec qui que ce soit",
            "Ce code est <strong>strictement personnel</strong> et vous identifie de manière unique",
            "Toute personne en possession de ce code peut accéder à l'événement à votre place",
            "Ne publiez pas ce billet sur les réseaux sociaux",
            "En cas de perte ou de vol, <strong>contactez-nous immédiatement</strong>",
        )],
        NOTE_END=(
            "Nous vous remercions pour votre confiance et restons à votre disposition "
            "pour toute question."
        ),
        SIGN_OFF="Cordialement,",
    )

    text_content = f"""Athena Event - Confirmation d'inscription

Bonjour {first_name} {last_name},

Nous avons le plaisir de confirmer votre inscription à l'événement suivant.

DÉTAILS DE VOTRE INSCRIPTION

Participant : {first_name} {last_name}
Email       : {email}
Événement   : {event_title}
Date        : {event_start}
Lieu        : {event_location}

{qr_token}

CONSIGNES DE SÉCURITÉ :
- Ne partagez jamais ce QR code avec qui que ce soit
- Ce code est strictement personnel et vous identifie de manière unique
- Toute personne en possession de ce code peut accéder à l'événement à votre place
- Ne publiez pas ce billet sur les réseaux sociaux
- En cas de perte ou de vol, contactez-nous immédiatement

Cordialement,
L'équipe Athena Event

---
+261 38 32 046 13
sales@athena-event.com
www.athena-event.com

© {datetime.now().year} Athena Event by Clearmind Analytics
Antananarivo, Madagascar"""

    # ── Construction MIME — structure : related > alternative + image CID ──
    # NOTE TECHNIQUE : MIMEMultipart('related') est nécessaire pour embarquer
    # le QR code inline via Content-ID sans qu'il apparaisse comme pièce jointe.
    msg             = MIMEMultipart('related')
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_alternative.attach(MIMEText(text_content, 'plain', 'utf-8'))
    msg_alternative.attach(MIMEText(html_content, 'html',  'utf-8'))

    qr_bytes = base64.b64decode(qr_base64)
    qr_image = MIMEBase('image', 'png')
    qr_image.set_payload(qr_bytes)
    encoders.encode_base64(qr_image)
    qr_image.add_header('Content-ID', '<qrcode>')
    qr_image.add_header('Content-Disposition', 'inline', filename='qrcode.png')
    msg.attach(qr_image)
    msg.attach(_load_logo_image_part())

    msg['Subject']    = f"Confirmation d'inscription — {event_title}"
    msg['From']       = f"Athena Event <{SMTP_USER}>"
    msg['To']         = email
    msg['Reply-To']   = SMTP_USER
    msg['Message-ID'] = f"<{registration_id}@athena-event.com>"
    msg['X-Mailer']   = "Athena Event Platform"

    # NOTE : SMTP simple + starttls port 587
    try:
        with smtplib.SMTP(SMTP_HOST, 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info(f"Email billet envoyé à {email}")
    except Exception as e:
        logging.error(f"Erreur envoi email : {e}")
        logging.error(f"Diagnostic — email param: {email!r} | msg['To']: {msg['To']!r} | SMTP_HOST: {SMTP_HOST!r}")
        raise


def send_ticket_email_multiticket(
    email: str,
    first_name: str,
    last_name: str,
    event_title: str,
    event_start: str,
    event_location: str,
    qr_base64_list: list,
    qr_tokens: list,
    registration_id: str,
    event_image_url: str = None,
):
    """
    Email de confirmation groupé : plusieurs billets (donc plusieurs QR codes,
    un par personne) envoyés dans un seul email à un même destinataire.
    Un bloc QR distinct est affiché par billet, chacun avec son propre
    Content-ID (qrcode1, qrcode2, ...) pour éviter tout conflit d'image inline.
    """
    SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.zeptomail.com")
    SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER     = os.environ.get("SMTP_USER", "noreply@athena-event.com")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

    if not all([SMTP_USER, SMTP_PASSWORD]):
        logging.error("Variables SMTP manquantes")
        raise ValueError("Configuration SMTP incomplète")

    ticket_count = len(qr_tokens)

    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_email = html.escape(email or "")
    safe_event_title = html.escape(event_title or "")
    safe_event_start = html.escape(str(event_start or ""))
    safe_event_location = html.escape(event_location or "")
    safe_qr_tokens = [html.escape(token or "") for token in qr_tokens]

    # event_image_url : accepté pour compatibilité avec le payload du backend, mais
    # plus utilisé — le hero du nouveau design est uni (pas d'image de fond).
    html_content = render_email(
        PREHEADER=f"Vos {ticket_count} billets sont confirmés — {safe_event_title}",
        EYEBROW="Billets événement",
        TITLE="Confirmation d'inscription",
        SUBTITLE=f"Vos {ticket_count} billets pour {safe_event_title}",
        GREETING=f"Bonjour {safe_first_name} {safe_last_name},",
        INTRO=(
            f"Nous avons le plaisir de confirmer votre inscription pour "
            f"<strong>{ticket_count} billets</strong>. Chaque billet ci-dessous "
            "dispose de son propre code d'accès — merci de conserver cet email "
            "précieusement et de présenter séparément chaque code à l'entrée "
            "de l'événement."
        ),
        FACTS=[
            {"LABEL": "Date", "VALUE": safe_event_start},
            {"LABEL": "Lieu", "VALUE": safe_event_location},
        ],
        INFO_TITLE="Détails de l'inscription",
        INFO_ROWS=[
            _row("Participant", f"{safe_first_name} {safe_last_name}"),
            _row("Email", safe_email),
            _row("Événement", safe_event_title),
            _row("Nombre de billets", str(ticket_count)),
        ],
        # Un billet par QR code, chacun avec un Content-ID unique (qrcode1, qrcode2…)
        TICKET_EYEBROW="Billet événement",
        TICKET_TITLE=safe_event_title,
        TICKETS=[
            {
                "TICKET_LABEL": f"Billet {i} / {ticket_count}",
                "CID": f"qrcode{i}",
                "TOKEN": token,
            }
            for i, token in enumerate(safe_qr_tokens, start=1)
        ],
        ALERT_KIND="danger",
        ALERT_TITLE="Consignes de sécurité importantes",
        ALERT_ITEMS=[{"TEXT": item} for item in (
            f"Vous disposez de <strong>{ticket_count} billets</strong>, chacun avec son propre QR code",
            "<strong>Ne partagez jamais un QR code</strong> avec qui que ce soit en dehors de son destinataire",
            "Chaque code est <strong>strictement personnel</strong> et identifie un participant de manière unique",
            "Toute personne en possession d'un code peut accéder à l'événement à la place du participant concerné",
            "Ne publiez pas ces billets sur les réseaux sociaux",
            "En cas de perte ou de vol, <strong>contactez-nous immédiatement</strong>",
        )],
        NOTE_END=(
            "Nous vous remercions pour votre confiance et restons à votre disposition "
            "pour toute question."
        ),
        SIGN_OFF="Cordialement,",
    )

    tokens_text = "\n".join(
        f"Billet {i}/{ticket_count} — code : {token}"
        for i, token in enumerate(qr_tokens, start=1)
    )

    text_content = f"""Athena Event - Confirmation d'inscription

Bonjour {first_name} {last_name},

Nous avons le plaisir de confirmer votre inscription pour {ticket_count} billets
à l'événement suivant.

DÉTAILS DE L'INSCRIPTION

Participant      : {first_name} {last_name}
Email            : {email}
Événement        : {event_title}
Date             : {event_start}
Lieu             : {event_location}
Nombre de billets: {ticket_count}

VOS BILLETS
{tokens_text}

CONSIGNES DE SÉCURITÉ :
- Vous disposez de {ticket_count} billets, chacun avec son propre QR code
- Ne partagez jamais un QR code avec qui que ce soit en dehors de son destinataire
- Chaque code est strictement personnel et identifie un participant de manière unique
- Toute personne en possession d'un code peut accéder à l'événement à la place du participant concerné
- Ne publiez pas ces billets sur les réseaux sociaux
- En cas de perte ou de vol, contactez-nous immédiatement

Cordialement,
L'équipe Athena Event

---
+261 38 32 046 13
sales@athena-event.com
www.athena-event.com

© {datetime.now().year} Athena Event by Clearmind Analytics
Antananarivo, Madagascar"""

    # ── Construction MIME — structure : related > alternative + N images CID ──
    msg             = MIMEMultipart('related')
    msg_alternative = MIMEMultipart('alternative')
    msg.attach(msg_alternative)

    msg_alternative.attach(MIMEText(text_content, 'plain', 'utf-8'))
    msg_alternative.attach(MIMEText(html_content, 'html',  'utf-8'))

    for i, qr_base64 in enumerate(qr_base64_list, start=1):
        qr_bytes = base64.b64decode(qr_base64)
        qr_image = MIMEBase('image', 'png')
        qr_image.set_payload(qr_bytes)
        encoders.encode_base64(qr_image)
        qr_image.add_header('Content-ID', f'<qrcode{i}>')
        qr_image.add_header('Content-Disposition', 'inline', filename=f'qrcode{i}.png')
        msg.attach(qr_image)

    msg.attach(_load_logo_image_part())

    msg['Subject']    = f"Confirmation de vos {ticket_count} billets — {event_title}"
    msg['From']       = f"Athena Event <{SMTP_USER}>"
    msg['To']         = email
    msg['Reply-To']   = SMTP_USER
    msg['Message-ID'] = f"<{registration_id}@athena-event.com>"
    msg['X-Mailer']   = "Athena Event Platform"

    try:
        with smtplib.SMTP(SMTP_HOST, 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logging.info(f"Email multi-billets ({ticket_count}) envoyé à {email}")
    except Exception as e:
        logging.error(f"Erreur envoi email multi-billets : {e}")
        raise