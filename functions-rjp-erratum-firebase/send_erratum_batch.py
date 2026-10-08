"""Script d'envoi en masse de l'erratum RJP 2026.

Envoie l'email d'erratum à tous les contacts avec 20 secondes d'intervalle.
Usage : ./venv/Scripts/python.exe send_erratum_batch.py
"""
import logging
import sys
import os
import smtplib
import time

# Charger le fichier .env s'il existe
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip()
                # Retirer les guillemets autour de la valeur (SMTP_HOST = "smtp.zeptomail.com")
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]
                os.environ.setdefault(key.strip(), value)

# Ajouter le dossier parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(__file__))

from erratum_senders import send_rjp_erratum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ──────────────────────────────────────────────────────────────
# LISTE DES CONTACTS (157)
# ──────────────────────────────────────────────────────────────
CONTACTS = [
    "direction.mailaka.manambina@gmail.com",
    "felana@ivana.mg",
    "mbolatiana.stephanie@ivana.mg",
    "cravoson25@gmail.com",
    "info@stcv.pro",
    "niriana.rajaonera@bmoi.mg",
    "Simon.TOVONDRAINY@bmoi.mg",
    "Hasinavalona.ANDRIANANTENAINA@bmoi.mg",
    "Jimmyraf.tpmeuble@gmail.com",
    "i.ramanarina@pamf.mg",
    "jonathan.rahamefy@gmail.com",
    "nrajaonary@insidecapital.net",
    "Hanta.Rakotovao@bni.mg",
    "nralaimanisa@gmail.com",
    "houssenmebobaly@malakass.com",
    "tovo.ratsimba@extrend-consulting.org",
    "dedem@weaxiom.com",
    "Andrianaivo.r@ngs.mg",
    "yoan.rab@gmail.com",
    "lucnouvian1@gmail.com",
    "rakotoarimanga.michael@npakadin.mg",
    "mathilde@hscm-conseil.com",
    "alexandre@adcrafter.studio",
    "christophe@rise.work",
    "rajaobelinamarc@gmail.com",
    "kenny@esf.mg",
    "andy.rak@terra.mg",
    "ceo@takamoa.com",
    "alexandre@viziocraft.com",
    "rramiandrisoa@fthmconsulting.com",
    "stephanie.rakotomalala@masoala-laboratoire.com",
    "e.cotsoyannis@miarakap.com",
    "david@clearmind-analytics.com",
    "dps.datapilotsolutions@gmail.com",
    "adrian.chindris@gmail.com",
    "Nirintsoa.RATOVOHERY@bmoi.mg",
    "Herymiadana@yahoo.fr",
    "rakotoniainamita@gmail.com",
    "tsanta.ramanitra@fiaro.net",
    "maqua.direction@gmail.com",
    "za.joella@gmail.com",
    "tsituramm@gmail.com",
    "tahina.rivoarilala@gmail.com",
    "t.randrianarivofidele@gmail.com",
    "srasaliboarivony@gmail.com",
    "rnirinafanomezantsoa@gmail.com",
    "ravbrenda@gmail.com",
    "ratsitoarison@gmail.com",
    "raheliarisoaniaina@gmail.com",
    "raharijaonahenintsoa1@gmail.com",
    "ornelladechenhasimbola@gmail.com",
    "narindranacy42@gmail.com",
    "mialinarindra@sakafo-madagascar.com",
    "marinajackierandria@gmail.com",
    "manantsoar@gmail.com",
    "lucasrasolofoniaina@gmail.com",
    "joanirina@gmail.com",
    "jimalison.giovanni@gmail.com",
    "fitahianafinaritra@gmail.com",
    "Fenofitianomenjanahary1@gmail.com",
    "fannykotonirina@gmail.com",
    "davvpanther@gmail.com",
    "barkatmatazaky@gmail.com",
    "assotohana@gmail.com",
    "armandorakotomanana2@gmail.com",
    "acep.dg@acep.mg",
    "Patrice.MAZZEI@bni.mg",
    "christel.chesne@mg.sanlamallianz.com",
    "fofana.hassan65@icloud.com",
    "g.ratsimbazafy@pamf.mg",
    "khedija.benothman@totalenergies.com",
    "marie-christina.kolo@ppi-groupesos.org",
    "rindra.razafindrazaka@hamac.mg",
    "sg@okapi.mg",
    "jamina@yanaecosysteme.com",
    "sanda@agencecoreali.com",
    "houssen@ucomad.mg",
    "patrick.razafindrafito@fiaro.net",
    "steve@moramarket.mg",
    "fano.torio@gmail.com",
    "nynyantsah@gmail.com",
    "heritinamanantsoa@gmail.com",
    "sandy.rafidison@stellar-ix.com",
    "loic.rakotoarisoa@stellar-ix.com",
    "Tristan.palis@stellar-ix.com",
    "patricia.andrianasy@stellar-ix.com",
    "paul.schonborn@stellar-ix.com",
    "anthony.christian@javaimport.mg",
    "lisiniaina.razafindrakoto@sgs.com",
    "riaz.hassim@althea.mg",
    "jrajaona@ingenosya.mg",
    "ramanga.g@live.fr",
    "iharir@gmail.com",
    "lraharijaona@fapbm.org",
    "nirinarajaonary@gmail.com",
    "zina.raveloson@madagascarairlines.com",
    "karim.barday@basan.mg",
    "ratovoson@gmail.com",
    "andriamamonjiarison@hermes-conseils.mg",
    "dirsynergy@gmail.com",
    "alaingpb2@gmail.com",
    "sertexdir@moov.mg",
    "hrakotoson@solidis.org",
    "trajaona@fthmconsulting.com",
    "fiandry.ndimbiarivola@castel-afrique.com",
    "andriamihaja.guenole@gmail.com",
    "ramboa@orchid.mg",
    "orchid.mamy@gmail.com",
    "gladtouchpro@gmail.com",
    "preludstudio.project@gmail.com",
    "ratisbonnealiceantoinette@gmail.com",
    "ratovomananaa22@gmail.com",
    "mahefa@rmaw.org",
    "admin@tropicomagency.com",
    "andrianina.fenosoa@std-inc.mg",
    "nancie.razafindraibe@std-inc.mg",
    "okaloukilalao@gmail.com",
    "okalouservices@gmail.com",
    "karene@heri.mg",
    "lmonloup@gmail.com",
    "lovatiana.ramandraiarisoa@basan.mg",
    "mahefa.ramandimbiarison@basan.mg",
    "onitiana.andrianina@gmail.com",
    "zina@andao-company.com",
    "herytiana.raleo@gmail.com",
    "rijarazakamahefa@gmail.com",
    "ramiadamananarinahzoandrianina@gmail.com",
    "carla.b@go-anka.com",
    "hasina.randriamora@etik.com",
    "miato.haven@gmail.com",
    "akshay.bikalala@uniplast.mg",
    "liliaratefi@ivana.mg",
    "rotsyrabarison@gmail.com",
    "toavina.net@gmail.com",
    "andry.ranarijaona@nexatranslations.com",
    "rakotom.tiana@gmail.com",
    "teo.lucidor@ent-pardalis.com",
    "dina.torapaint@gmail.com",
    "hantaranaivo.florearoma@gmail.com",
    "arajeriarison@gmail.com",
    "raoeliarisonrota@gmail.com",
    "liantsoarajaofetra@gmail.com",
    "henintsoarachelle@gmail.com",
    "a.randrianirina@technarea.com",
    "rfitia@gmail.com",
    "rasolofomorgan@gmail.com",
    "mbolanirinaantsa@gmail.com",
    "jamina@sango.agency",
    "ronak@tanatech-group.com",
    "tiffany.betonprefa@gmail.com",
    "valerie.andrianavalona@gmail.com",
    "maminirinaalanmanjaka@gmail.com",
    "ando.a@stepupdigital.net",
    "herilaza@sakafo-madagascar.com",
    "recrutement@upcostudio.com",
    "info@upcostudio.com",
    "prisca.andrianirina@edustep.mg",
]

INTERVAL_SECONDS = 20
MAX_RETRIES = 5          # tentatives par contact en cas d'erreur réseau/DNS
RETRY_DELAY_SECONDS = 30  # délai initial, doublé à chaque nouvelle tentative

# Journal des envois réussis : permet de reprendre sans renvoyer aux mêmes contacts
SENT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erratum_sent.log")


def _load_sent() -> set:
    if not os.path.exists(SENT_LOG):
        return set()
    with open(SENT_LOG, "r", encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}


def _mark_sent(email: str) -> None:
    with open(SENT_LOG, "a", encoding="utf-8") as f:
        f.write(email.lower() + "\n")


def _is_network_error(exc: Exception) -> bool:
    """Erreurs transitoires (DNS, connexion, coupure SMTP) qui méritent un nouvel essai."""
    return isinstance(exc, (OSError, smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError))


def _send_with_retry(email: str, label: str) -> None:
    delay = RETRY_DELAY_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            send_rjp_erratum(email=email)
            return
        except Exception as e:
            if not _is_network_error(e) or attempt == MAX_RETRIES:
                raise
            logging.warning(
                f"{label} ⚠️ Erreur réseau ({e}) — tentative {attempt}/{MAX_RETRIES}, "
                f"nouvel essai dans {delay}s (vérifier la connexion Internet / DNS)"
            )
            time.sleep(delay)
            delay = min(delay * 2, 300)


def main():
    already_sent = _load_sent()
    pending = [c for c in CONTACTS if c.lower() not in already_sent]
    total = len(pending)
    if already_sent:
        logging.info(f"{len(CONTACTS) - total} contact(s) déjà traités (voir {SENT_LOG}) — ignorés")
    logging.info(f"Début de l'envoi de l'erratum à {total} contacts (intervalle : {INTERVAL_SECONDS}s)")

    success = 0
    failed_emails = []

    try:
        for i, email in enumerate(pending, 1):
            label = f"[{i}/{total}]"
            logging.info(f"{label} Envoi à {email} ...")
            try:
                _send_with_retry(email, label)
                success += 1
                _mark_sent(email)
                logging.info(f"{label} ✅ Envoyé à {email}")
            except Exception as e:
                failed_emails.append(email)
                logging.error(f"{label} ❌ Échec pour {email} : {e}")

            # Attendre entre chaque envoi (sauf pour le dernier)
            if i < total:
                logging.info(f"⏳ Attente de {INTERVAL_SECONDS} secondes avant le prochain envoi...")
                time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.warning("Interrompu par l'utilisateur — relancer le script pour reprendre là où il s'est arrêté.")

    logging.info("=" * 60)
    logging.info(f"TERMINÉ : {success} envoyés, {len(failed_emails)} échec(s) sur {total} contacts")
    if failed_emails:
        logging.info("Échecs (seront retentés au prochain lancement) : " + ", ".join(failed_emails))
    logging.info("=" * 60)


if __name__ == "__main__":
    main()
