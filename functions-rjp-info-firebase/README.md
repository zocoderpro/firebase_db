# functions-rjp-info-firebase

## Topic Pub/Sub
`prod-rjp-info`

## Types d'emails gérés

| Type | Description | Champs requis |
|------|-------------|---------------|
| `RJP_INFO` | Email d'informations utiles RJP 2026 (8-9 octobre) | `type`, `email`, `lastName` |

## Fonctionnement

1. Le backend Spring publie un message JSON sur le topic `prod-rjp-info`
2. `main.py` décode le payload et valide les champs requis
3. Rendu HTML via `templates/info.html` (design RJP identique)
4. Envoi SMTP avec logo JPM en CID (`cid:rjp_jpm`)

**Caractéristiques :**
- Contenu complet : programme, plan du lieu, restauration, badges, panels, WhatsApp, replay
- Bouton Google Maps centré : "Ouvrir dans Google Maps"
- Lien formulaire panels J2
- Lien espace WhatsApp
- Salutation : `Madame [Nom]` / `Monsieur [Nom]` / `Madame/Monsieur [Nom]` (pas de prénom)

## Exemples curl

### Créer le topic
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-info"
```

### RJP_INFO
```bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-info:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_INFO","email":"fehizororasosolo@gmail.com","lastName":"RANAIVOSON","genre":"F"}' | base64 -w0)\"}]}"
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
| `info_senders.py` | Logique métier, contenu inline |
| `sender.py` | Construction MIME, envoi SMTP |
| `config.py` | Constantes, variables d'environnement |
| `templates_handler.py` | Moteur de rendu de templates |
| `templates/info.html` | Template HTML de l'email |
| `templates/fragments/envelope_*.html` | Enveloppes HTML |
| `assets/rjp2026/jpm.png` | Logo JPM |
| `assets/logo.jpeg` | Logo Athena Event |

## Contenu de l'email

```
Bonjour,

Nous avons hâte de vous accueillir à la RJP 2026, les 8 et 9 octobre au Patio Ivato.

Vous trouverez en pièces jointes le programme complet et le plan du lieu pour préparer votre venue.

Vous trouverez ici la localisation du Patio Ivato [BOUTON GOOGLE MAPS]

Des éléments de sécurité vous guideront vers le parking qui nous est dédié à la CCI, et il faudra marcher vers l'immeuble du Patio. Nous vous attendons au dernier étage.

Le retrait de vos badges se fait le jour J. Vous trouverez à l'entrée de l'espace RJP un check-in qui vous permettra de retirer votre badge en présentant votre QR Code ou votre adresse mail.

Sont inclus dans votre pass toute la restauration : cocktails, vin de bienvenue, viennoiserie au petit déjeuner, lunchbox pour le déjeuner et cocktail de clôture. Vous trouverez sur place de quoi vous rafraîchir auprès des stands de boissons (payant).

Pour participer aux sondages en direct pendant l'événement, assurez-vous de disposer d'une connexion Internet sur votre téléphone. Si vous souhaitez prendre part à la Battle IA du Jour 2, apportez un ordinateur portable chargé et son chargeur.

Pour le Jour 2, choisissez dès maintenant les panels auxquels vous souhaitez assister via ce formulaire :
https://docs.google.com/forms/d/e/1FAIpQLSdl6Q94MR2xtfMSdx1vTWvGka1ONR3OyUyG3E9s_xUTouXbNw/viewform?usp=header

Pour recevoir les actualités et rappels de la RJP directement sur votre téléphone, vous pouvez rejoindre notre espace WhatsApp :
https://chat.whatsapp.com/Dsj23q5yNWZ1Sz28YXn4ad?mode=gi_t

Vous ne pourrez pas assister à toutes les masterclass le 9 octobre : pas de panique, un lien Drive vous sera communiqué a posteriori pour visionner les replay et recevoir les documents des intervenants.

Tous les masterclass et les panels commenceront à l'heure.

Accueil J1 : 17h
Accueil J2 : 8h

Pour toute question avant l'événement : +261 34 04 105 06

À très bientôt,
L'équipe RJP 2026
```
