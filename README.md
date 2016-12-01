# RR-Sendeplan

Et provisorisk prosjekt for å kunne hente ut sendeplanen direkte fra Radio REST API.

## Hvorfor?

Det hender folk i SM lurer på hva sendeplanen er, blant annet for å lage RR-annonser
i Under Dusken. I stedet for at vi må skrive ned sendeplanen i et regneark, eller
radioledelsen bruker et regneark som ikke i det hele tatt stemmer med hva som
faktisk går, så kan de bruke denne nettapplikasjonen.

## Hvordan installere?

Som alle andre Python-ting, egentlig.

1. Klon dette repoet.
1. Lag et virtualenv som bruker python3, f. eks. `virtualenv -p python3 venv`.
3. Aktiver det: `. venv/bin/activate`
4. Installer avhengigheter: `pip install -r requirements.txt`
5. Åpne `settings.yaml.template` og fyll inn manglende innstillinger. Lagre som `settings.yaml`
   (i Vim gjør du dette ved å skrive `:w settings.yaml`)
6. Lag en ny bruker som skal kjøre denne applikasjonen.
7. Åpne `rr-sendeplan.conf.template` og fyll inn manglende variabler der. Lagre som `rr-sendeplan.conf`.
8. Åpne `start-rr-sendeplan.template` og fyll inn manglende variabler der. Lagre som `start-rr-sendeplan`.
9. Sørg for at fila `start-rr-sendeplan` er kjørbar for brukeren du lagde i steg 6.
10. Kopier `rr-sendeplan.conf` inn i `/etc/init.d` (krever sudo!)
11. Start rr-sendeplan ved å kjøre `sudo service rr-sendeplan start`.
12. Åpne `rr-sendeplan-apache.conf` og fyll inn manglende variabler der. Lagre som `rr-sendeplan-apache.conf`.
13. Kopier `rr-sendeplan-apache.conf` inn i `/etc/apache2/sites-available` eller integrer den i konfigurasjonen
    til internt.radiorevolt.no, avhengig av hvor du vil ha det hen.
14. Restart Apache: `sudo apache2ctl graceful`

