# functions-befiana-sms-firebase

## Topic Pub/Sub
`prod-sms-befiana-notifications`

## Types de SMS gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `SMS_BEFIANA_NOTIFICATION` | SMS Befiana (opérateur) | `type`, `phone`, `message` |
| `SMS_BEFIANA_OTP` | Code OTP Befiana | `type`, `phone`, `otp` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-sms-befiana-notifications`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Envoi SMS via l'api Befiana
4. Log du résultat (succès/échec)

## Exemples curl

### SMS_BEFIANA_NOTIFICATION
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-sms-befiana-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SMS_BEFIANA_NOTIFICATION","phone":"+261341234567","message":"Votre inscription est confirmée"}' | base64 -w0)\"}]}"
```

### SMS_BEFIANA_OTP
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-sms-befiana-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SMS_BEFIANA_OTP","phone":"+261341234567","otp":"123456"}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `sms_senders.py` | Logique métier, envoi SMS |
| `clients/befiana_client.py` | Client API Befiana |
| `config.py` | Constantes, variables d'environnement |
