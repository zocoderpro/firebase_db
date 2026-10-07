# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU DE L'EMAIL — CONFIRMATION DE PRÉSENCE (RJP 2026)   ║
# ║                                                              ║
# ║   Template figé, propre à l'événement (co-brandé JPM) :      ║
# ║   bandeau RJP 2026 + sponsors, textes et liens en dur.       ║
# ║                                                              ║
# ║   Pour modifier les textes → send_rjp_confirmation_j2()   ║
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


def send_rjp_confirmation_j2(recipients, name: str = None, subject: str = None, attachments: list = None) -> None:
    """
    Envoie l'email "Préparez votre venue le 9 octobre" aux participants inscrits
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
        _info_row("", "Accueil", "<strong>8h</strong>")
        + _info_row("", "Pour toute question avant l’événement", f"<strong>{safe_phone}</strong>")
    )

    # ── Corps du message ──
    rows = (
        _rjp2026_header()
        + _body_open(
            greeting=greeting,
            intro=(
                "Nous avons hâte de vous retrouver le <strong>9 octobre</strong> "
                "au <strong>Patio Ivato</strong>."
            )
        )
        + _note(
            "Vous trouverez en <a href=\"https://athena-event.com/pgm/rjp-26\" style=\"color:#163057;\">pièces jointes</a> le programme complet et le plan du lieu."
        )
        + _note(
            f"Vous trouverez ici la localisation du Patio Ivato : "
            f"<a href=\"{safe_map_url}\" style=\"color:#163057;\">"
            f"Ouvrir dans Google Maps</a>."
        )
        + _note(
            "Des éléments de sécurité vous guideront vers le parking qui nous est "
            "dédié à la <strong>CCI</strong>, et il faudra marcher vers l'immeuble du "
            "Patio. Nous vous attendons au <strong>dernier étage</strong>."
        )
        + _note(
            "Le retrait de vos badges se fait le jour J. "
            "Vous trouverez à l’entrée de l’espace RJP un check-in qui vous permettra de retirer votre "
            "badge en présentant votre QR Code ou votre adresse mail."
        )
        + _note(
            "Sont inclus dans votre pass toute la restauration: cocktails, vin de bienvenue, "
            "viennoiserie au petit déjeuner, lunchbox pour le déjeuner et cocktail de clôture. "
            "Vous trouverez sur place de quoi vous rafraîchir auprès des stands de boissons (payant)."
        )
        + _note(
            "Choisissez dès maintenant les panels auxquels vous souhaitez assister via ce formulaire : "
            "<a href=\"https://docs.google.com/forms/d/e/1FAIpQLSdl6Q94MR2xtfMSdx1vTWvGka1ONR3OyUyG3E9s_xUTouXbNw/viewform?usp=header\" style=\"color:#163057;\">"
            "Accéder au formulaire</a>."
        )
        + _note(
            "Pour participer aux sondages en direct, prévoyez une connexion Internet sur votre téléphone. "
            "Si vous souhaitez prendre part à la Battle IA, apportez un ordinateur portable chargé et son chargeur."
        )
        + _note(
            "Vous ne pourrez pas assister à toutes les masterclass le 9 octobre: pas de panique, "
            "un lien Drive vous sera communiqué a posteriori pour visionner les replay et recevoir "
            "les documents des intervenants."
        )
        + _note(
            "Tous les masterclass et les panels commenceront à l'heure."
        )
        + _note(
            "Pour recevoir les actualités et rappels de la RJP directement sur votre téléphone, "
            "vous pouvez rejoindre notre espace WhatsApp :"
        )
        + _cta_button(safe_whatsapp_url, "Rejoindre l'espace WhatsApp")
        + _info_card(info_rows, label="Informations pratiques")
        + _body_close_plain()
        + _rjp2026_sponsors_footer()
        + _body_reopen()
        + _body_close("À très bientôt,")
    )

    text_content = (
        f"RJP 2026 — Préparez votre venue le 9 octobre\n\n"
        f"{greeting}\n\n"
        "Nous avons hâte de vous retrouver le 9 octobre au Patio Ivato.\n\n"
        "Vous trouverez en pièces jointes le programme complet et le plan du lieu.\n\n"
        f"Localisation du Patio Ivato : {RJP_MAP_URL}\n\n"
        "Des éléments de sécurité vous guideront vers le parking qui nous est dédié "
        "à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons "
        "au dernier étage.\n\n"
        "Le retrait de vos badges se fait le jour J. Vous trouverez à l'entrée de "
        "l'espace RJP un check-in qui vous permettra de retirer votre badge en "
        "présentant votre QR Code ou votre adresse mail.\n\n"
        "Sont inclus dans votre pass toute la restauration: cocktails, vin de bienvenue, "
        "viennoiserie au petit déjeuner, lunchbox pour le déjeuner et cocktail de clôture. "
        "Vous trouverez sur place de quoi vous rafraîchir auprès des stands de boissons (payant).\n\n"
        "Choisissez dès maintenant les panels auxquels vous souhaitez assister via ce formulaire :\n"
        "https://docs.google.com/forms/d/e/1FAIpQLSdl6Q94MR2xtfMSdx1vTWvGka1ONR3OyUyG3E9s_xUTouXbNw/viewform?usp=header\n\n"
        "Pour participer aux sondages en direct, prévoyez une connexion Internet sur votre "
        "téléphone. Si vous souhaitez prendre part à la Battle IA, apportez un ordinateur "
        "portable chargé et son chargeur.\n\n"
        "Pour recevoir les actualités et rappels de la RJP directement sur votre téléphone, "
        "rejoignez notre espace WhatsApp :\n"
        f"{RJP_WHATSAPP_URL}\n\n"
        "Vous ne pourrez pas assister à toutes les masterclass le 9 octobre: pas de panique, "
        "un lien Drive vous sera communiqué a posteriori pour visionner les replay et recevoir "
        "les documents des intervenants.\n\n"
        "Tous les masterclass et les panels commenceront à l'heure.\n\n"
        "INFORMATIONS PRATIQUES\n"
        "Accueil : 8h\n"
        f"Pour toute question avant l'événement : {RJP_PHONE}\n\n"
        "À très bientôt,\n"
        "L'équipe RJP 2026"
    )

    msg = _build_message(
        subject=subject,
        to_addr=recipients if isinstance(recipients, str) else ", ".join(recipients),
        text_content=text_content,
        html_content=_build_html(
            rows,
            preheader="RJP 2026 — Préparez votre venue le 9 octobre"
        ),
        reply_to=SMTP_USER,
        message_id="<rjp-confirmation-j2@athena-event.com>",
        extra_images=_load_rjp2026_images(),
        attach_logo=False,
        from_name=RJP_FROM_NAME,
        attachments=attachments,
    )

    _send_email(msg)
    nb = 1 if isinstance(recipients, str) else len(recipients)
    logging.info(f"Email confirmation J2 RJP 2026 envoyé à {nb} destinataire(s)")
