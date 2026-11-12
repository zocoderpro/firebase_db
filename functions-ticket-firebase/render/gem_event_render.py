import os
import html
import mimetypes

from pathlib import Path
from datetime import datetime
from email.message import EmailMessage
from email.policy import SMTP
import pymupdf
from datetime import datetime
from num2words import num2words



BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_EMAIL_HTML_PATH = BASE_DIR / "templates" / "facture_gem_event.html"
ASSETS_DIR = BASE_DIR / "assets" / "gem2026"
TEMPLATE_FACTURE_PDF_PATH = BASE_DIR / "templates" / "facture_gem_event_template.pdf"
PREHEADER_FILLER = "&nbsp;&#8204;" * 60
INLINE_IMAGES = {
    "gembanner": "gembanner.jpeg",
    "gembanner_mobile": "gembanner_mobile.jpeg",
    "gembannerpartenaires": "bandeaupartenaires.png",
}


def render_facture_gem_event(first_name: str) -> str:
    """Charge le template HTML et injecte les variables."""

    with open(TEMPLATE_EMAIL_HTML_PATH, "r", encoding="utf-8") as file:
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
    facture_num: str,
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
    pdf_path = Path(TEMPLATE_FACTURE_PDF_PATH)

    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"Facture PDF introuvable : {pdf_path}"
        )

    with open(pdf_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()

    pdf_data = replace_pdf_text(
        pdf_path=str(pdf_path),
        invoice_number=facture_num,
        raison_social=raison_sociale,
        adresse=adress or "",
        nif_company=nif or "",
        stat_company=stat or "",
        total_amount=total_amount,
        first_name_last_name=f"{first_name} {last_name.upper()}"
    )

    msg.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename="Facture_GEM_CONNECT_2026.pdf"
    )

    return msg


def replace_pdf_text(
    pdf_path: str,
    invoice_number: str,
    raison_social: str,
    adresse: str,
    nif_company: str,
    stat_company: str,
    total_amount: float,
    first_name_last_name: str,
) -> bytes:
    """Remplace des textes spécifiques dans le PDF."""

    doc = pymupdf.open(pdf_path)

    try:
        for page in doc:

            replacements = [
                {
                    "search": "ND N°330.2026 PART-GEM CONNECT & RE-GEM",
                    "replacement": f"ND N°{invoice_number}.2026 PART-GEM CONNECT & RE-GEM",
                    "fontsize": 11,
                    "color": (68 / 255, 114 / 255, 196 / 255),
                },
                {
                    "search": "{{data_now}}",
                    "replacement": datetime.now().strftime("%d %B %Y"),
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "{{raison_social}}",
                    "replacement": raison_social,
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "{{adresse}}",
                    "replacement": adresse,
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "{{nif_company}}",
                    "replacement": nif_company,
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "{{stat_company}}",
                    "replacement": stat_company,
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "{{amount_number}}",
                    "replacement": f"{total_amount:,.0f}".replace(",", " "),
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "({{amount_letter}})",
                    "replacement": f"({num2words(total_amount, lang='fr')})",
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
                {
                    "search": "{{first_name_last_name}}",
                    "replacement": first_name_last_name,
                    "fontsize": 11,
                    "color": (0, 0, 0),
                },
            ]

            for item in replacements:
                areas = page.search_for(item["search"])

                # Trier les occurrences de haut en bas
                areas.sort(key=lambda rect: (rect.y0, rect.x0))

                occurrence = 0

                if occurrence >= len(areas):
                    continue

                area = areas[occurrence]

                # Masquer l'ancien texte
                page.add_redact_annot(area, fill=(1, 1, 1))
                page.apply_redactions()

                # Insérer le nouveau texte
                page.insert_text(
                    (area.x0, area.y1 - 2),
                    item["replacement"],
                    fontsize=item["fontsize"],
                    color=item["color"]
                )

        return doc.tobytes()

    finally:
        doc.close()