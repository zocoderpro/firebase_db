# functions-sms-mapi-firebase

## Topic Pub/Sub
`prod-sms-mapi-notifications`

## Types de SMS gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `SMS_NOTIFICATION` | SMS de notification générique | `type`, `phone`, `message` |
| `SMS_OTP` | Code OTP par SMS | `type`, `phone`, `otp` |
| `SMS_REMINDER` | Rappel SMS | `type`, `phone`, `eventDate` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-sms-mapi-notifications`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Envoi SMS via l'api MAPI (opérateur Madagascar)
4. Log du résultat (succès/échec)

## Exemples curl

### SMS_NOTIFICATION
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-sms-mapi-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SMS_NOTIFICATION","phone":"+261341234567","message":"Votre inscription est confirmée"}' | base64 -w0)\"}]}"
```

### SMS_OTP
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-sms-mapi-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SMS_OTP","phone":"+261341234567","otp":"123456"}' | base64 -w0)\"}]}"
```

### SMS_REMINDER
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-sms-mapi-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SMS_REMINDER","phone":"+261341234567","eventDate":"2026-10-15"}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `sms_senders.py` | Logique métier, envoi SMS |
| `clients/mapi_client.py` | Client API MAPI |
| `config.py` | Constantes, variables d'environnement |
