import os

# NOTE IMPORTANTE (specifique a l'emulateur Firebase Functions Python) :
# contrairement a cloud-functions/source/* (functions_framework), ce fichier
# ne doit JAMAIS lever d'exception au moment de l'import pour une variable
# manquante. L'emulateur importe main.py une premiere fois en phase de
# "discovery" (generation de functions.yaml) avec un environnement restreint
# qui ne contient PAS encore .env.local -- .env.local n'est injecte que plus
# tard, au moment de traiter une vraie requete. Une variable obligatoire ici
# ferait donc echouer le chargement de TOUT le codebase, pas seulement
# l'appel. La validation de presence se fait donc a la place dans main.py,
# au moment de traiter la requete (voir send_sms_befiana_test_http). Meme piege deja
# rencontre et corrige sur functions-sms-mapi-firebase/config.py.

# URL de base de l'API Befiana (SMS by Befiana).
BEFIANA_BASE_URL = os.environ.get("BEFIANA_BASE_URL", "https://api.befiana.cloud")

# Cle API Befiana -- authentification statique, pas de login/token comme
# MAPI. En local, valeur lue dans .env.local (chargee automatiquement par
# l'emulateur Firebase Functions au moment de traiter une requete). En
# deploiement reel, a fournir via des secrets Firebase
# (firebase functions:secrets:set) plutot que des env vars en clair -- non
# couvert par cette version "emulateur local".
BEFIANA_API_KEY = os.environ.get("BEFIANA_API_KEY")

# Cle partagee attendue dans le header "X-Api-Key" de chaque requete HTTP
# entrante. Protection minimale, pour eviter qu'un tiers ne declenche des
# envois de SMS et ne consomme le credit pendant la phase de test.
API_SHARED_KEY = os.environ.get("API_SHARED_KEY")
