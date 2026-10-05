# functions-brochure-firebase

## Topic Pub/Sub
`prod-event-ended`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `BROCHURE` | Brochure événement (1-3 templates) | `type`, `recipients[]`, `staticTemplateNum` |
| `EVENT_REGISTRATION_REQUEST_SECOND_CONFIRMATION` | 2e confirmation inscription | `type`, `recipients[]` |
| `EVENT_THANK_YOU` | Remerciement post-événement | `type`, `destinataire` |
| `CONTACT_REQUEST` | Demande de contact | `type`, `destEmail` |
| `ACCEPT_CONTACT_REQUEST` | Acceptation contact | `type`, `destEmail` |
| `REMINDER` | Rappel événement | `type`, `recipients[]` |
| `CUSTOM_EMAIL` | Email personnalisé | `type`, `recipient` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-event-ended`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Rendu HTML via templates complets (fichiers `.html` par type)
4. Envoi SMTP avec logo en CID

## Exemples curl

### BROCHURE
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-event-ended:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"BROCHURE","recipients":["test@gmail.com"],"staticTemplateNum":1}' | base64 -w0)\"}]}"
```

### EVENT_THANK_YOU
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-event-ended:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_THANK_YOU","destinataire":"test@gmail.com"}' | base64 -w0)\"}]}"
```

### CONTACT_REQUEST
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-event-ended:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"CONTACT_REQUEST","destEmail":"test@gmail.com"}' | base64 -w0)\"}]}"
```

### REMINDER
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-event-ended:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"REMINDER","recipients":["test@gmail.com"]}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `brochure_senders.py` | Logique métier, contenu des brochures |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates/` | Templates HTML complets par type |
