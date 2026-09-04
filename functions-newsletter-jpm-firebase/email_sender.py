"""
Construction et envoi de la newsletter JPM (Rentree du Jeune Patronat) via SMTP.

Template 100% statique (templates/newsletter_rjp.html, aucune variable
{{...}} a remplacer) -- copie exacte du fichier fourni par l'utilisateur,
avec les 12 logos partenaires deja integres en base64 dans le HTML. Rien
d'autre a construire ici que le message MIME et la conversion base64 -> CID.
"""
import base64
import re
import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, NEWSLETTER_TEMPLATE_PATH


def send_newsletter_jpm_smtp(recipients, subject):
    """
    Envoie la newsletter JPM (template statique) a une liste de destinataires.
    Parametres : recipients (str ou list[str]), subject (str)
    """
    if not recipients:
        raise ValueError("Champ obligatoire manquant: recipients")
    if not subject:
        raise ValueError("Champ obligatoire manquant: subject")

    with open(NEWSLETTER_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    msg = MIMEMultipart("mixed")
    msg["From"] = formataddr(("Jeune Patronat de Madagascar via Athena Event", SMTP_USER))
    msg["To"] = recipients if isinstance(recipients, str) else ", ".join(recipients)
    msg["Subject"] = subject

    msg_related = MIMEMultipart("related")
    msg.attach(msg_related)

    msg_alternative = MIMEMultipart("alternative")
    msg_related.attach(msg_alternative)

    # Gmail/Outlook suppriment les images "data:" base64 du HTML : on les
    # convertit en pieces jointes inline referencees par cid: (les 12 logos
    # partenaires + l'image de l'evenement phare, deja embarques en base64
    # dans le template).
    html_content = _embed_base64_images(html_content, msg_related)

    html_part = MIMEText(html_content, "html", "utf-8")
    msg_alternative.attach(html_part)

    _send_via_smtp(msg, recipients)


def _embed_base64_images(html_content, related_part):
    """
    Identique a functions-brochure-firebase/email_sender.py::_embed_base64_images
    -- meme logique, dupliquee ici volontairement (pas d'import cross-dossier
    entre codebases Firebase independantes). Remplace chaque
    <img src="data:image/...;base64,..."> par une reference cid: et attache
    l'image en piece jointe inline (multipart/related). Necessaire car Gmail,
    Outlook et la plupart des clients mail bloquent les data: URI. Les images
    identiques sont dedupliquees (un seul CID).
    """
    # Suffixe unique par envoi : sans lui, Zoho met en cache les images par
    # Content-ID et peut afficher celles d'un ancien email.
    unique = uuid.uuid4().hex[:12]
    pattern = re.compile(r'data:image/([a-zA-Z0-9+.-]+);base64,([A-Za-z0-9+/=]+)')
    cid_map = {}  # payload base64 -> (cid, bytes, subtype)

    def _to_cid(match):
        subtype = match.group(1).lower()
        payload = match.group(2)
        if subtype == "svg+xml":
            return match.group(0)  # SVG non supporte par les clients mail
        entry = cid_map.get(payload)
        if entry is None:
            try:
                img_bytes = base64.b64decode(payload)
            except Exception:
                return match.group(0)
            cid = f"newsimg{len(cid_map) + 1}.{unique}@athena-event.com"
            cid_map[payload] = (cid, img_bytes, subtype)
        else:
            cid = entry[0]
        return f"cid:{cid}"

    new_html = pattern.sub(_to_cid, html_content)

    for cid, img_bytes, subtype in cid_map.values():
        mime_subtype = "jpeg" if subtype == "jpg" else subtype
        img_part = MIMEImage(img_bytes, _subtype=mime_subtype)
        img_part.add_header("Content-ID", f"<{cid}>")
        # Pas de Content-Disposition (RFC 2387) : dans un multipart/related
        # cet en-tete est superflu et pousse Zoho/Thunderbird a lister
        # l'image comme piece jointe (meme choix que functions-brochure-firebase).
        related_part.attach(img_part)

    if cid_map:
        print(f"{len(cid_map)} image(s) base64 converties en pieces jointes inline (CID)")
    return new_html


def _send_via_smtp(msg, recipients):
    """Envoie le message via SMTP."""
    try:
        print(f"Envoi newsletter JPM via {SMTP_HOST}:{SMTP_PORT}...")

        if not all([SMTP_USER, SMTP_PASSWORD]):
            raise ValueError("Configuration SMTP incomplete (SMTP_USER ou SMTP_PASSWORD manquants)")

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Newsletter JPM envoyee avec succes a {recipients}")
        return True

    except Exception as e:
        print(f"Erreur envoi SMTP: {e}")
        raise
