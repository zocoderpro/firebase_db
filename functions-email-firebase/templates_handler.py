# ╔══════════════════════════════════════════════════════════════╗
# ║                                                              ║
# ║   MOTEUR DE RENDU — CHARGE LES FRAGMENTS HTML                ║
# ║                                                              ║
# ║   Le design vit dans templates/fragments/*.html.             ║
# ║   Ce module ne fait qu'injecter des variables {{VAR}}.       ║
# ║                                                              ║
# ╚══════════════════════════════════════════════════════════════╝

import os

FRAGMENTS_DIR = os.path.join(os.path.dirname(__file__), "templates", "fragments")


def render_fragment(name: str, **vars) -> str:
    """
    Charge templates/fragments/{name}.html et remplace chaque {{CLE}}
    par la valeur correspondante fournie en kwarg (clé insensible à la casse
    d'appel, mais le placeholder dans le fichier doit être en MAJUSCULES).
    """
    path = os.path.join(FRAGMENTS_DIR, f"{name}.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    for key, value in vars.items():
        html = html.replace(f"{{{{{key}}}}}", "" if value is None else str(value))
    return html
