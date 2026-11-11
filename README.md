## Installation varible python et lance projet cloud fuction
```bash
python -m venv venv
```

## l’activer :
```bash
venv\Scripts\activate
```

## Installer toutes les dépendances listées dans le fichier requirements.txt
```bash
pip install -r requirements.txt
```

## Login pour emulator firebase local

```bash
npx firebase init
```

# Installer dependecie python

```bash
pip install -r requirements.txt
```

# et lancer sur commande
```bash

 npx firebase emulators:start --project demo-event-app --import=./emulator-data --export-on-exit=./emulator-data
 npx firebase emulators:start --project demo-event-app --import=./data_prod --export-on-exit=./data_prod
 npx firebase emulators:start --project demo-event-app --import=./staging_data --export-on-exit=./staging_data
```

# Créer les topics
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/notifications-inbound"
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/topics/sse-delivery-topic"
```

# Créer les subscriptions
```bash
curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/subscriptions/notifications-inbound-sub" \
  -H "Content-Type: application/json" \
  -d '{"topic": "projects/demo-event-app/topics/notifications-inbound", "ackDeadlineSeconds": 10}'

curl -X PUT "http://localhost:8085/v1/projects/demo-event-app/subscriptions/sse-delivery-sub" \
  -H "Content-Type: application/json" \
  -d '{"topic": "projects/demo-event-app/topics/sse-delivery-topic", "ackDeadlineSeconds": 10}'
```

# Creation variabale local en spring pas ici

```bash
$env:FIRESTORE_EMULATOR_HOST="localhost:8082"                        
$env:SPRING_PROFILES_ACTIVE="dev"
```

```bash
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}
```

```bash
echo $env:GOOGLE_CLIENT_ID

mvn spring-boot:run


 ./mvnw spring-boot:run

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish"   -H "Content-Type: application/json"   -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_VOUCHER","email":"zaraalamadagascar@gmail.com","voucherCode":"XENNYSSX"}' | base64 -w0)\"}]}"  


curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish"   -H "Content-Type: application/json"   -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_VOUCHER","email":"lovatiana.ramandraiarisoa@basan.mg","voucherCode":"C6TQVMJH"}' | base64 -w0)\"}]}"

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish"   -H "Content-Type: application/json"   -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_VOUCHER","email":"ramandimbiarison@basan.mg","voucherCode":"ZN9MF7JN"}' | base64 -w0)\"}]}"

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-registration-confirmed:publish"   -H "Content-Type: application/json"   -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"EVENT_VOUCHER","email":"mahefa.ramandimbiarison@basan.mg","voucherCode":"5WU37RNR"}' | base64 -w0)\"}]}"

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-email-notifications:publish"   -H "Content-Type: application/json"   -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SEND_FACTURE_GEM_EVENT","email":"mahefa@gmail.com", "registrationId": "", "userFirstName": "Rakoto", "userLastName": "Nary", "qrCodeToken": "", "totalAmount": 247824" }' | base64 -w0)\"}]}"

curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-email-notifications:publish" \
-H "Content-Type: application/json" \
-d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"SEND_FACTURE_GEM_EVENT","email":"mahefa@gmail.com","userFirstName":"Rakoto","userLastName":"Nary","eventTitle":"GEM CONNECT & RE-GEM 2026","totalAmount":247824,"raisonSociale":"Entreprise XYZ","adress":"Antananarivo","nif":"1234567890","stat":"12345678901234",  "qrCodeToken": "", "registrationId": ""}' | base64 -w0)\"}]}"