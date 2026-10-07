# functions-rjp-reminder-firebase

## Topic Pub/Sub
`prod-rjp-reminder`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_REMINDER_BOTH_DAYS` | Rappel événement 2 jours (J1 + J2) | `type`, `email`, `lastName` |
| `RJP_REMINDER_DAY2` | Rappel journée 2 uniquement | `type`, `email`, `lastName` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-rjp-reminder`
2. `main.py` décode le payload et valide les champs requis selon le `type`
3. Rendu HTML via `templates/reminder.html` (design RJP identique aux invitations)
4. Envoi SMTP avec logo JPM en CID (`cid:rjp_jpm`)

**Caractéristiques :**
- Pas de QR code, pas de PDF joint
- Lien Google Maps : `https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5` (Patio Ivato)
- Salutation : `Madame [Nom]` / `Monsieur [Nom]` / `Madame/Monsieur [Nom]` (pas de prénom)

## Exemples curl

### Créer le topic
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-reminder"
```

### RJP_REMINDER_BOTH_DAYS (rappel 2 jours)
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-reminder:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_REMINDER_BOTH_DAYS","email":"fehizororasosolo@gmail.com","lastName":"RANAIVOSON","genre":"F"}' | base64 -w0)\"}]}"
```

### RJP_REMINDER_DAY2 (rappel journée 2)
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-reminder:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_REMINDER_DAY2","email":"fehizororasosolo@gmail.com","lastName":"RANAIVOSON","genre":"F"}' | base64 -w0)\"}]}"
```

## Gestion du genre

| `genre` | Salutation | Formule de politesse |
|---------|------------|----------------------|
| `"H"` | `Monsieur [Nom]` | `Monsieur` |
| `"F"` | `Madame [Nom]` | `Madame` |
| vide/autre | `Madame/Monsieur [Nom]` | `Madame/Monsieur` |

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `reminder_senders.py` | Logique métier, contenus inline |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates_handler.py` | Moteur de rendu de templates |
| `templates/reminder.html` | Template HTML du rappel |
| `templates/fragments/envelope_*.html` | Enveloppes HTML |
| `assets/rjp2026/jpm.png` | Logo JPM |
| `assets/logo.jpeg` | Logo Athena Event |

## Contenu des emails

### RJP_REMINDER_BOTH_DAYS
```
Madame/Monsieur [Nom],

Nous avons le plaisir de vous rappeler que la Rentrée du Jeune Patronat 2026 approche à grands pas !

Cet événement se déroulera sur deux journées riches en échanges, en rencontres et en opportunités de networking avec l'ensemble de notre écosystème.

Nous nous réjouissons de vous accueillir à cette édition 2026 et restons à votre disposition pour toute question.

Vous trouverez ici la localisation du Patio Ivato : https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5

Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, Madame/Monsieur, l'expression de nos salutations distinguées.

Bien cordialement,
L'équipe de la Rentrée du Jeune Patronat 2026
```

### RJP_REMINDER_DAY2
```
Madame/Monsieur [Nom],

Nous vous rappelons que la deuxième journée de la Rentrée du Jeune Patronat 2026 aura lieu demain.

Cette journée sera l'occasion de poursuivre les échanges et de renforcer les liens avec l'ensemble de notre écosystème.

Au plaisir de vous retrouver pour cette deuxième journée !

Vous trouverez ici la localisation du Patio Ivato : https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5

Dans l'attente du plaisir de vous compter parmi nous, nous vous prions d'agréer, Madame/Monsieur, l'expression de nos salutations distinguées.

Bien cordialement,
L'équipe de la Rentrée du Jeune Patronat 2026
```
