# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU DES EMAILS                                         ║
# ║                                                              ║
# ║   C'est ici que tu modifies les textes et les données        ║
# ║   affichées dans chaque type d'email. Le design (HTML/CSS)   ║
# ║   vit dans templates/email.html — aucun HTML ici.            ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import html
import logging
import os
import uuid
from datetime import datetime

from config import APP_BASE_URL, SMTP_USER
from sender import _build_message, _send_email, _format_expiry
from templates_handler import render_email


def _row(label: str, value: str, mono: bool = False) -> dict:
    """Ligne « libellé / valeur » du récapitulatif de templates/email.html."""
    return {"LABEL": label, "VALUE": value, "MONO": mono}


# ──────────────────────────────────────────────────────────────
# EMAILS D'AUTHENTIFICATION
# ──────────────────────────────────────────────────────────────

def send_activation_code(email: str, first_name: str, code: str, expires_at: str) -> None:
    expiry_date = expires_at
    safe_first_name = html.escape(first_name or "")
    safe_code = html.escape(code or "")
    safe_expiry = html.escape(str(expiry_date or ""))

    html_content = render_email(
        PREHEADER=f"Votre code d'activation Athena Event : {safe_code}",
        EYEBROW="Activation de compte",
        TITLE="Vérification de votre compte",
        SUBTITLE="Utilisez le code ci-dessous pour activer votre accès",
        GREETING=f"Bonjour {safe_first_name},",
        INTRO=(
            "Merci de vous être inscrit sur <strong>Athena Event</strong>. "
            "Pour activer votre compte, saisissez le code de vérification "
            "ci-dessous dans l'application :"
        ),
        CODE_LABEL="Votre code d'activation",
        CODE=safe_code,
        INFO_TITLE="Expiration",
        INFO_ROWS=[_row("Expire dans", f"{safe_expiry} minutes")],
        ALERT_KIND="warning",
        ALERT_TEXT=(
            "<strong>Ne partagez jamais ce code.</strong> "
            "L'équipe Athena Event ne vous demandera jamais votre code "
            "par email ou par téléphone."
        ),
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Code d'activation Athena Event : {code}",
        to_addr=email,
        text_content=(
            f"Bonjour {first_name},\n\n"
            f"Votre code d'activation : {code}\n"
            f"Expire le : {expiry_date}\n\n"
            "Ne partagez jamais ce code.\n\n-- Athena Event"
        ),
        html_content=html_content,
    )

    _send_email(msg)
    logging.info(f"Email code activation envoyé à {email}")


def send_hostess_activation_link(
    email: str,
    first_name: str,
    last_name: str,
    default_password: str,
    activation_link: str,
    user_id: str,
) -> None:
    safe_email = html.escape(email or "")
    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_password = html.escape(default_password or "")
    safe_activation_link = html.escape(activation_link or "", quote=True)

    html_content = render_email(
        PREHEADER=f"Bienvenue dans l'équipe Athena Event, {safe_first_name} — activez votre compte",
        EYEBROW="Compte hôtesse",
        TITLE=f"Bienvenue, {safe_first_name} !",
        SUBTITLE="Votre compte hôtesse Athena Event a été créé",
        GREETING=f"Bonjour {safe_first_name} {safe_last_name},",
        INTRO=(
            "Nous avons le plaisir de vous inviter à rejoindre notre équipe d'hôtesses "
            "pour les événements <strong>Athena Event</strong>. Votre compte est prêt "
            "— il ne vous reste qu'à l'activer."
        ),
        INFO_TITLE="Vos identifiants de connexion",
        INFO_ROWS=[
            _row("Email", safe_email),
            _row("Mot de passe provisoire", safe_password, mono=True),
        ],
        NOTE=(
            "Cliquez sur le bouton ci-dessous pour activer votre compte "
            "et définir votre propre mot de passe :"
        ),
        CTA_URL=safe_activation_link,
        CTA_LABEL="Activer mon compte",
        ALERT_KIND="warning",
        ALERT_TEXT=(
            "<strong>Sécurité :</strong> Vous devrez changer ce mot de passe "
            "provisoire lors de votre première connexion. "
            "Ne partagez jamais vos identifiants avec qui que ce soit."
        ),
        SIGN_OFF="Nous sommes ravis de vous compter parmi notre équipe.<br>Cordialement,",
    )

    msg = _build_message(
        subject=f"Bienvenue dans l'équipe Athena Event — {first_name} {last_name}",
        to_addr=email,
        text_content=(
            f"Athena Event — Invitation Hôtesse\n\n"
            f"Bonjour {first_name} {last_name},\n\n"
            f"Email : {email}\n"
            f"Mot de passe provisoire : {default_password}\n\n"
            f"Activer mon compte : {activation_link}\n\n"
            "Changez votre mot de passe à la première connexion.\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<{user_id}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email hôtesse envoyé à {email}")


def send_reset_password_email(
    email: str, first_name: str, token: str, expires_at: str,
) -> None:
    expiry_date = expires_at
    safe_first_name = html.escape(first_name or "")
    safe_token = html.escape(token or "")
    safe_expiry = html.escape(str(expiry_date or ""))

    html_content = render_email(
        PREHEADER=f"Votre code de réinitialisation Athena Event : {safe_token}",
        EYEBROW="Sécurité du compte",
        TITLE="Réinitialisation du mot de passe",
        SUBTITLE="Utilisez le code ci-dessous pour créer un nouveau mot de passe",
        GREETING=f"Bonjour {safe_first_name},",
        INTRO=(
            "Nous avons reçu une demande de réinitialisation de mot de passe "
            "pour votre compte <strong>Athena Event</strong>. "
            "Saisissez le code ci-dessous dans l'application pour continuer :"
        ),
        CODE_LABEL="Votre code de réinitialisation",
        CODE=safe_token,
        INFO_TITLE="Expiration",
        INFO_ROWS=[_row("Expire le", safe_expiry)],
        ALERT_KIND="danger",
        ALERT_TITLE="Consignes de sécurité",
        ALERT_TEXT=(
            "Ne partagez jamais ce code. "
            "L'équipe Athena Event ne vous demandera jamais votre code par email ou téléphone. "
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email — "
            "votre mot de passe restera inchangé."
        ),
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Code de réinitialisation — Athena Event : {token}",
        to_addr=email,
        text_content=(
            f"Athena Event — Réinitialisation de mot de passe\n\n"
            f"Bonjour {first_name},\n\n"
            f"Votre code de réinitialisation : {token}\n"
            f"Expire le : {expiry_date}\n\n"
            "Ne partagez jamais ce code.\n"
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<reset-{token}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email reset password envoyé à {email}")


# ──────────────────────────────────────────────────────────────
# EMAILS ÉVÉNEMENTS
# ──────────────────────────────────────────────────────────────

def send_event_awaiting_approval(
    admin_email: str,
    event_id: str,
    event_title: str,
    company_name: str,
    created_at: str
) -> None:
    """Envoie un email à l'admin pour notifier qu'un événement attend approbation"""

    safe_event_title = html.escape(event_title or "")
    safe_company_name = html.escape(company_name or "")
    safe_created_at = html.escape(str(created_at or ""))

    html_content = render_email(
        PREHEADER=f"Nouvel événement en attente — {safe_event_title}",
        EYEBROW="Action requise",
        TITLE="Nouvel événement en attente",
        SUBTITLE="Une demande d'approbation vous attend sur la plateforme",
        GREETING="Bonjour,",
        INTRO=(
            "Un nouvel événement vient d'être créé et attend votre approbation "
            "sur la plateforme <strong>Athena Event</strong>."
        ),
        INFO_TITLE="Résumé de l'événement",
        INFO_ROWS=[
            _row("Événement", safe_event_title),
            _row("Organisateur", safe_company_name),
            _row("Créé le", safe_created_at),
        ],
        NOTE=(
            "Connectez-vous à votre tableau de bord administrateur pour "
            "consulter les détails complets et approuver ou rejeter cet événement."
        ),
        ALERT_KIND="warning",
        ALERT_TEXT=(
            "<strong>Action requise :</strong> Veuillez traiter cette demande "
            "dans les meilleurs délais pour permettre à l'organisateur de poursuivre "
            "la préparation de son événement."
        ),
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Nouvel événement en attente — {event_title}",
        to_addr=admin_email,
        text_content=(
            f"Athena Event — Nouvel événement en attente d'approbation\n\n"
            f"Événement : {event_title}\n"
            f"Organisateur : {company_name}\n"
            f"Créé le : {created_at}\n"
            f"Référence : #{event_id}\n\n"
            f"Accédez au tableau de bord admin pour approuver ou rejeter cet événement :\n"
            f"{APP_BASE_URL}/admin/events/pending\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<event-approval-{event_id}@athena-event.com>",
        x_priority="2",  # Haute priorité
    )

    _send_email(msg)
    logging.info(f"Email notification admin envoyé à {admin_email} pour événement {event_id}")


def send_event_approved(
    company_email: str,
    company_name: str,
    event_id: str,
    event_title: str,
    event_start_date: str,
    event_location: str,
    approved_at: str
) -> None:
    """Envoie un email à l'entreprise pour confirmer que son événement est approuvé"""

    safe_company_name = html.escape(company_name or "")
    safe_event_title = html.escape(event_title or "")
    safe_event_start_date = html.escape(str(event_start_date or ""))
    safe_event_location = html.escape(event_location or "")
    safe_approved_at = html.escape(str(approved_at or ""))

    html_content = render_email(
        PREHEADER=f"Félicitations ! Votre événement {safe_event_title} a été approuvé",
        EYEBROW="Approuvé",
        TITLE="Événement approuvé !",
        SUBTITLE="Félicitations, votre événement a été validé",
        GREETING=f"Bonjour {safe_company_name},",
        INTRO=(
            "Nous avons le plaisir de vous informer que votre événement "
            "<strong>" + safe_event_title + "</strong> a été approuvé par notre équipe. "
            "Vous pouvez désormais poursuivre la gestion de votre événement "
            "sur la plateforme <strong>Athena Event</strong>."
        ),
        FACTS=[
            {"LABEL": "Date", "VALUE": safe_event_start_date},
            {"LABEL": "Lieu", "VALUE": safe_event_location},
        ],
        INFO_TITLE="Détails de l'événement",
        INFO_ROWS=[
            _row("Événement", safe_event_title),
            _row("Approuvé le", safe_approved_at),
        ],
        NOTE=(
            "Vous pouvez maintenant inviter des participants, gérer les inscriptions "
            "et accéder à toutes les fonctionnalités de gestion d'événement."
        ),
        ALERT_KIND="ok",
        ALERT_TEXT=(
            "<strong>Prochaines étapes :</strong> Connectez-vous à votre espace "
            "pour commencer à inviter vos participants et suivre les inscriptions en temps réel."
        ),
        SIGN_OFF="Nous vous souhaitons un excellent événement !",
    )

    msg = _build_message(
        subject=f"Événement approuvé — {event_title}",
        to_addr=company_email,
        text_content=(
            f"Athena Event — Événement approuvé\n\n"
            f"Bonjour {company_name},\n\n"
            f"Félicitations ! Votre événement a été approuvé.\n\n"
            f"DÉTAILS DE L'ÉVÉNEMENT\n"
            f"Événement : {event_title}\n"
            f"Date : {event_start_date}\n"
            f"Lieu : {event_location}\n"
            f"Approuvé le : {approved_at}\n"
            f"Référence : #{event_id}\n\n"
            "Vous pouvez maintenant inviter des participants et gérer les inscriptions.\n\n"
            "Nous vous souhaitons un excellent événement !\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<event-approved-{event_id}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email approbation événement envoyé à {company_email} pour {event_id}")


# ──────────────────────────────────────────────────────────────
# EMAILS INVITATIONS PARTICIPANTS
# ──────────────────────────────────────────────────────────────

def send_participant_invitation_known(
    company_email: str, company_name: str, event_id: str, token: str, url: str
) -> None:
    confirm_url = url
    decline_url = f"{APP_BASE_URL}/api/events/{event_id}/participants/decline?token={token}"
    safe_company_name = html.escape(company_name or "")
    safe_confirm_url = html.escape(confirm_url or "", quote=True)
    safe_decline_url = html.escape(decline_url or "", quote=True)

    html_content = render_email(
        PREHEADER=f"Invitation à un événement Athena Event — {safe_company_name}",
        EYEBROW="Invitation événement",
        TITLE="Invitation à participer",
        SUBTITLE="Un événement vous attend sur Athena Event",
        GREETING="Bonjour,",
        INTRO=(
            "Nous espérons que vous allez bien. Nous vous contactons concernant "
            "une invitation à participer à un événement organisé sur la plateforme "
            f"<strong>Athena Event</strong> pour <strong>{safe_company_name}</strong>."
        ),
        INFO_TITLE="Détails de l'invitation",
        INFO_ROWS=[
            _row("Entreprise invitée", safe_company_name),
            _row("Date de l'invitation", datetime.now().strftime('%d %B %Y')),
        ],
        NOTE=(
            "Pour plus d'informations ou si vous avez des questions, n'hésitez pas "
            "à nous contacter. Notre équipe se tient à votre disposition."
        ),
        CTA_URL=safe_confirm_url,
        CTA_LABEL="Confirmer ma participation",
        CTA2_URL=safe_decline_url,
        CTA2_LABEL="Décliner l'invitation",
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Invitation à un événement — {company_name}",
        to_addr=company_email,
        text_content=(
            f"Invitation à un événement — {company_name}\n\n"
            f"Entreprise : {company_name} | Référence : #{event_id}\n\n"
            f"Confirmer : {confirm_url}\n"
            f"Décliner  : {decline_url}\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<{token}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email invitation (known) envoyé à {company_email}")


def send_participant_invitation_unknown(
    company_email: str, company_name: str, event_id: str, token: str, url: str
) -> None:
    if not company_email or '@' not in company_email:
        logging.error(f"Email invalide: '{company_email}'")
        raise ValueError(f"Email invalide: {company_email}")

    # TODO : remplacer localhost par APP_BASE_URL avant le déploiement en production
    signup_url = url
    safe_company_name = html.escape(company_name or "")
    safe_signup_url = html.escape(signup_url or "", quote=True)

    html_content = render_email(
        PREHEADER=f"Vous êtes invité à rejoindre un événement Athena Event — {safe_company_name}",
        EYEBROW="Nouvelle inscription",
        TITLE="Rejoignez un événement",
        SUBTITLE="Créez votre compte gratuit pour confirmer votre participation",
        GREETING="Bonjour,",
        INTRO=(
            "Nous vous contactons concernant une invitation à rejoindre un événement "
            f"organisé sur <strong>Athena Event</strong> pour <strong>{safe_company_name}</strong>. "
            "La création de votre compte est gratuite et prend moins de 2 minutes."
        ),
        STEPS_TITLE="Comment participer",
        STEPS=[
            {"NUMBER": 1, "TEXT": "Cliquez sur le bouton ci-dessous pour <strong>créer votre compte gratuitement</strong>"},
            {"NUMBER": 2, "TEXT": "Complétez les informations de <strong>votre entreprise</strong>"},
            {"NUMBER": 3, "TEXT": "Votre participation est <strong>automatiquement confirm&#233;e</strong> &#10003;"},
        ],
        CTA_URL=safe_signup_url,
        CTA_LABEL="Créer mon compte gratuit",
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Invitation à rejoindre un événement — {company_name}",
        to_addr=company_email,
        text_content=(
            f"Invitation à rejoindre un événement — {company_name}\n\n"
            "1. Créez votre compte gratuitement\n"
            "2. Complétez les informations de votre entreprise\n"
            "3. Votre participation est automatiquement confirmée\n\n"
            f"Créer mon compte : {signup_url}\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<{token}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email invitation (unknown) envoyé à {company_email}")


def send_event_invitation(email: str, full_name: str, event_title: str, url: str) -> None:
    """Invitation nominative à s'inscrire à un événement (bouton « Confirmer ma participation »)."""
    if not email or '@' not in email:
        logging.error(f"Email invalide: '{email}'")
        raise ValueError(f"Email invalide: {email}")

    safe_full_name = html.escape(full_name or "")
    safe_event_title = html.escape(event_title or "")
    safe_url = html.escape(url or "", quote=True)

    html_content = render_email(
        PREHEADER=f"Vous êtes invité(e) — {safe_event_title}",
        EYEBROW="Invitation",
        TITLE="Vous êtes invité(e)",
        SUBTITLE=safe_event_title,
        GREETING=f"Bonjour {safe_full_name},",
        INTRO=(
            "Nous avons le plaisir de vous convier à l'événement "
            f"<strong>{safe_event_title}</strong>. "
            "Votre présence nous honorerait : confirmez dès maintenant votre "
            "participation en quelques instants."
        ),
        CTA_URL=safe_url,
        CTA_LABEL="Confirmer ma participation",
        NOTE_END=(
            "Si le bouton ne s'affiche pas, copiez ce lien dans votre navigateur : "
            f"{safe_url}"
        ),
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Invitation — {event_title}",
        to_addr=email,
        text_content=(
            f"Bonjour {full_name},\n\n"
            f"Vous êtes invité(e) à l'événement « {event_title} ».\n\n"
            f"Confirmer ma participation : {url}\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<{uuid.uuid4().hex}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email invitation événement envoyé à {email}")


def send_activation_link_organizer(
    email: str,
    first_name: str,
    last_name: str,
    default_password: str,
    company_name: str,
    activation_link: str,
) -> None:
    safe_email = html.escape(email or "")
    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_password = html.escape(default_password or "")
    safe_company_name = html.escape(company_name or "")
    safe_activation_link = html.escape(activation_link or "", quote=True)

    html_content = render_email(
        PREHEADER=f"Bienvenue sur Athena Event, {safe_first_name} — activez votre compte organisateur",
        EYEBROW="Compte organisateur",
        TITLE=f"Bienvenue, {safe_first_name} !",
        SUBTITLE="Votre compte organisateur Athena Event a été créé",
        GREETING=f"Bonjour {safe_first_name} {safe_last_name},",
        INTRO=(
            f"Nous avons le plaisir de vous accueillir en tant qu'organisateur "
            f"sur <strong>Athena Event</strong>. Votre compte pour "
            f"<strong>{safe_company_name}</strong> est prêt — activez-le pour commencer."
        ),
        INFO_TITLE="Vos identifiants de connexion",
        INFO_ROWS=[
            _row("Email", safe_email),
            _row("Mot de passe provisoire", safe_password, mono=True),
            _row("Entreprise", safe_company_name),
        ],
        NOTE=(
            "Cliquez sur le bouton ci-dessous pour activer votre compte "
            "et définir votre propre mot de passe :"
        ),
        CTA_URL=safe_activation_link,
        CTA_LABEL="Activer mon compte",
        ALERT_KIND="warning",
        ALERT_TEXT=(
            "<strong>Sécurité :</strong> Vous devrez changer ce mot de passe "
            "provisoire lors de votre première connexion. "
            "Ne partagez jamais vos identifiants avec qui que ce soit."
        ),
        SIGN_OFF="Nous sommes ravis de vous compter parmi nos organisateurs.<br>Cordialement,",
    )

    msg = _build_message(
        subject=f"Bienvenue sur Athena Event — {first_name} {last_name}",
        to_addr=email,
        text_content=(
            f"Athena Event — Compte Organisateur\n\n"
            f"Bonjour {first_name} {last_name},\n\n"
            f"Email : {email}\n"
            f"Mot de passe provisoire : {default_password}\n"
            f"Entreprise : {company_name}\n\n"
            f"Activer mon compte : {activation_link}\n\n"
            "Changez votre mot de passe à la première connexion.\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
    )

    _send_email(msg)
    logging.info(f"Email organisateur envoyé à {email}")


# ──────────────────────────────────────────────────────────────
# VOUCHER — template générique (remplace l'ancien template figé JPM)
# ──────────────────────────────────────────────────────────────
_VOUCHER_REDEEM_URL = "https://athena-event.com/inscription"


def send_event_voucher(email: str, voucher_code: str) -> None:
    """Envoie un voucher (code d'accès gratuit, montant ramené à 0).

    Template générique : événement, bandeau et lien d'inscription ne sont plus
    figés — le backend fournit `eventTitle` et `redeemUrl` dans le payload.
    """
    safe_voucher_code = html.escape(voucher_code or "")
    event_title = "votre événement"
    redeem_url = _VOUCHER_REDEEM_URL

    html_content = render_email(
        PREHEADER=f"Votre voucher pour {event_title} : {safe_voucher_code}",
        EYEBROW="Voucher",
        TITLE="Votre code d'accès",
        SUBTITLE="Utilisez le code ci-dessous pour vous inscrire",
        GREETING="Bonjour,",
        INTRO=(
            f"Nous avons le plaisir de vous offrir votre place pour "
            f"<strong>{html.escape(event_title)}</strong>. Voici votre bon d'invitation :"
        ),
        CODE_LABEL="Votre code voucher",
        CODE=safe_voucher_code,
        NOTE=(
            "Pour vous inscrire gratuitement, cliquez sur le bouton S'inscrire, "
            "choisissez l'option &laquo;&nbsp;Code promo&nbsp;&raquo; "
            "lors du paiement et saisissez votre code."
        ),
        CTA_URL=html.escape(redeem_url, quote=True),
        CTA_LABEL="S'inscrire",
        ALERT_KIND="warning",
        ALERT_TEXT=(
            "<strong>Conservez cet email :</strong> votre code voucher vous sera "
            "demandé lors de l'inscription. Ne le partagez pas si vous ne "
            "souhaitez pas qu'il soit utilisé par quelqu'un d'autre."
        ),
        SIGN_OFF="Au plaisir de vous accueillir.<br>Cordialement,",
    )

    msg = _build_message(
        subject=f"Votre voucher — {event_title}",
        to_addr=email,
        text_content=(
            f"Bonjour,\n\n"
            f"Nous avons le plaisir de vous offrir votre place pour "
            f"{event_title}. Voici votre bon d'invitation.\n\n"
            f"Votre code voucher : {voucher_code}\n\n"
            "Pour vous inscrire gratuitement, cliquez sur le lien ci-dessous, "
            "choisissez l'option « Code promo » lors du paiement "
            "et saisissez votre code.\n\n"
            f"Inscription : {redeem_url}\n\n"
            "Conservez cet email : votre code voucher vous sera demandé lors de "
            "l'inscription.\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
        reply_to=SMTP_USER,
        message_id=f"<voucher-{voucher_code}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email voucher envoyé à {email}")


def send_request_otp(destinataire: str, otp: str, event_image_url: str = None) -> None:
    # event_image_url : accepté pour compatibilité avec le payload du backend, mais
    # plus utilisé — le hero du nouveau design est uni (pas d'image de fond).
    safe_otp = html.escape(otp or "")

    html_content = render_email(
        PREHEADER=f"Votre code d'accès à la liste des participants : {safe_otp}",
        EYEBROW="Vérification d'accès",
        TITLE="Consultez vos participants",
        SUBTITLE="Votre code d'accès à la liste des présents",
        GREETING="Bonjour,",
        INTRO=(
            "Vous avez demandé à consulter la liste des personnes venues à votre "
            "événement. Saisissez le code ci-dessous pour y accéder et découvrir qui "
            "a répondu présent :"
        ),
        CODE_LABEL="Votre code OTP",
        CODE=safe_otp,
        ALERT_KIND="danger",
        ALERT_TEXT=(
            "<strong>Ce code est valable quelques minutes.</strong> "
            "Ne le partagez avec personne — l'équipe Athena Event ne vous le demandera jamais. "
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email."
        ),
        SIGN_OFF="Cordialement,",
    )

    msg = _build_message(
        subject=f"Votre code d'accès à la liste des participants : {otp}",
        to_addr=destinataire,
        text_content=(
            f"Athena Event — Accès à la liste des participants\n\n"
            f"Vous avez demandé à consulter la liste des personnes venues à votre événement.\n\n"
            f"Votre code OTP : {otp}\n\n"
            "Ce code est valable quelques minutes.\n"
            "Ne le partagez avec personne.\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=html_content,
    )

    _send_email(msg)
    logging.info(f"Email OTP envoyé à {destinataire}")
