### Install CloudSDK using winget
winget install --id Google.CloudSDK

winget list --id Google.CloudSDK


## Add gcloud SDK bin path to USER environment PATH
$gcloudBin = "C:\Users\danie\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$gcloudBin", "User")

## Login
gcloud auth application-default login
$env:GOOGLE_CLOUD_PROJECT="eridanus-gae"

Apoi porneste serverul:

$env:DEV_USER_EMAIL="iondaniel.ionescu@gmail.com"
$env:ALLOWED_USER_EMAIL="iondaniel.ionescu@gmail.com"
.\.venv\Scripts\python -m flask --app main run --debug


Accessing home page in power shell
Invoke-WebRequest -Uri http://127.0.0.1:5000/home -UseBasicParsing | Out-Null


$ $proc = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like
'*flask*--app*main*run*--debug*--no-reload*--port*5001*' }
$proc | Select-Object ProcessId, CommandLine
if ($proc) { $proc | ForEach-Object { Stop-Process -Id $_.ProcessId -Force } }


## Start app with local datastore (emulator)

1. Porneste emulatorul:

gcloud beta emulators datastore start --project="eridanus-gae" --host-port=localhost:8081

2. In alt shell, seteaza variabilele:

$env:DATASTORE_EMULATOR_HOST="localhost:8081"
$env:GOOGLE_CLOUD_PROJECT="eridanus-gae"
$env:DEV_USER_EMAIL="iondaniel.ionescu@gmail.com"
$env:ALLOWED_USER_EMAIL="iondaniel.ionescu@gmail.com"

3. Porneste app local:

.\.venv\Scripts\python -m flask --app main run --debug

Optional: daca vrei sa populezi date in emulator, trebuie sa le importi sau sa creezi manual (emulatorul porneste gol).



## deploy

Oh, man, it's working!! Imi vine sa te pup! Multumesc, mult! Cum fac deploymentul pe GAE.


• Super, ma bucur! Pentru deploy pe App Engine Standard (Python 3), pasii sunt:

  1. Asigura-te ca esti in backend si ai app.yaml setat corect.
  2. Autentificare si proiect:

  gcloud auth login
  gcloud config set project eridanus-gae

  gcloud app deploy

  4. Deschide aplicatia:

  gcloud app browse

  IAP
  Dupa deploy, activezi IAP si permiti acces doar pentru iondaniel.ionescu@gmail.com.

  Daca vrei, iti dau pasii exacti pentru IAP (prin consola GCP) si setarile recomandate.


› Da, te rog!


• Iata pasii clari pentru IAP (App Engine Standard):

  1. In Google Cloud Console, selecteaza proiectul eridanus-gae.
  2. Activeaza IAP:
  - Mergi la Security > Identity-Aware Proxy.
  - Daca apare un buton “Enable IAP”, apasa-l.

  3. Configureaza IAP pentru App Engine:
  - Activeaza “IAP” pe linia respectiva (toggle).

  4. Adauga acces pentru emailul tau:

  - In IAP, selecteaza App Engine app.
  - Click Add principal.
  - Introdu iondaniel.ionescu@gmail.com.
  - Rol: IAP-secured Web App User.

  5. Verifica accesul:

  - Deschide aplicatia din browser; trebuie sa fie cerut login cu contul tau Google.
  Optional (recomandat):

  - Mergi la OAuth consent screen si completeaza numele aplicatiei daca iti cere.
  - Verifica si IAM ca userul tau are rolurile necesare.


## Testare

  Ce am adăugat

  - requirements.txt include pytest.
  - tests/conftest.py verifică DATASTORE_EMULATOR_HOST și setează DATASTORE_PROJECT_ID dacă lipsește.
  - tests/test_repository_crud.py face create/read/update/delete pe Crunch.

  Cum rulezi

  1. Pornește emulatorul Datastore și setează env:

  set DATASTORE_EMULATOR_HOST=localhost:8081
  set DATASTORE_PROJECT_ID=test

  2. Rulează:

  pytest

  Fișiere create/modificate

  - requirements.txt
  - tests/conftest.py
  - tests/test_repository_crud.py

  Dacă vrei, pot adăuga și teste pentru rute Flask (cu auth IAP fake) sau pentru alte repo‑uri.