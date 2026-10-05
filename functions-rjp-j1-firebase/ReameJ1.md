ait. Le service accepte maintenant email + name (sans voucherCode), exactement comme dans votre exemple voucher.

Curl de test (topic prod-rjp-j1)
bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1:publish" \
  -H "Content-Type: application/json" \
  -d "{\"messages\":[{\"data\":\"$(echo -n '{"type":"RJP_J1_INFO","email":"zoclearmind@gmail.com","name":"Zo"}' | base64 -w0)\"}]}"

Ou avec le fichier prêt (même payload) :
bash
curl -X POST "http://localhost:8085/v1/projects/demo-event-app/topics/prod-rjp-j1:publish" \
  -H "Content-Type: application/json" \
  -d @test_rjp_j1_info.json


Ce qui a changé
- main.py : email accepté comme destinataire ; name lu (ou fullName, ou firstName+lastName).
- email_sender.py : salutation personnalisée « Bonjour Mahefa Ramandimbiarison, » (HTML + texte) ; sans name, retombe sur « Bonjour, ».
- test_rjp_j1_info.json : payload email + name ; README mis à jour.

Vérifié : rendu réel du MIME — salutation personnalisée présente en HTML et en texte, lien Maps intact, aucune trace de « voucher ». Compilation Python OK.

Note : le topic reste prod-rjp-j1 (isolé, comme convenu). Si vous préférez publier sur prod-registration-confirmed comme le voucher, dites-le — il faudrait alors ajouter ce topic au même main.py (un seul décorateur par fichier dans ce projet), ce qui reviendrait à mêler ce service à la logique email existante.