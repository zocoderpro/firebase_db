import os

from google.cloud import storage as gcs_storage

# "FUNCTIONS_EMULATOR" est positionnée par l'émulateur Firebase Functions
# (Node comme Python) et ne vaut "true" qu'en local. "K_SERVICE" n'est PAS un
# indicateur fiable ici : l'émulateur Gen2 le définit lui aussi (il imite
# l'environnement Cloud Run), donc l'utiliser seul fait passer le local pour
# de la prod. Sert à distinguer prod (vrai client GCS) de dev local
# (émulateur Firebase Storage).
if os.environ.get("FUNCTIONS_EMULATOR") == "true":
    # Développement local — émulateur Firebase Storage
    os.environ["STORAGE_EMULATOR_HOST"] = "http://127.0.0.1:9199"
    storage_client = gcs_storage.Client.create_anonymous_client()
    storage_client.project = "demo-event-app"
else:
    # Production — vrai client GCS avec les credentials par défaut
    storage_client = gcs_storage.Client()
