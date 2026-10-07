# functions-rjp-erratum-firebase

## Topic Pub/Sub
`prod-rjp-erratum`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_ERRATUM` | Email d'erratum RJP 2026 (précision sur la localisation) | `type`, `email`, `lastName` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-rjp-erratum`
2. `main.py` décode le payload et valide les champs requis
3. Rendu HTML via `templates/erratum.html` (design RJP identique)
4. Envoi SMTP avec logo JPM en CID (`cid:rjp_jpm`)

**Caractéristiques :**
- Précision sur le lieu exact : Patio Ivato
- Lien Google Maps : `https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5`
- Accès : parking CCI, dernier étage
- Salutation : `Bonjour [Nom],` (pas de prénom, pas de genre)

## Exemples curl

### Créer le topic
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-erratum"
```

### RJP_ERRATUM
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-erratum:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_ERRATUM","email":"fehizororasosolo@gmail.com","lastName":"RANAIVOSON"}' | base64 -w0)\"}]}"
```

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `erratum_senders.py` | Logique métier, contenu inline |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates_handler.py` | Moteur de rendu de templates |
| `templates/erratum.html` | Template HTML de l'email |
| `templates/fragments/envelope_*.html` | Enveloppes HTML |
| `assets/rjp2026/jpm.png` | Logo JPM |
| `assets/logo.jpeg` | Logo Athena Event |

## Contenu de l'email

**Objet :** `[Erratum] RJP 2026 - Précision sur la localisation`

```
Bonjour [Nom],

Suite à notre précédent message concernant la RJP 2026, nous souhaitons vous apporter une précision importante concernant le lieu exact de l'événement.

Le lieu exact est le suivant :

Vous trouverez ici la localisation du Patio Ivato : https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5

Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au dernier étage.

Nous vous prions de nous excuser pour ce rectificatif et restons à votre disposition pour toute question.

Bien cordialement,
L'équipe RJP 2026
```
