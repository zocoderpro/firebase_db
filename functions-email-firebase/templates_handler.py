# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   MOTEUR DE RENDU — UN SEUL TEMPLATE : templates/email.html  ║
# ║                                                              ║
# ║   Tout le design vit dans templates/email.html. Ce module    ║
# ║   ne fait qu'y injecter des données :                        ║
# ║                                                              ║
# ║     {{CLE}}                      → valeur (HTML déjà échappé)║
# ║     <!--IF:CLE-->…<!--/IF:CLE--> → bloc gardé si CLE non vide║
# ║     <!--IFNOT:CLE-->…            → bloc gardé si CLE vide    ║
# ║     <!--EACH:CLE-->…<!--/EACH:CLE-->                         ║
# ║                                  → bloc répété pour chaque   ║
# ║                                    dict de la liste CLE ; les║
# ║                                    clés du dict deviennent   ║
# ║                                    des {{CLE}} locales       ║
# ║                                    ({{INDEX}} = rang, de 1)  ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import logging
import os
import re
from datetime import datetime
from functools import lru_cache

from config import BRAND_KICKER, BRAND_NAME, LOGO_URL

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "email.html")

# Texte invisible de padding pour le preheader — force les clients email
# à ne pas afficher le début du corps de l'email dans l'aperçu.
_PREHEADER_FILLER = "&nbsp;&#8204;" * 60

# Un seul passage : un bloc OU une variable. Ce qui est injecté n'est jamais
# re-scanné, donc une donnée contenant « {{X}} » reste du texte brut.
_TOKEN = re.compile(
    r"<!--(IF|IFNOT|EACH):([A-Z0-9_]+)-->(.*?)<!--/\1:\2-->|\{\{([A-Z0-9_]+)\}\}",
    re.DOTALL,
)


@lru_cache(maxsize=1)
def _load_template() -> str:
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _render(source: str, ctx: dict) -> str:
    def replace(match):
        kind, name, body, var = match.groups()
        if var:
            if var not in ctx:
                logging.warning(f"Template email : variable {{{{{var}}}}} non fournie")
                return ""
            value = ctx[var]
            return "" if value is None else str(value)
        value = ctx.get(name)
        if kind == "IF":
            return _render(body, ctx) if value else ""
        if kind == "IFNOT":
            return "" if value else _render(body, ctx)
        # EACH
        return "".join(
            _render(body, {**ctx, **item, "INDEX": i})
            for i, item in enumerate(value or [], start=1)
        )

    return _TOKEN.sub(replace, source)


def render_email(**ctx) -> str:
    """Rend templates/email.html avec les données fournies en kwargs (clés en MAJUSCULES).

    Valeurs injectées telles quelles : l'appelant échappe (html.escape) tout champ
    venant du backend avant de le passer.
    """
    ctx.setdefault("LOGO", LOGO_URL)
    ctx.setdefault("BRAND", BRAND_NAME)
    ctx.setdefault("KICKER", BRAND_KICKER)
    ctx.setdefault("DOC_TITLE", ctx["BRAND"])
    ctx.setdefault("YEAR", datetime.now().year)
    ctx.setdefault("PREHEADER_FILLER", _PREHEADER_FILLER)
    # ALERT_KIND="warning|danger|ok" → drapeaux ALERT_WARNING / ALERT_DANGER / ALERT_OK
    kind = ctx.get("ALERT_KIND")
    if kind:
        ctx[f"ALERT_{kind.upper()}"] = True
        ctx["ALERT_ANY"] = True
    return _render(_load_template(), ctx)
