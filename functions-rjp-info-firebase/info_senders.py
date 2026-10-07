"""Email senders — email d'informations utiles RJP 2026 (8-9 octobre)."""
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
_RJP2026_EVENT_TITLE = "Rentrée du Jeune Patronat 2026"
_MAPS_LINK = "https://www.google.com/maps/place/LE+PATIO/@-18.9132406,47.5394938,942m/data=!3m1!1e3!4m9!3m8!1s0x21f07d09b37831e3:0x8832bf18c8e4cbd8!5m2!4m1!1i2!8m2!3d-18.9132406!4d47.5394938!16s%2Fg%2F11lxvqs8bl?entry=ttu&g_ep=EgoyMDI2MTAwNC4wIKXMDSoASAFQAw%3D%3D"
_PANELS_FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdl6Q94MR2xtfMSdx1vTWvGka1ONR3OyUyG3E9s_xUTouXbNw/viewform?usp=header"
_WHATSAPP_LINK = "https://chat.whatsapp.com/Dsj23q5yNWZ1Sz28YXn4ad?mode=gi_t"

# Contenu HTML inline
_INFO_BODY_HTML = f"""<p style="margin:0 0 16px 0;">Nous avons hâte de vous accueillir à la <strong>RJP 2026</strong>, les <strong>8 et 9 octobre</strong> au <strong>Patio Ivato</strong>.</p>

<p style="margin:0 0 16px 0;">Vous trouverez ici la localisation du Patio Ivato : <a href="{_MAPS_LINK}" style="color:#4F1FA8;text-decoration:underline;">Ouvrir dans Google Maps</a></p>

<p style="margin:0 0 16px 0;">Vous trouverez en <a href="https://athena-event.com/pgm/rjp-26" style="color:#4F1FA8;text-decoration:underline;">pièces jointes</a> le <strong>programme complet</strong> et le <strong>plan du lieu</strong> pour préparer votre venue.</p>

<p style="margin:0 0 16px 0;">Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au <strong>dernier étage</strong>.</p>

<p style="margin:0 0 16px 0;">Le retrait de vos badges se fait le <strong>jour J</strong>. Vous trouverez à l'entrée de l'espace RJP un check-in qui vous permettra de retirer votre badge en présentant votre <strong>QR Code</strong> ou votre <strong>adresse mail</strong>.</p>

<p style="margin:0 0 16px 0;">Sont inclus dans votre pass toute la restauration : cocktails, vin de bienvenue, viennoiserie au petit déjeuner, lunchbox pour le déjeuner et cocktail de clôture. Vous trouverez sur place de quoi vous rafraîchir auprès des stands de boissons (payant).</p>

<p style="margin:0 0 16px 0;">Pour participer aux sondages en direct pendant l'événement, assurez-vous de disposer d'une connexion Internet sur votre téléphone. Si vous souhaitez prendre part à la <strong>Battle IA du Jour 2</strong>, apportez un ordinateur portable chargé et son chargeur.</p>

<p style="margin:0 0 16px 0;">Pour le Jour 2, choisissez dès maintenant les panels auxquels vous souhaitez assister via ce formulaire :<br/>
<a href="{_PANELS_FORM_LINK}" style="color:#4F1FA8;text-decoration:underline;">{_PANELS_FORM_LINK}</a></p>

<p style="margin:0 0 16px 0;">Vous ne pourrez pas assister à toutes les masterclass le 9 octobre : pas de panique, un lien Drive vous sera communiqué a posteriori pour visionner les replay et recevoir les documents des intervenants.</p>

<p style="margin:0 0 0 0;">Pour toute question avant l'événement : <a href="tel:+261340410506" style="color:#4F1FA8;text-decoration:underline;">+261 34 04 105 06</a></p>"""


def _load_rjp_jpm_image_bytes():
    path = os.path.join(_RJP_ASSET_DIR, "jpm.png")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def send_rjp_info(
    email: str,
):
    """Envoie l'email d'informations utiles RJP 2026 (8-9 octobre)."""

    salutation = "Bonjour,"

    subject = f"RJP 2026 : Toutes les informations utiles pour les 8 et 9 octobre"

    formule_politesse = "Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, Madame/Monsieur, l'expression de nos salutations distinguées."

    # Rendu HTML
    template_path = os.path.join(os.path.dirname(__file__), "templates", "info.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    envelope_open = render_fragment("envelope_open", PREHEADER=subject, PREHEADER_FILLER="&nbsp;" * 200)
    envelope_close = render_fragment("envelope_close", YEAR=datetime.now().year)

    html_content = html_template
    replacements = {
        "{{ENVELOPE_OPEN}}": envelope_open,
        "{{ENVELOPE_CLOSE}}": envelope_close,
        "{{GREETING}}": salutation,
        "{{BODY_TEXT}}": _INFO_BODY_HTML,
        "{{SIGN_OFF}}": formule_politesse,
        "{{YEAR}}": str(datetime.now().year),
    }
    for k, v in replacements.items():
        html_content = html_content.replace(k, v)

    # Version texte
    text_body = f"""RJP via Athena Event – Informations utiles

{salutation}

Nous avons hâte de vous accueillir à la RJP 2026, les 8 et 9 octobre au Patio Ivato.

Vous trouverez en pièces jointes le programme complet et le plan du lieu pour préparer votre venue.

Vous trouverez ici la localisation du Patio Ivato : {_MAPS_LINK}

Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au dernier étage.

Le retrait de vos badges se fait le jour J. Vous trouverez à l'entrée de l'espace RJP un check-in qui vous permettra de retirer votre badge en présentant votre QR Code ou votre adresse mail.

Sont inclus dans votre pass toute la restauration : cocktails, vin de bienvenue, viennoiserie au petit déjeuner, lunchbox pour le déjeuner et cocktail de clôture. Vous trouverez sur place de quoi vous rafraîchir auprès des stands de boissons (payant).

Pour participer aux sondages en direct pendant l'événement, assurez-vous de disposer d'une connexion Internet sur votre téléphone. Si vous souhaitez prendre part à la Battle IA du Jour 2, apportez un ordinateur portable chargé et son chargeur.

Pour le Jour 2, choisissez dès maintenant les panels auxquels vous souhaitez assister via ce formulaire :
{_PANELS_FORM_LINK}

Pour recevoir les actualités et rappels de la RJP directement sur votre téléphone, vous pouvez rejoindre notre espace WhatsApp :
{_WHATSAPP_LINK}

Vous ne pourrez pas assister à toutes les masterclass le 9 octobre : pas de panique, un lien Drive vous sera communiqué a posteriori pour visionner les replay et recevoir les documents des intervenants.

Pour toute question avant l'événement : +261 34 04 105 06

À très bientôt,
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

    msg = _build_message(
        subject=subject,
        to_addr=email,
        text_content=text_body,
        html_content=html_content,
        extra_images=extra_images,
        attach_logo=False,
        from_name="RJP via Athena Event",
        attachments=[],
    )

    _send_email(msg)
    logging.info(f"Email d'informations RJP envoyé à {email}")
