"""Email senders — logique métier de chaque type d'email."""

import base64
import html
import logging
import os
import io
import qrcode
from datetime import datetime
from email.mime.image import MIMEImage

from sender import _build_message, _send_email
from templates_handler import render_fragment

# ──────────────────────────────────────────────────────────────
# CHEMINS & CONSTANTES
# ──────────────────────────────────────────────────────────────
_PDF_PATH = os.path.join(os.path.dirname(__file__), "assets", "programme_rjp_complet.pdf")
_RJP_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "rjp2026")

# Contenus inline (au lieu de fichiers externes)
_INTRO_TEXT = """<p style="margin:0 0 16px 0;">Dans le cadre de la <strong>Rentrée du Jeune Patronat 2026</strong>, placée sous le thème <em>« Passage à l'échelle »</em>, nous avons le plaisir de mettre à la disposition de votre institution, en sa qualité de <strong>partenaire institutionnel</strong>, <strong>{total_invitations} invitations supplémentaires</strong>.</p>

<p style="margin:0 0 16px 0;">L'invitation officielle destinée au Président de votre institution fait l'objet d'un envoi distinct.</p>

<p style="margin:0 0 16px 0;">Vous recevrez ainsi, par emails séparés, les <strong>{total_invitations} QR codes</strong> que vous pourrez transmettre aux représentants ou invités de votre choix. Ils pourront simplement présenter leur QR code à leur arrivée.</p>

<p style="margin:0 0 16px 0;"><strong>Avantage partenaire :</strong> Si vous souhaitez inviter davantage de personnes, une <strong>réduction de 20 %</strong> vous est accordée sur les invitations supplémentaires en tant que partenaire institutionnel.</p>

<p style="margin:0 0 0 0;">Nous vous remercions pour votre engagement à nos côtés et nous réjouissons de vous accueillir à la Rentrée du Jeune Patronat 2026.</p>"""

_SINGULAR_TEXT = """<p style="margin:0 0 16px 0;">Dans le cadre de la <strong>Rentrée du Jeune Patronat 2026</strong>, nous vous transmettons ci-joint votre <strong>QR code d'accès</strong>.</p>

<p style="margin:0 0 16px 0;">Nous vous prions de bien vouloir le présenter à votre arrivée afin de faciliter votre accès à l'événement.</p>

<p style="margin:0 0 0 0;">Au plaisir de vous accueillir à la <strong>Rentrée du Jeune Patronat 2026</strong>.</p>"""

_BITLY_URL = "https://bit.ly/3VcDPvW"
_RJP2026_EVENT_TITLE = "Rentrée du Jeune Patronat 2026"


# ──────────────────────────────────────────────────────────────
# HELPERS COMMUNS
# ──────────────────────────────────────────────────────────────

def _load_pdf_attachment():
    if not os.path.exists(_PDF_PATH):
        logging.warning(f"PDF introuvable: {_PDF_PATH}")
        return None
    with open(_PDF_PATH, "rb") as f:
        return ("Programme RJP_Complet.pdf", f.read(), "pdf")


def _load_rjp_jpm_image_bytes():
    path = os.path.join(_RJP_ASSET_DIR, "jpm.png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def _load_intro_text(total_invitations=5):
    return _INTRO_TEXT.format(total_invitations=total_invitations)


def _load_singular_text():
    return _SINGULAR_TEXT


def _make_qr_bytes(data: str) -> bytes:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


_RJP2026_EVENT_TITLE = "Rentrée du Jeune Patronat 2026"
_BITLY_URL = "https://bit.ly/3VcDPvW"


# ──────────────────────────────────────────────────────────────
# EMAIL STANDARD (inchangé)
# ──────────────────────────────────────────────────────────────

def send_rjp_invitation(
    email: str,
    first_name: str,
    last_name: str,
    qr_token: str = "",
    fonction: str = "",
    entite: str = "",
    genre: str = "H",
):
    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_fonction = html.escape(fonction or "")
    safe_entite = html.escape(entite or "")
    safe_qr_token = html.escape(qr_token or "")

    genre = (genre or "").strip().upper()
    if genre == "F":
        salutation = f"Madame {safe_last_name} {safe_first_name}"
    elif genre == "H":
        salutation = f"Monsieur {safe_last_name} {safe_first_name}"
    else:
        salutation = f"Madame/Monsieur {safe_last_name} {safe_first_name}"

    qr_bytes = _make_qr_bytes(qr_token or email)

    if safe_fonction and safe_entite:
        intro = f"{safe_fonction}, {safe_entite}"
    elif safe_fonction:
        intro = safe_fonction
    elif safe_entite:
        intro = safe_entite
    else:
        intro = ""

    titre_politesse = "Madame" if genre == "F" else ("Monsieur" if genre == "H" else "Madame/Monsieur")
    formule_politesse = f"Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, {titre_politesse}, l'expression de nos salutations distinguées."

    template_path = os.path.join(os.path.dirname(__file__), "templates", "invitation_simple.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    envelope_open = render_fragment("envelope_open", PREHEADER="Invitation à la Rentrée du Jeune Patronat 2026", PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    html_content = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{INTRO}}": intro,
        "{{QR_LABEL}}": "Votre QR code d'accès",
        "{{QR_CID}}": "qrcode",
        "{{QR_TOKEN}}": safe_qr_token,
        "{{SIGN_OFF}}": formule_politesse,
        "{{YEAR}}": str(datetime.now().year),
    }
    for k, v in replacements.items():
        html_content = html_content.replace(k, v)

    texte_politesse = f"Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, {titre_politesse}, l'expression de nos salutations distinguées."

    text_content = f"""RJP via Athena Event – Invitation

{salutation}
{intro}

Nous avons l'honneur de vous inviter à la Rentrée du Jeune Patronat 2026, placée sous le thème « Passage à l'échelle ».

Cet événement marquera le lancement officiel de cette nouvelle saison et sera l'occasion de partager un moment privilégié d'échanges, de réflexion et de networking avec l'ensemble de notre écosystème.

Vous trouverez ci-joint le programme complet de la Rentrée du Jeune Patronat 2026.

Pour faciliter votre accès à l'événement, nous vous prions de bien vouloir présenter le QR code joint à cette invitation lors de votre arrivée.

{texte_politesse}

Bien cordialement,

---
Athena Event by Clearmind Analytics
Antananarivo, Madagascar
athena-event.com
"""

    pdf_attachment = _load_pdf_attachment()
    attachments = [pdf_attachment] if pdf_attachment else []

    qr_bytes = _make_qr_bytes(qr_token or email)
    extra_images = [("qrcode", qr_bytes, "png")]
    jpm_bytes = _load_rjp_jpm_image_bytes()
    if jpm_bytes:
        extra_images.append(("rjp_jpm", jpm_bytes, "png"))

    msg = _build_message(
        subject=f"Invitation – {_RJP2026_EVENT_TITLE}",
        to_addr=email,
        text_content=text_content,
        html_content=html_content,
        extra_images=extra_images,
        attach_logo=False,
        from_name="RJP via Athena Event",
        attachments=attachments,
    )
    _send_email(msg)
    logging.info(f"Email d'invitation RJP envoyé à {email}")


# ──────────────────────────────────────────────────────────────
# BATCH : 1 INTRODUCTION + 5 INVITATIONS SINGULIÈRES
# ──────────────────────────────────────────────────────────────

def send_rjp_invitation_batch(
    email: str,
    first_name: str,
    last_name: str,
    qr_tokens: list,   # 5 tokens
    qr_codes: list,    # 5 contenus QR
    fonction: str = "",
    entite: str = "",
    genre: str = "H",
    maps_link: str = "https://maps.app.goo.gl/example",  # lien Google Maps par défaut
):
    """Envoie N+1 emails séquentiels :
    1. Introduction (sans pièces jointes)
    2..N+1. N invitations singulières avec QR, PDF complet, lien Google Maps
    Le nombre d'invitations = len(qr_codes) (ou len(qr_tokens) si qr_codes vide).
    """
    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_fonction = html.escape(fonction or "")
    safe_entite = html.escape(entite or "")

    genre = (genre or "").strip().upper()
    if genre == "F":
        salutation = f"Madame {safe_last_name} {safe_first_name}"
    elif genre == "H":
        salutation = f"Monsieur {safe_last_name} {safe_first_name}"
    else:
        salutation = f"Madame/Monsieur {safe_last_name} {safe_first_name}"

    # Pour les emails singuliers : salutation simple "Bonjour,"
    singular_salutation = "Bonjour,"

    if safe_fonction and safe_entite:
        intro = f"{safe_fonction}, {safe_entite}"
    elif safe_fonction:
        intro = safe_fonction
    elif safe_entite:
        intro = safe_entite
    else:
        intro = ""

    titre_politesse = "Madame" if genre == "F" else ("Monsieur" if genre == "H" else "Madame/Monsieur")
    formule_politesse = f"Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, {titre_politesse}, l'expression de nos salutations distinguées."

    # Nombre d'invitations = nombre de qrCodes (fallback sur qrTokens)
    total_invitations = len(qr_codes) if qr_codes else len(qr_tokens)

    intro_text_raw = _load_intro_text(total_invitations)
    singular_text_raw = _load_singular_text()

    envelope_open = render_fragment("envelope_open", PREHEADER="Invitation à la Rentrée du Jeune Patronat 2026", PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    template_path = os.path.join(os.path.dirname(__file__), "templates", "invitation_batch.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    pdf_attachment = _load_pdf_attachment()
    jpm_bytes = _load_rjp_jpm_image_bytes()

    # ═══════════════════════════════════════════════════════════
    # EMAIL 1 : INTRODUCTION (sans pièces jointes)
    # ═══════════════════════════════════════════════════════════
    intro_html = _render_batch_html(
        html_template, envelope_open, envelope_close,
        salutation, intro,
        intro_text_raw,
        qr_token=None, qr_cid=None,
        formule_politesse=formule_politesse,
        sign_off=f"Bien cordialement,<br/><br/>L'équipe de la Rentrée du Jeune Patronat 2026",
        show_pdf_note=False,
        show_qr_alert=False,
        show_qr_block=False,
        show_bitly=False,
        is_intro_email=True,
    )

    intro_text = f"""RJP via Athena Event – Introduction

{salutation}
{intro}

Dans le cadre de la Rentrée du Jeune Patronat 2026, placée sous le thème « Passage à l'échelle », nous avons le plaisir de mettre à la disposition de votre institution, en sa qualité de partenaire institutionnel, {total_invitations} invitations supplémentaires.

L'invitation officielle destinée au Président de votre institution fait l'objet d'un envoi distinct.

Vous recevrez ainsi, par emails séparés, les {total_invitations} QR codes que vous pourrez transmettre aux représentants ou invités de votre choix. Ils pourront simplement présenter leur QR code à leur arrivée.

Avantage partenaire : Si vous souhaitez inviter davantage de personnes, une réduction de 20 % vous est accordée sur les invitations supplémentaires en tant que partenaire institutionnel.

Nous vous remercions pour votre engagement à nos côtés et nous réjouissons de vous accueillir à la Rentrée du Jeune Patronat 2026.

Bien cordialement,
L'équipe de la Rentrée du Jeune Patronat 2026

---
Athena Event by Clearmind Analytics
Antananarivo, Madagascar
athena-event.com"""

    extra_images = []
    if jpm_bytes:
        extra_images.append(("rjp_jpm", jpm_bytes, "png"))

    _send_email(_build_message(
        subject=f"Rentrée du Jeune Patronat 2026 – Vos {total_invitations} invitations",
        to_addr=email,
        text_content=intro_text,
        html_content=intro_html,
        extra_images=extra_images,
        attach_logo=False,
        from_name="RJP via Athena Event",
        attachments=[],
    ))
    logging.info(f"Email introduction RJP envoyé à {email}")

    # ═══════════════════════════════════════════════════════════
    # EMAILS 2..N+1 : N INVITATIONS SINGULIÈRES (N = nombre de qrCodes)
    # ═══════════════════════════════════════════════════════════
    for i in range(total_invitations):
        qr_token = qr_tokens[i] if i < len(qr_tokens) else ""
        qr_code = qr_codes[i] if i < len(qr_codes) else ""
        safe_qr_token = html.escape(qr_token or "")
        qr_code_data = qr_code or qr_token

        qr_bytes = _make_qr_bytes(qr_code_data)
        safe_qr_token = html.escape(qr_token or "")

        singular_html = _render_batch_html(
            html_template, envelope_open, envelope_close,
            singular_salutation, "",  # salutation simple, pas d'intro fonction/entité
            singular_text_raw,
            qr_token=html.escape(qr_token),
            qr_cid="qrcode",
            formule_politesse=formule_politesse,
            sign_off=f"Bien cordialement,<br/><br/>L'équipe de la Rentrée du Jeune Patronat 2026",
            show_pdf_note=True,
            show_qr_alert=True,
            show_qr_block=True,
            show_bitly=True,
            is_intro_email=False,
            maps_link=maps_link,
        )

        singular_text = f"""RJP via Athena Event – Invitation {i+1}/{total_invitations}

{singular_salutation}

Dans le cadre de la Rentrée du Jeune Patronat 2026, nous vous transmettons ci-joint votre QR code d'accès.

Nous vous prions de bien vouloir le présenter à votre arrivée afin de faciliter votre accès à l'événement.

Au plaisir de vous accueillir à la Rentrée du Jeune Patronat 2026.

Lieu : {maps_link}

Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, {titre_politesse}, l'expression de nos salutations distinguées.

Bien cordialement,
L'équipe de la Rentrée du Jeune Patronat 2026

---
Athena Event by Clearmind Analytics
Antananarivo, Madagascar
athena-event.com"""

        qr_bytes = _make_qr_bytes(qr_code_data)
        extra_images = [("qrcode", qr_bytes, "png")]
        if jpm_bytes:
            extra_images.append(("rjp_jpm", jpm_bytes, "png"))

        pdf_attach = _load_pdf_attachment()
        attachments = [pdf_attach] if pdf_attach else []

        _send_email(_build_message(
            subject=f"Votre QR code d'accès – Rentrée du Jeune Patronat 2026 ({i+1}/{total_invitations})",
            to_addr=email,
            text_content=singular_text,
            html_content=singular_html,
            extra_images=[("qrcode", qr_bytes, "png")] + ([("rjp_jpm", jpm_bytes, "png")] if jpm_bytes else []),
            attach_logo=False,
            from_name="RJP via Athena Event",
            attachments=[pdf_attach] if pdf_attach else [],
        ))
        logging.info(f"Email invitation singulière {i+1}/{total_invitations} RJP envoyé à {email}")


def _render_batch_html(
    html_template, envelope_open, envelope_close,
    salutation, intro, body_text,
    qr_token, qr_cid,
    formule_politesse, sign_off,
    show_pdf_note, show_qr_alert, show_qr_block, show_bitly,
    is_intro_email=False,
    maps_link="https://maps.app.goo.gl/example",
):
    """Rendu HTML pour un email du batch (utilise le template unique invitation_batch.html)."""
    envelope_open_html = render_fragment("envelope_open", PREHEADER=body_text[:80] if body_text else "Rentrée du Jeune Patronat 2026", PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close_html = render_fragment("envelope_close", YEAR=datetime.now().year)

    # INTRO_BLOCK : pour l'email d'intro, on affiche l'intro (fonction/entité)
    if is_intro_email and intro:
        intro_block = f'<p style="margin:0 0 24px 0;font-family:Arial,sans-serif;font-size:15px;color:#3b4453;line-height:1.75;">{intro}</p>'
    else:
        intro_block = ""

    # QR_BLOCK : seulement pour emails singuliers
    if show_qr_block and qr_token and qr_cid:
        qr_block = f'''<tr>
            <td class="body-td" style="padding:0 40px;">
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin:28px 0;">
                <tr>
                  <td class="qr-td" align="center" style="background-color:#122748;border-radius:12px;padding:28px 24px;text-align:center;">
                    <p style="margin:0 0 6px 0;font-family:Arial,sans-serif;font-size:10px;font-weight:700;color:#c7a253;text-transform:uppercase;letter-spacing:3px;">
                      Votre QR code d'accès
                    </p>
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center">
                      <tr><td style="width:36px;height:2px;background-color:#c7a253;font-size:0;line-height:2px;">&nbsp;</td></tr>
                    </table>
                    <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin-top:16px;">
                      <tr>
                        <td class="qr-frame-td" style="background-color:#ffffff;border-radius:10px;padding:14px;border:1px solid #c7a253;">
                          <img class="qr-img" src="cid:{qr_cid}" alt="QR Code d'accès" width="190" height="190" style="width:190px;height:190px;display:block;" />
                        </td>
                      </tr>
                    </table>
                    <p style="margin:16px 0 0 0;font-family:Arial,sans-serif;font-size:13px;color:#d7deea;line-height:1.6;">
                      {qr_token}
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>'''
    else:
        qr_block = ""

    # MAPS_BLOCK : lien Google Maps (remplace bitly)
    if show_bitly:
        maps_block = f'''<tr>
            <td class="body-td" style="padding:0 40px;">
              <p style="margin:20px 0 0 0;font-family:Arial,sans-serif;font-size:15px;color:#3b4453;line-height:1.6;">
                Lieu : <a href="{maps_link}" style="color:#4F1FA8;text-decoration:underline;">{maps_link}</a>
              </p>
            </td>
          </tr>'''
    else:
        maps_block = ""

    # PDF_NOTE_BLOCK : seulement pour emails singuliers
    if show_pdf_note:
        pdf_note_block = '''<tr>
            <td class="body-td" style="padding:0 40px;">
              <p style="margin:20px 0 0 0;font-family:Arial,sans-serif;font-size:15px;color:#3b4453;line-height:1.6;">
                Vous trouverez ci-joint le programme complet de la Rentrée du Jeune Patronat 2026.
              </p>
            </td>
          </tr>'''
    else:
        pdf_note_block = ""

    html = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{INTRO_BLOCK}}": intro_block,
        "{{BODY_TEXT}}": body_text,
        "{{QR_BLOCK}}": qr_block,
        "{{BITLY_BLOCK}}": maps_block,
        "{{PDF_NOTE_BLOCK}}": pdf_note_block,
        "{{SIGN_OFF}}": sign_off,
        "{{YEAR}}": str(datetime.now().year),
    }

    for k, v in replacements.items():
        html = html.replace(k, v)
    return html