# AGENTS.md — firebase_db (Athena Event)

Monorepo des Cloud Functions **Python 3.12 (Gen2)** d'Athena Event, pilotées par
Pub/Sub : envoi d'emails (confirmation, billet, newsletter), SMS, génération de
badges et brochures. Chaque dossier `functions-*-firebase/` est un *codebase*
indépendant déclaré dans `firebase.json`. Il n'y a **ni backend applicatif ni
base de données** ici : les fonctions ne font que réagir à des messages Pub/Sub
publiés par le backend Spring (projet `athena`, hors de ce dépôt).

## Environnement de dev

Chaque codebase a son **propre** `venv/` (firebase-tools active
`functions-<service>-firebase/venv/Scripts/activate.bat` en dur — un venv à la
racine du dépôt ne sert à rien). Créer les 7 :

```bash
cd functions-<service>-firebase
uv venv --python 3.12 venv          # ou : python -m venv venv
uv pip install --python venv/Scripts/python.exe -r requirements.txt
```

Node 22 + `firebase-tools` 15.x requis (installé via `package.json`).

## Lancer l'émulateur

```bash
npm start
# équivaut à :
npx firebase emulators:start --project demo-event-app --import=./emulator-data --export-on-exit=./emulator-data
```

Ports (voir `firebase.json`) : functions `5001`, firestore `8082`, storage `9199`,
pubsub `8085`, UI `4000`. Projet émulé : `demo-event-app`.

Les **topics et subscriptions ne sont pas créés automatiquement** : les créer une
fois via les `curl` documentés dans `README.md` (topics `notifications-inbound`,
`sse-delivery-topic`, puis `prod-registration-confirmed`, etc.).

## Tests et lint

Aucun. `npm test` est un placeholder (`echo "Error: no test specified" && exit 1`).
Il n'existe ni CI, ni linter, ni config de tests. Tester = publier un message sur
l'émulateur Pub/Sub (voir `test_*.json`, `payload.json`) et lire les logs.

Publier un payload local :

```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/<topic>:publish" \
  -H "Content-Type: application/json" \
  -d "{\"messages\":[{\"data\":\"$(base64 -w0 < test_event_voucher.json)\"}]}"
```

## Architecture des fonctions

| Codebase (`firebase.json`)  | Dossier                        | Topic écouté                     |
|-----------------------------|--------------------------------|----------------------------------|
| `email-service`             | `functions-email-firebase`     | `prod-registration-confirmed`    |
| `ticket-service`            | `functions-ticket-firebase`    | `prod-email-notifications`       |
| `brochure-service`          | `functions-brochure-firebase`  | `prod-event-ended`               |
| `sms-mapi-test-service`     | `functions-sms-mapi-firebase`  | `prod-sms-mapi-notifications`    |
| `sms-befiana-test-service`  | `functions-befiana-sms-firebase`| `prod-sms-befiana-notifications`|
| `newsletter-jpm-service`    | `functions-newsletter-jpm-firebase`| `prod-newsletter-jpm`        |
| `rjp-j1-service`            | `functions-rjp-j1-firebase`    | `prod-rjp-j1`                    |

`functions-ticket-firebase2/` est une **ancienne version legacy** (non déclarée
dans `firebase.json`) — ne pas la modifier.

## Conventions observées

- **Dispatch par `type`** : chaque `main.py` lit `event.data.message.json`,
  valide une liste `required_fields`, puis branche sur `data["type"]` en
  MAJUSCULES_SNAKE (`ACTIVATION_CODE`, `EVENT_VOUCHER`, `REMINDER_J12`…).
  **Ajouter un type** = ajouter sa validation + son dispatch dans le `main.py`
  du service concerné, puis la fonction d'envoi dans `email_sender(s).py`.
- Structure d'un service : `main.py` (entrée + dispatch), `config.py` (constantes
  + `os.environ.get`), `sender.py`/`email_sender(s).py` (MIME + SMTP),
  `templates/` (HTML), `clients/` (clients API SMS). Noms de fichiers et de
  fonctions en `snake_case`.
- Blocs délimités par des cadres ASCII : `ZONE DESIGN — MODIFIABLE LIBREMENT`
  vs `ZONE LOGIQUE — NE PAS MODIFIER SAUF DEV CONFIRMÉ`. Respecter la frontière.
- Emails : HTML + version texte, images **inline en CID** (`cid:logo`,
  `cid:qrcode`) — jamais d'URL externe pour le logo/QR. Commentaires et logs en
  français.
- Commits : messages en français, impératif descriptif (« Ajout de… », « Correction… »),
  pas de Conventional Commits.

## Pièges

- **Aucune fonction ne se charge sans `venv/` dans son dossier** : firebase-tools
  échoue avec `spawn "...\functions-<service>-firebase\venv\Scripts\activate.bat"
  ENOENT` et l'émulateur affiche quand même « All emulators ready » avec 0
  fonction. Symptôme trompeur : vérifier les lignes `functions: Loaded functions
  definitions from source: ...` dans les logs avant de publier.
- `functions-ticket-firebase/.env.local` est **tracké par git** (`git ls-files`)
  et contient des secrets (tokens Postmark/Bird). Ne pas y ajouter de nouveaux
  secrets ; le signaler si demandé de le modifier.
- `config.py` **ne doit jamais lever d'exception à l'import** pour une variable
  manquante : l'émulateur importe `main.py` en phase *discovery* sans `.env.local`.
  Valider les variables dans la fonction, au moment de la requête.
- Ne pas détecter le local via `K_SERVICE` : l'émulateur Gen2 le définit aussi.
  Utiliser `FUNCTIONS_EMULATOR == "true"` (voir `storage.py`, `pdf_generator.py`).
- `send_ticket_email_with_qr()` code en dur le port `587` au lieu de `SMTP_PORT`.
- Badge ticket = **ZPL** pour imprimante Zebra iT4S (pas de PDF) ; positions en
  dots 300 DPI dans `pdf_generator.py::_build_zpl()`. Détails dans
  `functions-ticket-firebase/README.md`.
- Chaque service a son propre `requirements.txt` ; les versions diffèrent
  légèrement entre dossiers.
