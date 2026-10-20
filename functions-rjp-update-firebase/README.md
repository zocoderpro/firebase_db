# functions-rjp-update-firebase

## Topic Pub/Sub
`prod-rjp-update`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_UPDATE` | Email de mise à jour du programme RJP 2026 | `type`, `email` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-rjp-update`
2. `main.py` décode le payload et valide les champs requis
3. Rendu HTML via `templates/update.html` (design RJP identique)
4. Envoi SMTP avec logo JPM en CID (`cid:rjp_jpm`) + PDF programme en pièce jointe

**Caractéristiques :**
- Objet : `RJP 2026 : Mise à jour du programme`
- Annonce : discours de l'Ambassadeur annulé
- PDF joint : `assets/programme_rjp_update.pdf` (Programme Complet J1 J2 compressé)
- Salutation : `Bonjour,` (pas de prénom, pas de genre)

## Exemples curl

### Créer le topic
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-update"
```

### RJP_UPDATE
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-update:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_UPDATE","email":"fehizororasosolo@gmail.com"}' | base64 -w0)\"}]}"
```

## Envoi en masse

Script `send_update_batch.py` : envoie à 157 contacts avec **10 secondes d'intervalle**.

```bash
cd functions-rjp-update-firebase
./venv/Scripts/python.exe send_update_batch.py
```

**Durée estimée :** 157 × 10s = **~26 minutes**

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Pub/Sub, validation, dispatch |
| `update_senders.py` | Logique métier, contenu inline, chargement PDF |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates_handler.py` | Moteur de rendu de templates |
| `templates/update.html` | Template HTML de l'email |
| `templates/fragments/envelope_*.html` | Enveloppes HTML |
| `assets/programme_rjp_update.pdf` | PDF programme mis à jour |
| `assets/rjp2026/jpm.png` | Logo JPM |
| `assets/logo.jpeg` | Logo Athena Event |
| `send_update_batch.py` | Script d'envoi en masse (10s intervalle) |

## Contenu de l'email

**Objet :** `RJP 2026 : Mise à jour du programme`

```
Bonjour,

Suite à notre précédent message, nous souhaitons vous informer d'une modification du programme de la RJP 2026, qui a lieu ce soir.

Le discours de l'Ambassadeur est annulé.

Le programme a donc été ajusté en conséquence :

Vous trouverez en pièce jointe le programme mis à jour.

Nous vous prions de nous excuser pour ce changement et restons à votre disposition pour toute question.

À ce soir,
Bien cordialement,
L'équipe RJP 2026
```
