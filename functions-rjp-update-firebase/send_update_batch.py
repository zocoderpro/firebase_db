"""Script d'envoi en masse de l'email de mise à jour du programme RJP 2026.

Envoie l'email de mise à jour à tous les contacts avec 10 secondes d'intervalle.
Usage : ./venv/Scripts/python.exe send_update_batch.py
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

from update_senders import send_rjp_update

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ──────────────────────────────────────────────────────────────
# LISTE DES CONTACTS (157)
# ──────────────────────────────────────────────────────────────
CONTACTS = [
    "nyhasy.ramaroson@ccifm.mg",
    "guy.foka@konecta.com",
    "ramarosonmendie@gmail.com",
    "nanou.fiankinana@un.org",
    "tahiry.ramanantsoa@gmail.com",
    "cassandra.mansotte@sobatra.mg",
    "fanjara@yanaecosysteme.com",
    "tansug.ok@unctad.org",
    "mario.jales@un.org",
    "onja.ravo@gmail.com",
    "dzafindravaka@sfi.mg",
    "ioannis@taloumis.mg",
    "groupement.pme@gmail.com",
    "gfem.se@gmail.com",
    "directeurexecutif@gefp.mg",
    "syndusmad@sim.mg",
    "lalaina.rabemananjara@ccifm.mg",
    "t.randriamaromanana@miarakap.com",
    "ingridcjdmada@gmail.com",
    "holy.efoi@gmail.com",
    "gilrzf@yahoo.fr",
    "gem@iris.mg",
    "frederic.andriamaharo@basan.mg",
    "hary@oti.mg",
    "ac.tchokonte@mg.airtel.com",
    "julien.marchand1@concentrix.com",
    "gcam@moov.mg",
    "marc.renauld@galana.mg",
    "ejjr@galaxam.com",
    "president@goticom.org.mg",
    "georgesgeeraerts@outlook.com",
    "dama.jeanluc@gmail.com",
    "c.brunot@codal.mg",
    "johannpless@gmail.com",
    "pca@confederation-tourisme.mg",
    "jl.marquetoux@mineschamber.mg",
    "m.ranaivoson@ietp.com",
    "dg@arbiochem.mg",
    "hbonshe@baobab.com",
    "fionamorin@gmail.com",
    "revina@iom.int",
    "pbrechard@iom.int",
    "rabetsivoh.claudia.mba@gmail.com",
    "zara@viseo.mg",
    "benoit.sarraute@sipembanque.mg",
    "anna.ratsimbason@boa.mg",
    "anjaranirina.rakotoarivony@boa.mg",
    "ameziane.jamal@boa.mg",
    "ina.diallo@afgbank.mg",
    "r.ekogha@bgfi.com",
    "a.evouna@bgfi.com",
    "andry.ravalomanda@bred.mg",
    "frederic.sammut@bred.mg",
    "thierry.charras-gillot@bred.mg",
    "regis.barriac@bred.fr",
    "jmravelomanantsoa@solidis.org",
    "f.wybo@ultramaille.mg",
    "pierre.raoelina@fmfp.mg",
    "fenitra@google.com",
    "a.andrianarivelo@bfm.mg",
    "fortunat.andriani@gmail.com",
    "arabarijohn@ifc.org",
    "rakers@ifc.org",
    "smuco@worldbank.org",
    "aseck2@worldbank.org",
    "adrien.ladislas@pic.mg",
    "leguenn@afd.fr",
    "claudi.ferrer-savall@eeas.europa.eu",
    "roberto.schiliro@eeas.europa.eu",
    "roland.kobia@eeas.europa.eu",
    "tojo.ramamonjisoa@edbm.mg",
    "eva.radavidrason@edbm.mg",
    "ugo.razafindratandra@edbm.mg",
    "dg.edbm@edbm.mg",
    "entreprendremadagascar@yahoo.fr",
    "fanja.razakaboana@gmail.com",
    "lanto@labooi.mg",
    "trasamimanana@sipromad.com",
    "johanne.raharinosy@ccifm.mg",
    "heritinanantsoa@gmail.com",
    "ginesthelie@gmail.com",
    "president@gem.mg",
]

INTERVAL_SECONDS = 10
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
            send_rjp_update(email=email)
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
    logging.info(f"Début de l'envoi de l'email de mise à jour à {total} contacts (intervalle : {INTERVAL_SECONDS}s)")

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
