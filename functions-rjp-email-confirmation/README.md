# functions-rjp-email-confirmation

Cloud Function Firebase (Pub/Sub) — email **« Confirmez votre présence »**
aux participants inscrits à la Rentrée du Jeune Patronat 2026 (RJP 2026).

Fonction volontairement isolée de `functions-email-firebase` (trop chargée) : un
codebase dédié, un topic dédié, un template figé co-brandé JPM.

## Structure

```
functions-rjp-email-confirmation/
├── main.py            # Point d'entrée Firebase + topic prod-rjp-email-confirmation
├── config.py          # SMTP + constantes RJP (liens, téléphone, sujet)
├── sender.py          # Envoi SMTP centralisé (+ pièces jointes)
├── attachments.py     # Chargement des pièces jointes (URL http(s) ou gs://)
├── email_sender.py    # Contenu de l'email (send_rjp_email_confirmation)
├── templates_handler.py
└── templates/         # Composants visuels (copie de functions-email-firebase)
```

## Topic

`prod-rjp-email-confirmation`

## Payload Pub/Sub

```json
{
  "type": "RJP_EMAIL_CONFIRMATION",
  "email": "mahefa.ramandimbiarison@basan.mg",
  "name": "Mahefa Ramandimbiarison",
  "subject": "RJP 2026 : Confirmez votre présence",
  "attachments": ["https://.../programme.pdf", "gs://bucket/plan.pdf"]
}
```

- `email` : destinataire (une chaîne). Peut aussi être `recipients` (liste ou chaîne),
  `destinataire` ou `destEmail`.
- `name` : optionnel — nom affiché dans la salutation ("Bonjour Mahefa Ramandimbiarison,").
  Peut aussi être `fullName`, ou `firstName` + `lastName`. Sans nom : "Bonjour,".
- `subject` : optionnel (défaut `RJP_SUBJECT` dans `config.py`).
- `attachments` : optionnel (URL http(s) ou `gs://`). Si absent, l'email part sans
  pièce jointe.

## Tester sur l'émulateur

Créer le topic une fois, puis publier le payload de test :

```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-email-confirmation"

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-email-confirmation:publish" \
  -H "Content-Type: application/json" \
  -d @test_rjp_email_confirmation.json
  

  curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-email-confirmation:publish" \
  -H "Content-Type: application/json" \
  -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_EMAIL_CONFIRMATION","email":"zoclearmind@gmail.com","name":"zo coder"}' | base64 -w0)\"}]}"
```

`test_rjp_email_confirmation.json` (à la racine du dépôt) contient le payload encodé base64
prêt à l'emploi.

## Où modifier quoi

| Élément                         | Fichier / fonction                                    |
|---------------------------------|-------------------------------------------------------|
| Textes de l'email               | `email_sender.py` — `send_rjp_email_confirmation()`   |
| Liens Maps / WhatsApp / téléphone| `config.py` — `RJP_MAP_URL`, `RJP_WHATSAPP_URL`, `RJP_PHONE` |
| Sujet par défaut                | `config.py` — `RJP_SUBJECT`                           |
| Bandeau / sponsors RJP          | `templates/fragments/rjp2026_header.html`, `rjp2026_sponsors_footer.html` |
