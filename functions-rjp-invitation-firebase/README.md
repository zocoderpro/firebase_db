# functions-rjp-invitation-firebase

## Topic Pub/Sub
`prod-rjp-invitation`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_INVITATION` | Invitation individuelle RJP | `type`, `email`, `firstName`, `lastName` |
| `RJP_INVITATION_BATCH` | Batch: 1 intro + N invitations | `type`, `email`, `firstName`, `lastName`, `qrTokens[]`, `qrCodes[]` |

## Fonctionnement

### RJP_INVITATION (simple)
1. Le backend Spring publie un message JSON sur le topic `prod-rjp-invitation`
2. `main.py` décode le payload et valide les champs requis
3. Génération du QR code en PNG, encodé en CID (`cid:qrcode`)
4. Rendu HTML via `templates/invitation_simple.html`
5. Envoi SMTP avec PDF programme complet en pièce jointe

### RJP_INVITATION_BATCH
1. Le backend Spring publie un message JSON avec `qrTokens[]` et `qrCodes[]`
2. `main.py` décode le payload et valide les champs requis
3. Envoi de N+1 emails :
   - Email 1 : Introduction (contenu de `email_introduction.txt`)
   - Emails 2..N+1 : N invitations singulières (contenu de `invitation_singulier.txt`)
4. Chaque invitation singulière contient :
   - QR code unique (inline, pas en attache)
   - Lien Google Maps (`maps_link`)
   - PDF programme complet en pièce jointe
5. Rendu HTML via `templates/invitation_batch.html`

## Exemples curl

### RJP_INVITATION (simple)
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-invitation:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_INVITATION","email":"Jimmyraf.tpmeuble@gmail.com","firstName":"Jimmy","lastName":"Rafaralahy","qrToken":"757623","fonction":"TP MEUBLE","entite":"","genre":"H"}' | base64 -w0)\"}]}"
```

### RJP_INVITATION_BATCH
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-invitation:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_INVITATION_BATCH","email":"groupement.pme@gmail.com","firstName":"Zo Nantenaina","lastName":"RANAIVOSON","qrTokens":["774118","447271","222451","534162","200291"],"qrCodes":["774118","447271","222451","534162","200291"],"fonction":"Présidente","entite":"GPMES","genre":"F","maps_link":"https://bit.ly/3VcDPvW"}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `invitation_senders.py` | Logique métier, contenu des invitations |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates/invitation_simple.html` | Template invitation individuelle |
| `templates/invitation_batch.html` | Template batch (intro + singuliers) |
| `assets/programme_rjp_complet.pdf` | PDF programme complet |
| `assets/rjp2026/jpm.png` | Logo JPM |

## Gestion du genre

| `genre` | Salutation | Formule de politesse |
|---------|------------|----------------------|
| `"H"` | `Monsieur [Nom] [Prénom]` | `Monsieur` |
| `"F"` | `Madame [Nom] [Prénom]` | `Madame` |
| vide/autre | `Madame/Monsieur [Nom] [Prénom]` | `Madame/Monsieur` |
