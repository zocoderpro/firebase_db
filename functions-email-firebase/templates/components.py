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
# ║     • Cards, boutons       → templates/fragments/info_card.html, ║
# ║                              cta_button.html, alert.html    ║
# ║     • Contenu d'un email   → email_senders.py               ║
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


def _cta_button(url: str, label: str) -> str:
    """
    Bouton call-to-action centré : navy, texte blanc, coins arrondis.
    Technique double :
      - VML v:roundrect pour Outlook Windows (commentaires conditionnels)
      - <a> inline-block pour tous les autres clients
    """
    return render_fragment("cta_button", URL=url, LABEL=label)


def _cta_secondary(url: str, label: str) -> str:
    """Lien secondaire centré sous le bouton principal (ex: Décliner l'invitation)."""
    return render_fragment("cta_secondary", URL=url, LABEL=label)


def _alert(content: str, variant: str = "warning") -> str:
    """
    Encadré discret.
    variant = "warning" → fond ivoire (note, conseil)
    variant = "danger"  → fond rosé (sécurité, vigilance)
    """
    styles = {
        "warning": ("#faf6ec", "#6d5a35"),
        "danger":  ("#fbf1f0", "#8c4640"),
    }
    bg, color = styles.get(variant, styles["warning"])
    return render_fragment("alert", BG=bg, COLOR=color, CONTENT=content)


def _code_block(code: str, label: str = "Code d'activation") -> str:
    """
    Bloc navy profond avec un code en grand centré.
    Réutilisé pour l'activation de compte ET le reset password.
    label : texte au-dessus du code (modifiable selon le contexte)
    """
    return render_fragment("code_block", LABEL=label, CODE=code)


def _steps_card(steps: list) -> str:
    """
    Card avec étapes numérotées.
    steps : liste de chaînes HTML décrivant chaque étape.
    """
    rows_html = ""
    for i, step in enumerate(steps, 1):
        margin = "style='margin-bottom:14px;'" if i < len(steps) else ""
        rows_html += render_fragment("step_row", MARGIN=margin, NUMBER=i, STEP=step)
    return render_fragment("steps_card", ROWS=rows_html)


def _note(content: str, margin: str = "0 0 4px 0") -> str:
    """Paragraphe de contenu libre entre deux blocs (ex: phrase de clôture).
    margin : CSS margin du <p> — la plupart des appels utilisent la valeur
             par défaut, mais certains (ex: send_event_approved) ont un
             espacement différent hérité du HTML d'origine."""
    return render_fragment("note", MARGIN=margin, CONTENT=content)


def _footer() -> str:
    """
    Pied de page navy : devise, contacts, copyright — centrés.
    """
    return render_fragment("footer", YEAR=datetime.now().year)


def _build_html(rows: str, preheader: str = "") -> str:
    """Assemble l'email complet : open + contenu + footer + close."""
    return _email_open(preheader) + rows + _footer() + _email_close()
