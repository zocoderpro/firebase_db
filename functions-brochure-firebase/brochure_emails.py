# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   CONTENU DES EMAILS                                         ║
# ║                                                              ║
# ║   Un constructeur par numéro de template (staticTemplateNum).║
# ║   C'est ici que tu modifies les textes et les données        ║
# ║   affichées ; le design (HTML/CSS) vit dans                  ║
# ║   templates/email.html — aucun HTML ici.                     ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import html
from datetime import datetime

from event_content import PG_SPONSORS, RJP_PATRONAGE, RJP_SPONSORS, sections_ctx
from templates_handler import asset_uri, footer_links, render_email


def _e(value) -> str:
    """Échappe un champ venant du backend (texte et attributs)."""
    return html.escape(str(value or "").strip())


def _rows(*pairs) -> list:
    """Lignes « libellé / valeur » du récapitulatif — les valeurs vides sont omises."""
    return [{"LABEL": label, "VALUE": value} for label, value in pairs if value]


# ──────────────────────────────────────────────────────────────
# 1 à 3 — BROCHURE (merci de votre visite, aux couleurs de l'entreprise)
# ──────────────────────────────────────────────────────────────

def _brochure(data: dict) -> str:
    company_name = _e(data.get("company_name"))
    company_email = _e(data.get("company_email"))
    first_name = _e(data.get("firstName"))

    # customContent : HTML libre fourni par le backend (« accepte TOUT HTML »),
    # donc volontairement non échappé — avec un texte par défaut s'il est vide.
    custom_content = data.get("customContent")
    if custom_content is None or custom_content.strip() == "":
        event_name = _e(data.get("event_name") or "l'événement")
        custom_content = (
            f"Merci pour cet échange enrichissant lors de {event_name} ! N'hésitez pas "
            "à nous contacter pour toute question ou besoin d'information complémentaire."
        )

    ctx = dict(
        PREHEADER=f"Merci de votre visite — {company_name}",
        DOC_TITLE=company_name,
        BRAND=company_name,
        KICKER="Votre partenaire stratégique",
        HEADER_TAG="Merci de votre visite",
        EYEBROW="Suite à notre rencontre lors de l'événement Athena",
        TITLE=f"Ravi de vous avoir rencontré, {first_name} !",
        SUBTITLE="Voici les ressources dont nous avons discuté",
        GREETING=f"Bonjour {first_name},",
        BODY_HTML=custom_content,
        NOTE="Des questions ? Envie d'aller plus loin ?",
        CTA_URL=f"mailto:{company_email}",
        CTA_LABEL="Planifier un échange &rarr;",
        NOTE_END=(
            "Ou répondez directement à cet email.<br>"
            "Nous sommes impatients de pouvoir contribuer à votre réussite."
        ),
        SIGN_OFF="Bien cordialement,",
        SIGNATURE=f"L'équipe {company_name}",
        FOOTER_TAGLINE=company_name,
        FOOTER_LINKS=footer_links((company_email, f"mailto:{company_email}")),
        FOOTER_COPY=f"&copy; {datetime.now().year} {company_name}. Tous droits réservés.",
        FOOTER_NOTE="Cet email vous a été envoyé car vous avez visité notre stand lors d'Athena Event.",
        UNSUBSCRIBE_URL=_e(data.get("unsubscribeUrl")),
    )
    # Logo de l'entreprise (URL directe) ; à défaut, logo Athena embarqué
    if (data.get("company_logo") or "").strip():
        ctx["LOGO"] = _e(data["company_logo"])
    return render_email(**ctx)


# ──────────────────────────────────────────────────────────────
# 4 — EVENT_REGISTRATION_REQUEST_SECOND_CONFIRMATION
# ──────────────────────────────────────────────────────────────

def _second_confirmation(data: dict) -> str:
    event_title = _e(data.get("eventTitle") or data.get("event_name") or "Événement Athena")
    limit_day = _e(data.get("limitDaySuggestion"))

    return render_email(
        PREHEADER=(
            "L'événement affiche complet. Un clic suffit pour garder votre place — "
            "sans réponse, elle reviendra à une personne en liste d'attente."
        ),
        EYEBROW="Confirmation requise",
        TITLE="Confirmation de votre place",
        SUBTITLE="L'événement est complet — confirmez votre présence en un clic",
        GREETING=f"Bonjour {_e(data.get('firstName'))},",
        INTRO=(
            f"<strong>Les inscriptions à {event_title} ont dépassé le nombre de places "
            "disponibles — l'intérêt a été bien plus fort que prévu.</strong><br><br>"
            "Vous faites partie des inscrits, et nous voulons nous assurer que votre place "
            "vous est bien gardée. Pour être justes envers tout le monde, nous confirmons "
            "une dernière fois les présences : indiquez-nous en un clic si vous serez là. "
            f"Sans réponse de votre part d'ici le {limit_day}, votre place sera proposée "
            "à une personne en liste d'attente.<br><br>"
            "Et si vous ne pouvez plus venir, dites-le-nous sans gêne : vous libérez ainsi "
            "votre place pour quelqu'un qui attend de pouvoir y assister. C'est un vrai coup de main."
        ),
        INFO_TITLE="Détails de l'événement",
        INFO_HEADING=event_title,
        INFO_TEXT=_e(data.get("eventDescription")),
        INFO_ROWS=_rows(
            ("Date de début", _e(data.get("eventStartDate"))),
            ("Date de fin", _e(data.get("eventEndDate"))),
            ("Limite de place", _e(data.get("eventCapacity"))),
            ("Veuillez répondre avant", limit_day),
        ),
        CTA_URL=_e(data.get("confirmationLink") or "#"),
        CTA_LABEL="Oui, je serai présent(e)",
        CTA2_URL=_e(data.get("declineLink") or "#"),
        CTA2_LABEL="Non, je libère ma place",
        NOTE_END=(
            "Trente secondes suffisent pour répondre — merci de le faire, cela nous aide à "
            "préparer un bon événement sans oublier personne sur la liste d'attente."
        ),
        SIGN_OFF="Cordialement,",
    )


# ──────────────────────────────────────────────────────────────
# 5 — EVENT_THANK_YOU (Rencontre Géopolitique de l'Océan Indien 2026)
# ──────────────────────────────────────────────────────────────

def _thank_you_rjp(data: dict) -> str:
    return render_email(
        PREHEADER="Deux jours d'échanges pour l'avenir de notre région — merci d'en avoir fait partie.",
        EYEBROW="Rencontre Géopolitique · Océan Indien",
        TITLE="Merci d'avoir été des nôtres.",
        SUBTITLE="Plus de 200 participants · 2 journées d'échanges",
        GREETING=f"Bonjour {_e(data.get('toFirstName'))},",
        INTRO=(
            "Pendant deux jours, vous avez pris part aux échanges sur les enjeux et les "
            "reconfigurations géopolitiques de l'océan Indien. Votre présence, vos questions "
            "et vos idées ont donné tout son sens à cette Rencontre. Nous vous en remercions "
            "très sincèrement.<br><br>"
            "Les temps forts, les photos et les conclusions des panels vous seront partagés "
            "prochainement. En attendant, votre retour nous serait précieux pour construire "
            "la prochaine édition."
        ),
        FACTS=[
            {"LABEL": "Dates", "VALUE": _e(data.get("eventDateRange"))},
            {"LABEL": "Lieu", "VALUE": "Palais d'Andafiavaratra · Antananarivo"},
        ],
        PATRONAGE=RJP_PATRONAGE,
        SECTIONS=sections_ctx(RJP_SPONSORS),
        SIGN_OFF="Bien à vous,",
        SIGNATURE="Les organisateurs",
        SIGNATURE_SUB="Club 1808 &nbsp;&middot;&nbsp; Institut Diplomatique de Paris (IDP)",
        SIGNATURE_LOGO=asset_uri("9efe5070.png"),
        FOOTER_TAGLINE="&laquo;&nbsp;Raharaha ikambanana ho an'i Madagasikara&nbsp;&raquo;",
        FOOTER_LINKS=footer_links(
            ("club1808.com", "https://club1808.com/"),
            ("contact@club1808.com", "mailto:contact@club1808.com"),
        ),
        FOOTER_COPY="",
        FOOTER_NOTE=(
            "Vous recevez cet e-mail car vous étiez inscrit(e) à la Rencontre Géopolitique "
            "de l'Océan Indien 2026."
        ),
        UNSUBSCRIBE_URL=_e(data.get("unsubscribeUrl")),
    )


# ──────────────────────────────────────────────────────────────
# 6 — CONTACT_REQUEST / 7 — ACCEPT_CONTACT_REQUEST (mise en relation)
# ──────────────────────────────────────────────────────────────

def _full_name(first, last, fallback) -> str:
    return " ".join(part for part in (_e(first), _e(last)) if part) or _e(fallback)


def _contact_footer(reason: str) -> dict:
    return dict(
        FOOTER_LINKS=footer_links(
            ("athena-event.com", "https://athena-event.com/"),
            ("noreply@athena-event.com", "mailto:noreply@athena-event.com"),
        ),
        FOOTER_COPY="",
        FOOTER_NOTE=reason,
    )


def _greeting_dest(data: dict) -> str:
    dest_name = " ".join(
        part for part in (_e(data.get("destFirstName")), _e(data.get("destLastName"))) if part
    )
    return f"Bonjour {dest_name}," if dest_name else "Bonjour,"


def _contact_request(data: dict) -> str:
    contacts = []
    for requester in data.get("requesters") or []:
        email = _e(requester.get("requesterEmail"))
        link = _e(requester.get("acceptationLink"))
        contacts.append({
            "K_NAME": _full_name(requester.get("requesterFirstName"),
                                 requester.get("requesterLastName"), email),
            "K_ROLE": " &middot; ".join(
                p for p in (_e(requester.get("requesterProfession")),
                            _e(requester.get("requesterCompany"))) if p
            ),
            "K_EMAIL": email,
            "K_TEL": _e(requester.get("requesterTel")),
            "K_NOTE": _e(requester.get("note")),
            "K_BTN_URL": link,
        })

    return render_email(
        PREHEADER="Des participants souhaitent rester en contact avec vous — retrouvez leurs coordonnées ci-dessous.",
        EYEBROW="Athena Event · Mise en relation",
        TITLE="Des participants souhaitent entrer en contact avec vous.",
        SUBTITLE="Vos demandes de mise en relation",
        GREETING=_greeting_dest(data),
        INTRO=(
            "À l'occasion de l'événement, plusieurs participants ont exprimé le souhait "
            "d'entrer en relation avec vous. Vous trouverez ci-dessous leurs coordonnées, "
            "accompagnées, le cas échéant, du message qu'ils vous ont adressé."
        ),
        CONTACTS=contacts,
        NOTE_END=(
            "Nous vous laissons le soin de donner suite à ces demandes, selon votre "
            "convenance, en écrivant directement à l'adresse indiquée. Chaque échange qui "
            "se prolonge au-delà de l'événement en fait grandir la valeur."
        ),
        SIGN_OFF="Bien à vous,",
        **_contact_footer(
            "Vous recevez cet e-mail car des participants ont demandé à entrer en contact "
            "avec vous via Athena Event."
        ),
    )


def _contact_accepted(data: dict) -> str:
    email = _e(data.get("accepterEmail"))
    contact = {
        "K_NAME": _full_name(data.get("accepterFirstName"), data.get("accepterLastName"), email),
        "K_EMAIL": email,
        "K_TEL": _e(data.get("accepterTel")),
        "K_NOTE": _e(data.get("accepterNote")),
        "K_BADGE": "Demande acceptée",
    }
    dest_note = _e(data.get("destNote"))

    return render_email(
        PREHEADER="Bonne nouvelle — votre demande de mise en relation a été acceptée.",
        EYEBROW="Athena Event · Mise en relation",
        TITLE="Votre demande de contact a été acceptée.",
        SUBTITLE="Mise en relation confirmée",
        GREETING=_greeting_dest(data),
        INTRO=(
            "Nous avons le plaisir de vous annoncer qu'une suite favorable a été donnée à "
            "votre demande de mise en relation. Vous trouverez ci-dessous les coordonnées "
            "de la personne qui a accepté votre invitation, accompagnées, le cas échéant, "
            "du message qu'elle vous a adressé."
        ),
        CONTACTS=[contact],
        CONTACTS_FOOT=(
            "Pour mémoire, le message que vous aviez adressé&nbsp;: "
            f"&laquo;&nbsp;{dest_note}&nbsp;&raquo;"
        ) if dest_note else "",
        NOTE_END=(
            "Nous vous invitons à poursuivre cet échange en écrivant directement à "
            "l'adresse indiquée. C'est ainsi que les rencontres d'un événement deviennent "
            "des relations durables."
        ),
        SIGN_OFF="Bien à vous,",
        **_contact_footer(
            "Vous recevez cet e-mail car votre demande de mise en relation a été acceptée "
            "via Athena Event."
        ),
    )


# ──────────────────────────────────────────────────────────────
# 8 / 9 — Madagascar PostgreSQL Conference 2026 (rappel J-1, remerciement)
# ──────────────────────────────────────────────────────────────

def _pg_common() -> dict:
    return dict(
        EYEBROW="Open source · Single-track · Community",
        TITLE="Madagascar PostgreSQL Conference 2026",
        HERO_LOGO=asset_uri("d24259a9.png"),
        HERO_LOGO_ALT="PostgreSQL Users Group Madagascar",
        SECTIONS=sections_ctx(PG_SPONSORS),
        SIGN_OFF="Bien à vous,",
        SIGNATURE="L'équipe PostgreSQL User Group Madagascar",
        SIGNATURE_SUB="Communauté PostgreSQL Madagascar (MG-PUG)",
        FOOTER_TAGLINE="Powered by AthenaEvent &mdash; Intelligence &eacute;v&eacute;nementielle",
        FOOTER_COPY=(
            "Madagascar PostgreSQL Conference 2026 &middot; Communaut&eacute; PostgreSQL "
            "Madagascar (MG-PUG)<br>18 juillet 2026 &middot; Ingenosya, Antananarivo"
        ),
    )


def _pg_reminder(data: dict) -> str:
    return render_email(
        PREHEADER="Accueil dès 8h30 à Ingenosya — et pensez à apporter votre CV pour les rencontres de demain.",
        SUBTITLE="C'est demain · Samedi 18 juillet",
        GREETING="À demain !",
        INTRO=(
            "Vous êtes inscrit·e à la Madagascar PostgreSQL Conference 2026, et nous avons "
            "hâte de vous accueillir demain à Ingenosya. Voici un petit rappel pour bien "
            "préparer votre journée."
        ),
        FACTS=[
            {"LABEL": "Date", "VALUE": "Samedi 18 juillet 2026"},
            {"LABEL": "Horaire", "VALUE": "08:30 &ndash; 13:00 &middot; accueil dès 08:30"},
            {"LABEL": "Lieu", "VALUE": "Ingenosya, Antananarivo"},
        ],
        ALERT_KIND="warning",
        ALERT_TITLE="Pensez à votre CV",
        ALERT_TEXT=(
            "La journée sera aussi une occasion de réseauter&nbsp;: plusieurs entreprises "
            "et organisations présentes pourraient recruter. Apportez votre CV &mdash; "
            "imprimé ou simplement sur votre téléphone &mdash; pour profiter pleinement "
            "de ces échanges."
        ),
        AGENDA_TITLE="Au programme",
        AGENDA=[
            {"A_TIME": "08:30", "A_TEXT": "Accueil, café et remise des badges"},
            {"A_TIME": "09:00&ndash;12:15", "A_TEXT": "Conférences &amp; échanges &mdash; santé, SIG, performance, IA..."},
            {"A_TIME": "12:15&ndash;13:00", "A_TEXT": "Réseautage et collation"},
        ],
        AGENDA_URL="https://pugmg.github.io/pgconf-antananarivo-2026/#programme",
        AGENDA_LABEL="Voir le programme complet &rarr;",
        SECTIONS_HEADING="Merci à nos sponsors et partenaires",
        SECTIONS_SUB="Cette conférence gratuite est rendue possible grâce à eux.",
        FOOTER_NOTE="",
        **{k: v for k, v in _pg_common().items() if k != "FOOTER_NOTE"},
    )


def _pg_thanks(data: dict) -> str:
    return render_email(
        PREHEADER="Merci d'avoir fait de cette première édition un moment inoubliable pour la communauté PostgreSQL malgache.",
        SUBTITLE="Merci pour votre présence",
        GREETING="Merci !",
        INTRO=(
            "La Madagascar PostgreSQL Conference 2026 s'est achevée le samedi 18 juillet à "
            "Ingenosya, et nous tenions à vous remercier chaleureusement d'y avoir participé. "
            "Vos échanges, votre curiosité et votre énergie ont fait de cette journée un "
            "véritable succès pour la communauté PostgreSQL malgache.<br><br>"
            "Nous espérons que vous repartez avec de nouvelles connaissances, de belles "
            "rencontres et l'envie de continuer à faire vivre l'écosystème open source à "
            "Madagascar. À très bientôt pour la prochaine édition&nbsp;!"
        ),
        SECTIONS_HEADING="Un immense merci à nos sponsors et partenaires",
        SECTIONS_SUB="Cette conférence gratuite, ouverte à tous, a été rendue possible grâce à leur généreux soutien.",
        FOOTER_NOTE="Vous recevez cet e-mail car vous étiez inscrit·e à la Madagascar PostgreSQL Conference 2026.",
        **{k: v for k, v in _pg_common().items() if k != "FOOTER_NOTE"},
    )


# ──────────────────────────────────────────────────────────────
# Dispatch par numéro de template
# ──────────────────────────────────────────────────────────────

BUILDERS = {
    1: _brochure,            # Corporate Élégant       ┐ un seul design désormais :
    2: _brochure,            # Modern Professional     │ les trois numéros restent
    3: _brochure,            # Business Professional   ┘ acceptés par le backend
    4: _second_confirmation, # Confirmation d'inscription événementielle
    5: _thank_you_rjp,       # Remerciement post-événement (RJP 2026)
    6: _contact_request,     # Demandes de mise en relation
    7: _contact_accepted,    # Acceptation d'une mise en relation
    8: _pg_reminder,         # Rappel J-1 (PostgreSQL Conference 2026)
    9: _pg_thanks,           # Remerciement (PostgreSQL Conference 2026)
}


def build_html(template_num: int, data: dict) -> str:
    builder = BUILDERS.get(template_num)
    if builder is None:
        raise ValueError(f"Template numéro {template_num} non trouvé. Utilisez un numéro de 1 à 9.")
    return builder(data)
