# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU DE L'EMAIL — CONFIRMATION DE PRÉSENCE (RJP 2026)   ║
# ║                                                              ║
# ║   Template figé, propre à l'événement (co-brandé JPM) :      ║
# ║   bandeau RJP 2026 + sponsors, textes et liens en dur.       ║
# ║                                                              ║
# ║   Pour modifier les textes → send_rjp_email_confirmation()   ║
# ║   ci-dessous.                                                ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import html
import logging
import os

from config import (
    RJP_FROM_NAME,
    RJP_MAP_URL,
    RJP_PHONE,
    RJP_SUBJECT,
    RJP_WHATSAPP_URL,
    SMTP_USER,
)
from sender import _build_message, _send_email
from templates.components import (
    _rjp2026_header,
    _rjp2026_sponsors_footer,
    _body_open,
    _body_close,
    _body_close_plain,
    _body_reopen,
    _info_card,
    _info_row,
    _note,
    _cta_button,
    _build_html,
)

# Bandeau RJP 2026 — logo organisateur (JPM) + 12 sponsors, tous en CID.
# Meme mecanisme que functions-email-firebase/email_senders.py::send_event_voucher.
_RJP2026_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "rjp2026")
_RJP2026_IMAGES = [
    ("rjp_jpm", "jpm.png"),
    # ("rjp_bni", "bni.png"),
    # ("rjp_pamf", "pamf.png"),
    # ("rjp_acep", "acep.png"),
    # ("rjp_soredim", "soredim.png"),
    # ("rjp_sobatra", "sobatra.png"),
    # ("rjp_orca", "orca.png"),
    # ("rjp_bmoi", "bmoi.png"),
    # ("rjp_logia", "logia.jpg"),
    # ("rjp_total_energie", "total_energie.png"),
    # ("rjp_venture_capital", "venture_capital.jpg"),
    # ("rjp_wellcom", "wellcom.jpg"),
    # ("rjp_sanlam_allianz", "sanlam_allianz.png"),
]


def _load_rjp2026_images() -> list:
    """Charge les images du bandeau RJP 2026 (logo JPM + sponsors) en tuples
    (cid, bytes, subtype) — passés à _build_message(extra_images=...)."""
    images = []
    for cid, filename in _RJP2026_IMAGES:
        subtype = "jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "png"
        with open(os.path.join(_RJP2026_ASSET_DIR, filename), "rb") as f:
            images.append((cid, f.read(), subtype))
    return images


def send_rjp_email_confirmation(recipients, name: str = None, subject: str = None, attachments: list = None) -> None:
    """
    Envoie l'email "Confirmez votre présence" aux participants inscrits
    à la Rentrée du Jeune Patronat 2026.

    Parametres :
      recipients  : str (un destinataire) ou list[str] (plusieurs)
      name        : optionnel — nom du destinataire pour la salutation
                    ("Bonjour Jean,"). Si absent, salutation neutre "Bonjour,".
      subject     : optionnel — sinon RJP_SUBJECT (config.py)
      attachments : optionnel — liste de tuples (filename, bytes) a joindre
                    (programme, plan du lieu). Fournis par le backend ou
                    charges via attachments.py.
    """
    if not recipients:
        raise ValueError("Champ obligatoire manquant: recipients")

    subject = subject or RJP_SUBJECT
    safe_map_url = html.escape(RJP_MAP_URL, quote=True)
    safe_whatsapp_url = html.escape(RJP_WHATSAPP_URL, quote=True)
    safe_phone = html.escape(RJP_PHONE)
    safe_name = html.escape(name.strip()) if name and name.strip() else ""
    greeting = f"Bonjour {safe_name}," if safe_name else "Bonjour,"

    # ── Informations pratiques ──
    info_rows = (
        _info_row("", "Accueil &amp; Networking", "<strong>17h</strong>")
        + _info_row("", "Début de l'événement", "<strong>18h</strong> (la sonnerie sera activée à l'heure)")
        + _info_row("", "Lieu", "Patio Ivato — dernier étage")
        + _info_row("", "Contact", f"<a href='tel:{safe_phone.replace(' ', '')}' "
                                   f"style='color:#163057;text-decoration:none;'>{safe_phone}</a>")
    )

    # ── Corps du message ──
    rows = (
        _rjp2026_header()
        + _body_open(
            greeting=greeting,
            intro=(
                "Nous avons hâte de vous retrouver le <strong>8 octobre</strong> "
                "au <strong>Patio Ivato</strong>."
            )
        )
        + _note(
            f"Vous trouverez ici la localisation du Patio Ivato : "
            f"<a href=\"{safe_map_url}\" style=\"color:#163057;\">"
            f"Ouvrir l'itinéraire dans Google Maps</a>."
        )
        + _note(
            "Des éléments de sécurité vous guideront vers le parking qui nous est "
            "dédié à la <strong>CCI</strong>, et il faudra marcher vers l'immeuble du "
            "Patio. Nous vous attendons au <strong>dernier étage</strong>."
        )
        + _note(
            "Si vous disposez d'un chauffeur, le véhicule peut vous déposer à "
            "l'entrée de l'immeuble, puis se diriger vers le parking."
        )
        + _note(
            "Si vous avez reçu une invitation personnalisée avec un QR code, il ne "
            "vous est pas nécessaire de passer par le check-in. Présentez directement "
            "votre QR code à l'entrée du <strong>SAS</strong>."
        )
        + _info_card(info_rows, label="Informations pratiques")
        + _note(
            "Le programme complet et le plan du lieu sont en <a href=\"https://athena-event.com/pgm/rjp-26\" style=\"color:#163057;\">pièces "
            "jointes</a>. Pensez à disposer d'une connexion Internet sur votre "
            "téléphone pour participer aux <strong>sondages en direct</strong>."
        )
        + _note(
            "Pour suivre les actualités de la RJP et <strong>confirmer votre présence</strong>, "
            "nous vous invitons à rejoindre notre groupe WhatsApp."
        )
        + _note(
            "<strong>Merci de bien vouloir confirmer votre présence ce mercredi 07 octobre </strong>"
            "<strong>avant 10h00, afin de nous permettre de finaliser l'organisation.</strong>"
        )
        + _cta_button(safe_whatsapp_url, "Rejoindre l'espace WhatsApp")
        + _body_close_plain()
        + _rjp2026_sponsors_footer()
        + _body_reopen()
        + _body_close("À très bientôt,")
    )

    text_content = (
        f"RJP 2026 — Confirmez votre présence\n\n"
        f"{greeting}\n\n"
        "Nous avons hâte de vous retrouver le 8 octobre au Patio Ivato.\n\n"
        f"Localisation du Patio Ivato : {RJP_MAP_URL}\n\n"
        "Des éléments de sécurité vous guideront vers le parking qui nous est dédié "
        "à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons "
        "au dernier étage.\n\n"
        "Si vous disposez d'un chauffeur, le véhicule peut vous déposer à l'entrée de "
        "l'immeuble, puis se diriger vers le parking.\n\n"
        "Si vous avez reçu une invitation personnalisée avec un QR code, il ne vous est "
        "pas nécessaire de passer par le check-in. Présentez directement votre QR code "
        "à l'entrée du SAS.\n\n"
        "INFORMATIONS PRATIQUES\n"
        "Accueil & Networking : 17h\n"
        "Début de l'événement : 18h (la sonnerie sera activée à l'heure)\n"
        "Lieu : Patio Ivato — dernier étage\n"
        f"Contact : {RJP_PHONE}\n\n"
        "Le programme complet et le plan du lieu sont en pièces jointes. Pensez à "
        "disposer d'une connexion Internet sur votre téléphone pour participer aux "
        "sondages en direct.\n\n"
        "Pour recevoir les actualités et rappels de la RJP directement sur votre "
        "téléphone, rejoignez notre espace WhatsApp :\n"
        f"{RJP_WHATSAPP_URL}\n\n"
        "Merci de bien vouloir confirmer votre présence ce mercredi 06 octobre "
        "avant 10h00, afin de nous permettre de finaliser l'organisation.\n\n"
        "À très bientôt,\n"
        "L'équipe Athena Event"
    )

    msg = _build_message(
        subject=subject,
        to_addr=recipients if isinstance(recipients, str) else ", ".join(recipients),
        text_content=text_content,
        html_content=_build_html(
            rows,
            preheader="RJP 2026 — Confirmez votre présence"
        ),
        reply_to=SMTP_USER,
        message_id="<rjp-email-confirmation@athena-event.com>",
        extra_images=_load_rjp2026_images(),
        attach_logo=False,
        from_name=RJP_FROM_NAME,
        attachments=attachments,
    )

    _send_email(msg)
    nb = 1 if isinstance(recipients, str) else len(recipients)
    logging.info(f"Email confirmation RJP 2026 envoyé à {nb} destinataire(s)")
