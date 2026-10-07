"""
Gestion des pieces jointes (programme + plan du lieu) pour l'email de confirmation de présence RJP 2026.

Supporte deux sources :
  - URL http(s) publique (ex: lien GCS signe ou CDN)
  - chemin GCS `gs://bucket/chemin/fichier.pdf`

Le backend n'est pas oblige de fournir des pieces jointes : si `attachments`
est vide/absent dans le payload, l'email part sans piece jointe (le corps
mentionne alors le programme/plan, l'organisateur peut fournir les liens plus
tard).
"""
import logging

import requests
from firebase_admin import storage

from config import BUCKET_NAME


def _download_from_url(url: str):
    """Telecharge un fichier depuis une URL http(s) publique."""
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f"Echec telechargement piece jointe {url}: {e}")
        return None


def _download_from_storage(gs_url: str):
    """Telecharge un fichier depuis Firebase Storage (gs://bucket/chemin)."""
    try:
        # gs://bucket/chemin/fichier -> chemin/fichier (le bucket est ignore,
        # on utilise BUCKET_NAME comme le fait functions-brochure-firebase).
        file_path = gs_url.replace("gs://", "", 1).split("/", 1)[-1]
        bucket = storage.bucket(BUCKET_NAME)
        blob = bucket.blob(file_path)
        return blob.download_as_bytes()
    except Exception as e:
        logging.error(f"Echec telechargement depuis Storage {gs_url}: {e}")
        return None


def load_attachment(url: str):
    """
    Charge une piece jointe et retourne un tuple (filename, bytes) ou None.
    `url` peut etre un lien http(s) ou un chemin gs://.
    """
    if not url or not url.strip():
        return None

    url = url.strip()
    if url.startswith("gs://"):
        data = _download_from_storage(url)
    elif url.startswith("http://") or url.startswith("https://"):
        data = _download_from_url(url)
    else:
        logging.warning(f"Source de piece jointe non supportee, ignoree: {url}")
        return None

    if data is None:
        return None

    # Nom de fichier derive de l'URL (dernier segment), nettoye des parametres.
    filename = url.split("?")[0].rstrip("/").split("/")[-1] or "piece-jointe.pdf"
    return filename, data


def load_attachments(urls: list) -> list:
    """Charge une liste de pieces jointes, ignore silencieusement les echecs."""
    attachments = []
    for url in urls or []:
        result = load_attachment(url)
        if result:
            attachments.append(result)
        else:
            logging.warning(f"Piece jointe ignoree (echec de chargement): {url}")
    return attachments
