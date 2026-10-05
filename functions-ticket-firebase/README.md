# functions-ticket-firebase

## Topic Pub/Sub
`prod-email-notifications`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `EVENT_REGISTRATION_CONFIRMED` | Billet avec QR code (premier envoi) | `type`, `email`, `firstName`, `lastName`, `eventId`, `qrToken` |
| `RESEND_REGISTRATION_CONFIRMED` | Renvoi billet (avec badge ZPL) | `type`, `email`, `firstName`, `lastName`, `eventId`, `qrToken` |
| `RESEND_REGISTRATION_CONFIRMED_INVITED` | Renvoi billet invité | `type`, `email`, `firstName`, `lastName`, `eventId`, `qrToken` |
| `EVENT_REGISTRATION_CONFIRMED_MULTITICKET` | Multi-billets (1 badge ZPL + N QR) | `type`, `email`, `firstName`, `lastName`, `eventId`, `qrTokens[]` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-email-notifications`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Génération du badge ZPL (imprimante Zebra iT4S, 300 DPI) via `pdf_generator.py`
4. Génération du QR code en PNG, encodé en CID (`cid:qrcode`)
5. Envoi SMTP avec billet HTML + badge ZPL en pièce jointe

## Exemples curl

### EVENT_REGISTRATION_CONFIRMED
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-email-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_REGISTRATION_CONFIRMED","email":"test@gmail.com","firstName":"Jean","lastName":"Rakoto","eventId":"evt_123","qrToken":"qrt_abc123"}' | base64 -w0)\"}]}"
```

### RESEND_REGISTRATION_CONFIRMED
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-email-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RESEND_REGISTRATION_CONFIRMED","email":"test@gmail.com","firstName":"Jean","lastName":"Rakoto","eventId":"evt_123","qrToken":"qrt_abc123"}' | base64 -w0)\"}]}"
```

### EVENT_REGISTRATION_CONFIRMED_MULTITICKET
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-email-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_REGISTRATION_CONFIRMED_MULTITICKET","email":"test@gmail.com","firstName":"Jean","lastName":"Rakoto","eventId":"evt_123","qrTokens":["qrt_001","qrt_002","qrt_003"]}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `ticket_senders.py` | Logique métier, contenu des billets |
| `pdf_generator.py` | Génération badge ZPL (Zebra iT4S) |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates/` | Templates HTML des billets |
