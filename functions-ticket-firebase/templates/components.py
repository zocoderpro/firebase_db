# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ZONE DESIGN — COMPOSANTS VISUELS                          ║
# ║                                                              ║
# ║   Identité Athena Event : navy #163057 / doré #c7a253,      ║
# ║   titres Georgia, corps Arial.                               ║
# ║                                                              ║
# ║   Le HTML de chaque composant vit dans un fichier dédié      ║
# ║   sous templates/fragments/*.html — ce module ne fait        ║
# ║   qu'assembler les variables et les blocs répétés/optionnels.║
# ║                                                              ║
# ║   Pour modifier :                                            ║
# ║     • Logo / image hero    → config.py                      ║
# ║     • Couleurs, polices    → templates/fragments/envelope_open.html ║
# ║     • Structure du header  → templates/fragments/hero.html  ║
# ║     • Footer               → templates/fragments/footer.html║
# ║     • Cards, alertes       → templates/fragments/info_card.html, ║
# ║                              alert.html, security_card.html ║
# ║     • Bloc QR code         → templates/fragments/qr_block.html ║
# ║     • Contenu d'un email   → email_sender.py                ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

from datetime import datetime

from config import HERO_IMAGE_URL, LOGO_URL
from templates.base import _email_open, _email_close
from templates_handler import render_fragment


# ──────────────────────────────────────────────────────────────
# COMPOSANTS VISUELS
# ──────────────────────────────────────────────────────────────

def _hero(title: str, subtitle: str, email_type_label: str = "", hero_image_url: str = "") -> str:
    """
    Bandeau hero navy : logo + marque à gauche, badge doré à droite,
    filet doré, titre Georgia et sous-titre.

    email_type_label : texte affiché dans le badge en haut à droite du hero.
    hero_image_url   : image de fond personnalisée (ex: image de l'événement).
                       Si vide, utilise HERO_IMAGE_URL par défaut.
    """
    bg_url = hero_image_url or HERO_IMAGE_URL
    badge_col = render_fragment("hero_badge", EMAIL_TYPE_LABEL=email_type_label) if email_type_label else ""
    cols = 2 if email_type_label else 1

    return render_fragment(
        "hero",
        BG_URL=bg_url,
        LOGO_URL=LOGO_URL,
        BADGE_COL=badge_col,
        COLS=cols,
        TITLE=title,
        SUBTITLE=subtitle,
    )


def _body_open(greeting: str, intro: str) -> str:
    """Ouvre la zone de contenu : salutation + paragraphe d'introduction."""
    return render_fragment("body_open", GREETING=greeting, INTRO=intro)


def _body_close(sign_off: str = "Cordialement,") -> str:
    """Ferme la zone de contenu : filet doré + signature."""
    return render_fragment("body_close", SIGN_OFF=sign_off)


def _body_close_plain() -> str:
    """Ferme la zone de contenu SANS filet doré ni signature — utilisé quand un
    bloc pleine largeur (ex: _rjp2026_sponsors_footer()) doit s'intercaler
    avant la signature finale. À utiliser avec _body_reopen()."""
    return render_fragment("body_close_plain")


def _body_reopen() -> str:
    """Rouvre une zone de contenu au même padding que _body_open(), sans
    salutation ni intro — pour reprendre le texte indenté (ex: note de
    remerciement + signature) après un bloc pleine largeur inséré via
    _body_close_plain()."""
    return render_fragment("body_reopen")


def _info_card(rows_html: str, label: str = "DÉTAILS") -> str:
    """
    Carte blanche à liseré doré (même langage visuel que les cartes
    de mise en relation Athena).
    rows_html : lignes générées par _info_row()
    label     : titre de la card en petites capitales dorées
    """
    return render_fragment("info_card", LABEL=label, ROWS=rows_html)


def _info_row(icon: str, label: str, value: str) -> str:
    """
    Ligne d'information "Label : valeur".
    icon : conservé pour compatibilité — laisser vide de préférence
           (les emojis se rendent différemment selon les clients).
    """
    icon_cell = render_fragment("info_row_icon", ICON=icon) if icon else ""
    return render_fragment("info_row", ICON_CELL=icon_cell, LABEL=label, VALUE=value)


def _qr_block(qr_token: str = "", cid: str = "qrcode", ticket_label: str = "") -> str:
    """
    Bloc QR code centré sur fond navy profond.
    L'image est injectée via Content-ID (src="cid:{cid}") — pas une URL externe.

    cid          : Content-ID de l'image QR à référencer — permet d'assembler
                   plusieurs blocs QR dans un même email (un par billet).
    ticket_label : libellé affiché au-dessus du QR (ex: "Billet 1 / 3").
                   Vide → libellé générique par défaut.
    """
    label = ticket_label or "Votre code d'acc&#232;s personnel"
    return render_fragment("qr_block", LABEL=label, CID=cid, QR_TOKEN=qr_token)


def _security_card(items: list) -> str:
    """
    Card sécurité : fond rosé discret, puces assorties.
    items : liste de chaînes HTML décrivant chaque consigne.
    """
    rows_html = ""
    for item in items:
        rows_html += render_fragment("security_item", ITEM=item)
    return render_fragment("security_card", ITEMS=rows_html)


def _note(content: str) -> str:
    """Paragraphe de contenu libre entre deux blocs (ex: phrase de clôture)."""
    return render_fragment("note", CONTENT=content)


def _rjp2026_header() -> str:
    """
    En-tête organisateur RJP 2026 (dégradé + logo JPM) — remplace _hero() pour
    ce template ponctuel (template_type=True). Contenu 100% statique.
    """
    return render_fragment("rjp2026_header")


def _rjp2026_sponsors_footer() -> str:
    """
    Bloc sponsors/partenaires RJP 2026 (4 catégories : Or, Argent, RSE &
    Jeunesse, Amis du JPM) — placé en bas de l'email, après le corps du
    message, à la demande de l'organisateur (JPM). Contenu 100% statique,
    tous les logos en CID cid:rjp_*.
    """
    return render_fragment("rjp2026_sponsors_footer")


def _footer() -> str:
    """
    Pied de page navy : devise, contacts, copyright — centrés.
    """
    return render_fragment("footer", YEAR=datetime.now().year)


def _build_html(rows: str, preheader: str = "") -> str:
    """Assemble l'email complet : open + contenu + footer + close."""
    return _email_open(preheader) + rows + _footer() + _email_close()
