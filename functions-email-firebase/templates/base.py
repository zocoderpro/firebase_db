# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   ZONE DESIGN — ENVELOPPE HTML                               ║
# ║                                                              ║
# ║   Le HTML de l'enveloppe (styles, structure du document)     ║
# ║   vit dans templates/fragments/envelope_open.html et         ║
# ║   envelope_close.html. Ce fichier ne fait qu'injecter le     ║
# ║   preheader dans le fragment d'ouverture.                    ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

from templates_handler import render_fragment

# Texte invisible de padding pour le preheader — force les clients email
# à ne pas afficher le début du corps de l'email dans l'aperçu.
_PREHEADER_FILLER = "&nbsp;&#8204;" * 60


def _email_open(preheader_text: str = "") -> str:
    """Ouvre le document HTML, injecte les styles et la table wrapper principale."""
    return render_fragment(
        "envelope_open",
        PREHEADER=preheader_text,
        PREHEADER_FILLER=_PREHEADER_FILLER,
    )


def _email_close() -> str:
    """Ferme la table shell, ajoute la note légale, ferme le body."""
    return render_fragment("envelope_close")
