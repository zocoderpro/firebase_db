# functions-rjp-jourj-firebase

## Topic Pub/Sub
`prod-rjp-jourj`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_JOURJ` | Email Jour J RJP 2026 (rappel jour même) | `type`, `email` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-rjp-jourj`
2. `main.py` décode le payload et valide les champs requis
3. Rendu HTML via `templates/jourj.html` (design RJP identique)
4. Envoi SMTP avec logo JPM en CID (`cid:rjp_jpm`)

**Caractéristiques :**
- Objet : `RJP 2026 : Jour J !`
- Rappel du lieu exact : Patio Ivato
- Lien Google Maps : `https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5`
- Accès : parking CCI, dernier étage
- Salutation : `Bonjour,` (pas de prénom, pas de genre)

## Exemples curl

### Créer le topic
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-jourj"
```

### RJP_JOURJ
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-jourj:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_JOURJ","email":"fehizororasosolo@gmail.com"}' | base64 -w0)\"}]}"
```

## Envoi en masse

Script `send_jourj_batch.py` : envoie à 157 contacts avec **10 secondes d'intervalle**.

```bash
cd functions-rjp-jourj-firebase
./venv/Scripts/python.exe send_jourj_batch.py
```

**Durée estimée :** 157 × 10s = **~26 minutes**

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `jourj_senders.py` | Logique métier, contenu inline |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates_handler.py` | Moteur de rendu de templates |
| `templates/jourj.html` | Template HTML de l'email |
| `templates/fragments/envelope_*.html` | Enveloppes HTML |
| `assets/rjp2026/jpm.png` | Logo JPM |
| `assets/logo.jpeg` | Logo Athena Event |
| `send_jourj_batch.py` | Script d'envoi en masse (10s intervalle) |

## Contenu de l'email

**Objet :** `RJP 2026 : Jour J !`

```
Bonjour,

RJP 2026 : Jour J ! Nous avons hâte de vous retrouver ce soir.

Nous souhaitons vous rappeler le lieu exact de l'événement :

Vous trouverez ici la localisation du Patio Ivato : https://maps.app.goo.gl/5x4qXxDoEZy8XXvt5

Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au dernier étage.

Nous vous prions de nous excuser pour ce second message et restons à votre disposition pour toute question.

À ce soir,
Bien cordialement,
L'équipe RJP 2026
```
