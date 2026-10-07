"""Template rendering — loads HTML fragments with {{VAR}} replacement."""

import os

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates", "fragments")


def render_fragment(name: str, **vars) -> str:
    """Charge templates/fragments/{name}.html et remplace chaque {{CLE}}."""
    path = os.path.join(_TEMPLATES_DIR, f"{name}.html")
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    for key, value in vars.items():
        html = html.replace(f"{{{{{key}}}}}", "" if value is None else str(value))
    return html
