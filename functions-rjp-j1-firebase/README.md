# functions-rjp-j1-firebase

## Topic Pub/Sub
`prod-rjp-j1`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_J1_BROCHURE` | Brochure J1 (Journée 1) | `type`, `recipients[]`, `eventId` |
| `RJP_J1_REMINDER` | Rappel J1 | `type`, `recipients[]`, `eventDate` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-rjp-j1`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Rendu HTML avec template J1 (spécifique à la Journée 1)
4. Envoi SMTP avec logo en CID

## Exemples curl

### RJP_J1_BROCHURE
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_J1_BROCHURE","recipients":["test@gmail.com"],"eventId":"evt_123"}' | base64 -w0)\"}]}"
```

### RJP_J1_REMINDER
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_J1_REMINDER","recipients":["test@gmail.com"],"eventDate":"2026-10-15"}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `brochure_senders.py` | Logique métier, contenu J1 |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates/` | Templates HTML J1 |
