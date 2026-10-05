# functions-rjp-j1

Cloud Function Firebase (Pub/Sub) — email **« Préparez votre venue le 8 octobre »**
aux participants inscrits au **jour 1** de la Rentrée du Jeune Patronat 2026 (RJP 2026).

Fonction volontairement isolée de `functions-email-firebase` (trop chargée) : un
codebase dédié, un topic dédié, un template figé co-brandé JPM.

## Structure

```
functions-rjp-j1-firebase/
├── main.py            # Point d'entrée Firebase + topic prod-rjp-j1
├── config.py          # SMTP + constantes RJP (liens, téléphone, sujet)
├── sender.py          # Envoi SMTP centralisé (+ pièces jointes)
├── attachments.py     # Chargement des pièces jointes (URL http(s) ou gs://)
├── email_sender.py    # Contenu de l'email (send_rjp_j1_info)
├── templates_handler.py
└── templates/         # Composants visuels (copie de functions-email-firebase)
```

## Topic

`prod-rjp-j1`

## Payload Pub/Sub

```json
{
  "type": "RJP_J1_INFO",
  "email": "mahefa.ramandimbiarison@basan.mg",
  "name": "Mahefa Ramandimbiarison",
  "subject": "RJP 2026 : Préparez votre venue le 8 octobre",
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
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1"

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1:publish" \
  -H "Content-Type: application/json" \
  -d @test_rjp_j1_info.json

  curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1:publish" \
  -H "Content-Type: application/json" \
  -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_J1_INFO","email":"zoclearmind@gmail.com","name":"zo coder"}' | base64 -w0)\"}]}"
```

`test_rjp_j1_info.json` (à la racine du dépôt) contient le payload encodé base64
prêt à l'emploi.

## Où modifier quoi

| Élément                         | Fichier / fonction                            |
|---------------------------------|-----------------------------------------------|
| Textes de l'email               | `email_sender.py` — `send_rjp_j1_info()`      |
| Liens Maps / WhatsApp / téléphone| `config.py` — `RJP_MAP_URL`, `RJP_WHATSAPP_URL`, `RJP_PHONE` |
| Sujet par défaut                | `config.py` — `RJP_SUBJECT`                   |
| Bandeau / sponsors RJP          | `templates/fragments/rjp2026_header.html`, `rjp2026_sponsors_footer.html` |
