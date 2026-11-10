# functions-email-firebase

## Topic Pub/Sub
`prod-registration-confirmed`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `ACTIVATION_CODE` | Code d'activation de compte | `type`, `email`, `firstName`, `code`, `expiresAt`, `template` |
| `ACTIVATION_LINK` | Lien d'activation hôtesse | `type`, `userId`, `email`, `firstName`, `lastName`, `default_password`, `link` |
| `ACTIVATION_LINK_ORGANIZER` | Lien d'activation organisateur | `type`, `email`, `firstName`, `lastName`, `default_password`, `company_name`, `link` |
| `RESET_PASSWORD` | Réinitialisation mot de passe | `type`, `email`, `firstName`, `token`, `expiresAt`, `template` |
| `EVENT_AWAITING_APPROVAL` | Notification admin - événement en attente | `eventId`, `eventTitle`, `companyName`, `createdAt` |
| `EVENT_APPROVED` | Notification organisateur - événement approuvé | `companyName`, `eventId`, `eventTitle`, `eventStartDate`, `eventLocation`, `approvedAt` |
| `PARTICIPANT_INVITATION_KNOWN` | Invitation participant (connu) | `type`, `companyName`, `eventId`, `token`, `url`, `template` |
| `PARTICIPANT_INVITATION_UNKNOWN` | Invitation participant (inconnu) | `type`, `companyName`, `eventId`, `token`, `url`, `template` |
| `EVENT_INVITATION` | Invitation à s'inscrire (bouton « Confirmer ma participation ») | `type`, `email`, `fullName`, `eventTitle`, `url` |
| `EVENT_INVITATION` (GEM) | Invitation institutionnelle GEM | `type`, `email`, `fullName`, `eventTitle`, `url` + optionnels : `firstName`, `lastName`, `sexe`, `institution`, `role`, `eventDateLocation`, `eventSubtitle`, `programConnectTitle`, `programConnectTime`, `programRegemTitle`, `programRegemTime`, `rsvpText`, `confirmationText`, `contactLine`, `signatoryName`, `signatoryTitle`, `includePaperNote` |
| `REQUEST_OTP` | Code OTP accès liste participants | `otp` |
|| `EVENT_VOUCHER` | Voucher événement | `type`, `email`, `voucherCode` ||
|| `GEM_CHEQUE_RECEIVED` | Confirmation client réception chèque (template GEM) | `type`, `email`, `phone`, `company`, `eventTitle`, `ticketCount`, `totalAmount` ||
|| `GEM_CHEQUE_ADMIN_NOTICE` | Notification équipe GEM nouveau chèque (template GEM) | `type`, `email`, `clientEmail`, `phone`, `company`, `eventTitle`, `ticketCount`, `totalAmount` ||

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-registration-confirmed`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Dispatch vers la fonction d'envoi correspondante dans `email_senders.py`
4. Rendu HTML via le template unique `templates/email.html` (ou `templates/gem_event_invitation.html` pour les invitations GEM)
5. Envoi SMTP avec logo en CID (`cid:logo` ou `cid:gemlogo`)

## Exemples curl

### ACTIVATION_CODE
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"ACTIVATION_CODE\",\"email\":\"test@gmail.com\",\"firstName\":\"Jean\",\"code\":\"123456\",\"expiresAt\":\"30\",\"template\":\"default\"}' | base64 -w0)\"}]}"
```

### ACTIVATION_LINK
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"ACTIVATION_LINK\",\"userId\":\"usr_123\",\"email\":\"test@gmail.com\",\"firstName\":\"Jean\",\"lastName\":\"Rakoto\",\"default_password\":\"temp123\",\"link\":\"https://app.athena-event.com/activate/abc\"}' | base64 -w0)\"}]}"
```

### RESET_PASSWORD
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"RESET_PASSWORD\",\"email\":\"test@gmail.com\",\"firstName\":\"Jean\",\"token\":\"reset_abc123\",\"expiresAt\":\"15\",\"template\":\"default\"}' | base64 -w0)\"}]}"
```

### EVENT_APPROVED
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"EVENT_APPROVED\",\"companyEmail\":\"org@gmail.com\",\"companyName\":\"ACME\",\"eventId\":\"evt_123\",\"eventTitle\":\"Conférence 2026\",\"eventStartDate\":\"2026-10-15\",\"eventLocation\":\"Antananarivo\",\"approvedAt\":\"2026-09-01\"}' | base64 -w0)\"}]}"
```

### REQUEST_OTP
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"REQUEST_OTP\",\"destinataire\":\"test@gmail.com\",\"otp\":\"123456\"}' | base64 -w0)\"}]}"
```

### EVENT_INVITATION (GEM)
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"EVENT_INVITATION\",\"email\":\"test@gmail.com\",\"fullName\":\"Jean Rakoto\",\"eventTitle\":\"GEM-CONNECT & RE-GEM 2026\",\"url\":\"https://athena-event.com/accepteinvitation/evt123?registrationId=reg456\",\"firstName\":\"Jean\",\"lastName\":\"Rakoto\",\"sexe\":\"M\",\"institution\":\"ACME Corp\",\"role\":\"Directeur Général\",\"eventDateLocation\":\"Jeudi 19 novembre 2026 · Novotel Convention & SPA Alarobia\",\"eventSubtitle\":\"Fahatokisana – Confiance · Perspectives économiques 2027\",\"programConnectTitle\":\"GEM-CONNECT\",\"programConnectTime\":\"09h00 - 12h30\",\"programRegemTitle\":\"RE-GEM\",\"programRegemTime\":\"18h30 - 22h00\",\"rsvpText\":\"Nous vous serions reconnaissants de bien vouloir nous faire part de votre réponse avant le 10 novembre 2026.\",\"confirmationText\":\"Une fois votre présence confirmée, votre pass d\\'accès personnel avec QR code vous sera adressé par e-mail.\",\"contactLine\":\"Pour toute information : protocol@gem.mg\",\"signatoryName\":\"Ravo Razafindrakoto\",\"signatoryTitle\":\"Président du GEM\",\"includePaperNote\":true}' | base64 -w0)\"}]}"
```

### GEM_CHEQUE_RECEIVED
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"GEM_CHEQUE_RECEIVED\",\"email\":\"client@gmail.com\",\"phone\":\"+261 34 00 000 00\",\"company\":\"ACME Corp\",\"eventTitle\":\"GEM-CONNECT 2026\",\"ticketCount\":5,\"totalAmount\":500000}' | base64 -w0)\"}]}"
```

### GEM_CHEQUE_ADMIN_NOTICE
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{\"type\":\"GEM_CHEQUE_ADMIN_NOTICE\",\"email\":\"admin@gem.mg\",\"clientEmail\":\"client@gmail.com\",\"phone\":\"+261 34 00 000 00\",\"company\":\"ACME Corp\",\"eventTitle\":\"GEM-CONNECT 2026\",\"ticketCount\":5,\"totalAmount\":500000}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `email_senders.py` | Logique métier, contenu des emails |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates/email.html` | Template HTML unique (design AthenaEvent) |
| `templates/gem_event_invitation.html` | Template institutionnel GEM |
| `templates/GEM_CHEQUE/cheque_received.html` | Template GEM confirmation réception chèque |
| `templates/GEM_CHEQUE/cheque_admin_notice.html` | Template GEM notification admin chèque |
| `templates_handler.py` | Moteur de rendu : `{{VAR}}`, `<!--IF:X-->`, `<!--EACH:X-->` |
