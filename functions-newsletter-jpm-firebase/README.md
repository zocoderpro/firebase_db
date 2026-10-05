# functions-newsletter-jpm-firebase

## Topic Pub/Sub
`prod-newsletter-jpm`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `NEWSLETTER_JPM` | Newsletter JPM | `type`, `recipients[]`, `subject`, `content` |
| `NEWSLETTER_JPM_INVITATION` | Invitation newsletter JPM | `type`, `recipients[]`, `eventId` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-newsletter-jpm`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Rendu HTML avec template JPM (logo JPM, sponsors)
4. Envoi SMTP avec logo en CID

## Exemples curl

### NEWSLETTER_JPM
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-newsletter-jpm:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"NEWSLETTER_JPM","recipients":["test@gmail.com"],"subject":"Newsletter Octobre","content":"<p>Contenu de la newsletter</p>"}' | base64 -w0)\"}]}"
```

### NEWSLETTER_JPM_INVITATION
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-newsletter-jpm:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"NEWSLETTER_JPM_INVITATION","recipients":["test@gmail.com"],"eventId":"evt_123"}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `newsletter_senders.py` | Logique métier, contenu newsletters |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates/` | Templates HTML JPM |
