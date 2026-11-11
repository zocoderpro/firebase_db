import os
import html
import mimetypes

from pathlib import Path
from datetime import datetime
from email.message import EmailMessage
from email.policy import SMTP


BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_PATH = BASE_DIR / "templates" / "facture_gem_event.html"
ASSETS_DIR = BASE_DIR / "assets" / "gem2026"

PREHEADER_FILLER = "&nbsp;&#8204;" * 60

# Correspondance entre les CID du HTML et les fichiers images
INLINE_IMAGES = {
    "gembanner": "gembanner.jpeg",
    "gembanner_mobile": "gembanner_mobile.jpeg",
    "gembannerpartenaires": "bandeaupartenaires.png",
}


def render_facture_gem_event(first_name: str) -> str:
    """Charge le template HTML et injecte les variables."""

    with open(TEMPLATE_PATH, "r", encoding="utf-8") as file:
        template = file.read()

    context = {
        "DOC_TITLE": "Facture GEM CONNECT & RE-GEM 2026",
        "FIRST_NAME": html.escape(first_name or ""),
        "SIGN_OFF": "Bien cordialement,",
        "PREHEADER": "Votre facture est disponible en pièce jointe.",
        "PREHEADER_FILLER": PREHEADER_FILLER,
        "YEAR": str(datetime.now().year),
    }

    for key, value in context.items():
        template = template.replace(
            f"{{{{{key}}}}}",
            value
        )

    return template


def build_facture_gem_event_email(
    email: str,
    first_name: str,
    last_name: str,
    event_title: str,
    total_amount: float,
    raison_sociale: str,
    facture_pdf_path: str,
    adress: str = None,
    nif: str = None,
    stat: str = None,
) -> EmailMessage:
    """
    Construit un email GEM prêt pour SMTP.

    Contenu :
    - Version texte
    - Version HTML
    - Images inline avec CID
    - Facture PDF en pièce jointe

    Aucun envoi SMTP ici.
    """

    msg = EmailMessage(policy=SMTP)

    # En-têtes
    msg["Subject"] = f"Votre facture - {event_title}"
    msg["From"] = os.environ.get(
        "SMTP_USER",
        "noreply@athena-event.com"
    )
    msg["To"] = email

    # Version texte
    msg.set_content(
        f"Bonjour {first_name},\n\n"
        "Veuillez trouver en pièce jointe votre facture.\n\n"
        "Nous vous remercions pour votre confiance.\n\n"
        "L'équipe du GEM"
    )

    # Version HTML
    html_content = render_facture_gem_event(first_name)

    msg.add_alternative(
        html_content,
        subtype="html"
    )

    html_part = msg.get_payload()[-1]

    # Images inline
    for cid, filename in INLINE_IMAGES.items():

        image_path = ASSETS_DIR / filename

        if not image_path.is_file():
            raise FileNotFoundError(
                f"Image introuvable : {image_path}"
            )

        mime_type, _ = mimetypes.guess_type(image_path)

        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError(f"Type d'image invalide : {filename}")

        maintype, subtype = mime_type.split("/", 1)

        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        html_part.add_related(
            image_data,
            maintype=maintype,
            subtype=subtype,
            cid=f"<{cid}>",
            filename=filename,
            disposition="inline"
        )

    # Facture PDF en pièce jointe
    pdf_path = Path(facture_pdf_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"Facture PDF introuvable : {pdf_path}"
        )

    with open(pdf_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    msg.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=pdf_path.name
    )

    return msg