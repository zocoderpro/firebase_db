# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU DES EMAILS                                         ║
# ║                                                              ║
# ║   C'est ici que tu modifies les textes, l'ordre des blocs,  ║
# ║   et les données affichées dans chaque type d'email.         ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import html
import logging
from datetime import datetime

from config import APP_BASE_URL, SMTP_USER
from sender import _build_message, _send_email, _format_expiry
from templates.components import (
    _hero,
    _body_open,
    _body_close,
    _info_card,
    _info_row,
    _cta_button,
    _cta_secondary,
    _alert,
    _code_block,
    _steps_card,
    _note,
    _build_html,
)


# ──────────────────────────────────────────────────────────────
# EMAILS D'AUTHENTIFICATION
# ──────────────────────────────────────────────────────────────

def send_activation_code(email: str, first_name: str, code: str, expires_at: str) -> None:
    expiry_date = expires_at
    safe_first_name = html.escape(first_name or "")
    safe_code = html.escape(code or "")
    safe_expiry = html.escape(str(expiry_date or ""))

    rows = (
        _hero(
            title="Vérification de votre compte",
            subtitle="Utilisez le code ci-dessous pour activer votre accès",
            email_type_label="Activation de compte",
        )
        + _body_open(
            greeting=f"Bonjour {safe_first_name},",
            intro=(
                "Merci de vous être inscrit sur <strong>Athena Event</strong>. "
                "Pour activer votre compte, saisissez le code de vérification "
                "ci-dessous dans l'application :"
            )
        )
        + _code_block(safe_code, label="Votre code d'activation")
        + _info_card(
            _info_row("", "Expire dans", f"<strong>{safe_expiry} minutes</strong>"),
            label="EXPIRATION"
        )
        + _alert(
            "<strong>Ne partagez jamais ce code.</strong> "
            "L'équipe Athena Event ne vous demandera jamais votre code "
            "par email ou par téléphone.",
            variant="warning"
        )
        + _body_close()
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
        html_content=_build_html(rows, preheader=f"Votre code d'activation Athena Event : {safe_code}"),
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

    creds_rows = (
        _info_row("", "Email", safe_email)
        + _info_row(
            "", "Mot de passe provisoire",
            f"<code style='background-color:#f2ede1;padding:2px 7px;"
            f"border-radius:4px;font-family:Courier New,monospace;"
            f"font-size:13px;color:#163057;'>{safe_password}</code>"
        )
    )

    rows = (
        _hero(
            title=f"Bienvenue, {safe_first_name} !",
            subtitle="Votre compte hôtesse Athena Event a été créé",
            email_type_label="Compte hôtesse",
        )
        + _body_open(
            greeting=f"Bonjour {safe_first_name} {safe_last_name},",
            intro=(
                "Nous avons le plaisir de vous inviter à rejoindre notre équipe d'hôtesses "
                "pour les événements <strong>Athena Event</strong>. Votre compte est prêt "
                "— il ne vous reste qu'à l'activer."
            )
        )
        + _info_card(creds_rows, label="Vos identifiants de connexion")
        + _note(
            "Cliquez sur le bouton ci-dessous pour activer votre compte "
            "et définir votre propre mot de passe :"
        )
        + _cta_button(safe_activation_link, "Activer mon compte")
        + _alert(
            "<strong>Sécurité :</strong> Vous devrez changer ce mot de passe "
            "provisoire lors de votre première connexion. "
            "Ne partagez jamais vos identifiants avec qui que ce soit.",
            variant="warning"
        )
        + _body_close("Nous sommes ravis de vous compter parmi notre équipe.<br>Cordialement,")
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
        html_content=_build_html(
            rows,
            preheader=f"Bienvenue dans l'équipe Athena Event, {safe_first_name} — activez votre compte"
        ),
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

    rows = (
        _hero(
            title="Réinitialisation du mot de passe",
            subtitle="Utilisez le code ci-dessous pour créer un nouveau mot de passe",
            email_type_label="Sécurité du compte",
        )
        + _body_open(
            greeting=f"Bonjour {safe_first_name},",
            intro=(
                "Nous avons reçu une demande de réinitialisation de mot de passe "
                "pour votre compte <strong>Athena Event</strong>. "
                "Saisissez le code ci-dessous dans l'application pour continuer :"
            )
        )
        + _code_block(safe_token, label="Votre code de réinitialisation")
        + _info_card(
            _info_row("", "Expire le", f"<strong>{safe_expiry}</strong>"),
            label="EXPIRATION"
        )
        + _alert(
            "<strong>Consignes de sécurité :</strong><br>"
            "Ne partagez jamais ce code. "
            "L'équipe Athena Event ne vous demandera jamais votre code par email ou téléphone. "
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email — "
            "votre mot de passe restera inchangé.",
            variant="danger"
        )
        + _body_close()
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
        html_content=_build_html(
            rows,
            preheader=f"Votre code de réinitialisation Athena Event : {safe_token}"
        ),
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

    info_rows = (
        _info_row("", "Événement", f"<strong>{safe_event_title}</strong>")
        + _info_row("", "Organisateur", safe_company_name)
        + _info_row("", "Créé le", safe_created_at)
    )

    rows = (
        _hero(
            title="Nouvel événement en attente",
            subtitle="Une demande d'approbation vous attend sur la plateforme",
            email_type_label="Action requise",
        )
        + _body_open(
            greeting="Bonjour,",
            intro=(
                "Un nouvel événement vient d'être créé et attend votre approbation "
                "sur la plateforme <strong>Athena Event</strong>."
            )
        )
        + _info_card(info_rows, label="RÉSUMÉ DE L'ÉVÉNEMENT")
        + _note(
            "Connectez-vous à votre tableau de bord administrateur pour "
            "consulter les détails complets et approuver ou rejeter cet événement."
        )
        + _alert(
            " <strong>Action requise :</strong> Veuillez traiter cette demande "
            "dans les meilleurs délais pour permettre à l'organisateur de poursuivre "
            "la préparation de son événement.",
            variant="warning"
        )
        + _body_close()
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
        html_content=_build_html(
            rows,
            preheader=f"Nouvel événement en attente — {safe_event_title}"
        ),
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

    info_rows = (
        _info_row("", "Événement", f"<strong>{safe_event_title}</strong>")
        + _info_row("", "Date", safe_event_start_date)
        + _info_row("", "Lieu", safe_event_location)
        + _info_row("", "Approuvé le", safe_approved_at)
    )

    rows = (
        _hero(
            title="Événement approuvé !",
            subtitle="Félicitations, votre événement a été validé",
            email_type_label="Approuvé",
        )
        + _body_open(
            greeting=f"Bonjour {safe_company_name},",
            intro=(
                "Nous avons le plaisir de vous informer que votre événement "
                "<strong>" + safe_event_title + "</strong> a été approuvé par notre équipe. "
                "Vous pouvez désormais poursuivre la gestion de votre événement "
                "sur la plateforme <strong>Athena Event</strong>."
            )
        )
        + _info_card(info_rows, label="DÉTAILS DE L'ÉVÉNEMENT")
        + _note(
            "Vous pouvez maintenant inviter des participants, gérer les inscriptions "
            "et accéder à toutes les fonctionnalités de gestion d'événement.",
            margin="20px 0 0 0"
        )
        + _alert(
            "<strong>Prochaines étapes :</strong> Connectez-vous à votre espace "
            "pour commencer à inviter vos participants et suivre les inscriptions en temps réel.",
            variant="warning"
        )
        + _body_close("Nous vous souhaitons un excellent événement !")
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
        html_content=_build_html(
            rows,
            preheader=f"Félicitations ! Votre événement {safe_event_title} a été approuvé"
        ),
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

    info_rows = (
        _info_row("", "Entreprise invitée", f"<strong>{safe_company_name}</strong>")
        + _info_row("", "Date de l'invitation", datetime.now().strftime('%d %B %Y'))
    )

    rows = (
        _hero(
            title="Invitation à participer",
            subtitle="Un événement vous attend sur Athena Event",
            email_type_label="Invitation événement",
        )
        + _body_open(
            greeting="Bonjour,",
            intro=(
                "Nous espérons que vous allez bien. Nous vous contactons concernant "
                "une invitation à participer à un événement organisé sur la plateforme "
                f"<strong>Athena Event</strong> pour <strong>{safe_company_name}</strong>."
            )
        )
        + _info_card(info_rows, label="Détails de l'invitation")
        + _note(
            "Pour plus d'informations ou si vous avez des questions, n'hésitez pas "
            "à nous contacter. Notre équipe se tient à votre disposition."
        )
        + _cta_button(safe_confirm_url, "Confirmer ma participation")
        + _cta_secondary(safe_decline_url, "Décliner l'invitation")
        + _body_close()
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
        html_content=_build_html(
            rows,
            preheader=f"Invitation à un événement Athena Event — {safe_company_name}"
        ),
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

    steps = [
        "Cliquez sur le bouton ci-dessous pour "
        "<strong style='color:#163057;'>créer votre compte gratuitement</strong>",
        "Complétez les informations de "
        "<strong style='color:#163057;'>votre entreprise</strong>",
        "Votre participation est "
        "<strong style='color:#163057;'>automatiquement confirm&#233;e</strong> &#10003;",
    ]

    rows = (
        _hero(
            title="Rejoignez un événement",
            subtitle="Créez votre compte gratuit pour confirmer votre participation",
            email_type_label="Nouvelle inscription",
        )
        + _body_open(
            greeting="Bonjour,",
            intro=(
                "Nous vous contactons concernant une invitation à rejoindre un événement "
                f"organisé sur <strong>Athena Event</strong> pour <strong>{safe_company_name}</strong>. "
                "La création de votre compte est gratuite et prend moins de 2 minutes."
            )
        )
        + _steps_card(steps)
        + _cta_button(safe_signup_url, "Créer mon compte gratuit")
        + _body_close()
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
        html_content=_build_html(
            rows,
            preheader=f"Vous êtes invité à rejoindre un événement Athena Event — {safe_company_name}"
        ),
        reply_to=SMTP_USER,
        message_id=f"<{token}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email invitation (unknown) envoyé à {company_email}")


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

    creds_rows = (
        _info_row("", "Email", safe_email)
        + _info_row(
            "", "Mot de passe provisoire",
            f"<code style='background-color:#f2ede1;padding:2px 7px;"
            f"border-radius:4px;font-family:Courier New,monospace;"
            f"font-size:13px;color:#163057;'>{safe_password}</code>"
        )
        + _info_row("", "Entreprise", f"<strong>{safe_company_name}</strong>")
    )

    rows = (
        _hero(
            title=f"Bienvenue, {safe_first_name} !",
            subtitle="Votre compte organisateur Athena Event a été créé",
            email_type_label="Compte organisateur",
        )
        + _body_open(
            greeting=f"Bonjour {safe_first_name} {safe_last_name},",
            intro=(
                f"Nous avons le plaisir de vous accueillir en tant qu'organisateur "
                f"sur <strong>Athena Event</strong>. Votre compte pour "
                f"<strong>{safe_company_name}</strong> est prêt — activez-le pour commencer."
            )
        )
        + _info_card(creds_rows, label="Vos identifiants de connexion")
        + _note(
            "Cliquez sur le bouton ci-dessous pour activer votre compte "
            "et définir votre propre mot de passe :"
        )
        + _cta_button(safe_activation_link, "Activer mon compte")
        + _alert(
            "<strong>Sécurité :</strong> Vous devrez changer ce mot de passe "
            "provisoire lors de votre première connexion. "
            "Ne partagez jamais vos identifiants avec qui que ce soit.",
            variant="warning"
        )
        + _body_close("Nous sommes ravis de vous compter parmi nos organisateurs.<br>Cordialement,")
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
        html_content=_build_html(
            rows,
            preheader=f"Bienvenue sur Athena Event, {safe_first_name} — activez votre compte organisateur"
        ),
        reply_to=SMTP_USER,
    )

    _send_email(msg)
    logging.info(f"Email organisateur envoyé à {email}")


def send_event_voucher(
    email: str,
    first_name: str,
    last_name: str,
    event_title: str,
    voucher_code: str,
) -> None:
    """Envoie un voucher (code d'accès gratuit, montant ramené à 0) pour un événement précis."""
    safe_first_name = html.escape(first_name or "")
    safe_last_name = html.escape(last_name or "")
    safe_event_title = html.escape(event_title or "")
    safe_voucher_code = html.escape(voucher_code or "")

    rows = (
        _hero(
            title="Votre voucher est prêt",
            subtitle=f"Accès offert pour {safe_event_title}",
            email_type_label="Voucher événement",
        )
        + _body_open(
            greeting=f"Bonjour {safe_first_name} {safe_last_name},",
            intro=(
                f"Nous avons le plaisir de vous offrir un accès gratuit à "
                f"<strong>{safe_event_title}</strong> sur la plateforme "
                f"<strong>Athena Event</strong>. Voici votre voucher :"
            )
        )
        + _code_block(safe_voucher_code, label="Votre code voucher")
        + _note(
            "Saisissez ce code lors de votre inscription sur la plateforme "
            "Athena Event — le montant sera automatiquement ramené à 0."
        )
        + _alert(
            "<strong>Conservez cet email :</strong> votre code voucher vous sera "
            "demandé lors de l'inscription. Ne le partagez pas si vous ne "
            "souhaitez pas qu'il soit utilisé par quelqu'un d'autre.",
            variant="warning"
        )
        + _body_close("Au plaisir de vous accueillir.<br>Cordialement,")
    )

    msg = _build_message(
        subject=f"Votre voucher Athena Event — {event_title}",
        to_addr=email,
        text_content=(
            f"Athena Event — Voucher\n\n"
            f"Bonjour {first_name} {last_name},\n\n"
            f"Nous avons le plaisir de vous offrir un accès gratuit à {event_title}.\n\n"
            f"Votre code voucher : {voucher_code}\n\n"
            "Saisissez ce code lors de votre inscription sur la plateforme "
            "Athena Event — le montant sera automatiquement ramené à 0.\n\n"
            "Conservez cet email : votre code voucher vous sera demandé lors de "
            "l'inscription.\n\n"
            "Cordialement,\nL'équipe Athena Event"
        ),
        html_content=_build_html(
            rows,
            preheader=f"Votre voucher pour {safe_event_title} : {safe_voucher_code}"
        ),
        reply_to=SMTP_USER,
        message_id=f"<voucher-{voucher_code}@athena-event.com>",
    )

    _send_email(msg)
    logging.info(f"Email voucher envoyé à {email} pour {event_title}")


def send_request_otp(destinataire: str, otp: str, event_image_url: str = None) -> None:
    safe_otp = html.escape(otp or "")
    safe_event_image_url = html.escape(event_image_url, quote=True) if event_image_url else ""

    rows = (
        _hero(
            title="Consultez vos participants",
            subtitle="Votre code d'accès à la liste des présents",
            email_type_label="Vérification d'accès",
            hero_image_url=safe_event_image_url,
        )
        + _body_open(
            greeting="Bonjour,",
            intro=(
                "Vous avez demandé à consulter la liste des personnes venues à votre "
                "événement. Saisissez le code ci-dessous pour y accéder et découvrir qui "
                "a répondu présent :"
            )
        )
        + _code_block(safe_otp, label="Votre code OTP")
        + _alert(
            "<strong>Ce code est valable quelques minutes.</strong> "
            "Ne le partagez avec personne — l'équipe Athena Event ne vous le demandera jamais. "
            "Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.",
            variant="danger"
        )
        + _body_close()
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
        html_content=_build_html(rows, preheader=f"Votre code d'accès à la liste des participants : {safe_otp}"),
    )

    _send_email(msg)
    logging.info(f"Email OTP envoyé à {destinataire}")
