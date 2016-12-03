# RR-Sendeplan

Et provisorisk prosjekt for å kunne hente ut sendeplanen direkte fra Radio REST API.

## Hvorfor?

Det hender folk i SM lurer på hva sendeplanen er, blant annet for å lage RR-annonser
i Under Dusken. I stedet for at vi må skrive ned sendeplanen i et regneark, eller
radioledelsen bruker et regneark som ikke i det hele tatt stemmer med hva som
faktisk går, så kan de bruke denne nettapplikasjonen.

## Funksjonalitet

* Se sendeplanen for noen uker fram og tilbake.
* Mobil-vennlig
* Oppdateres hvert 5. minutt
* Data hentes rett fra DigAIRange (BCS)
* Sendeplanen kan lastes ned som CVS (nyttig for sommerimport!)

Obs: dette prosjektet avhenger av et API som gir tilgang til BCS-systemet,
så det er ikke nyttig for noen utenfor Radio Revolt.

## Hvordan installere?

Som alle andre Python-ting, egentlig. Les deg opp på [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
hvis du ikke har brukt det før.

Oppsettet som beskrives her, bruker gunicorn som en web-server som kjører sendeplan.py-applikasjonen.
Apache2 antas å være i bruk, og brukes som en reverse proxy. Det vil si at brukerne som aksesserer
applikasjonen, gjør det gjennom Apache2, som internt bruker gunicorn-serveren. Apache2-serveren blir
også satt til å cache sidene for fem minutter, så ikke RR-Sendeplan kan brukes til å DoS-e serveren
som Radio-APIet kjører på.

Noen instruksjoner vil være forskjellige avhengig av om du bruker Upstart eller SystemD.
Generelt så er Ubuntu 14.04 Upstart, og Ubuntu 16.04 SystemD, slå opp på Google hvis du
er usikker.

1.  Sørg for at python3 og virtualenv er installert: `sudo apt-get install python3 virtualenv`
2.  Klon dette repoet: `git clone https://github.com/RadioRevolt/RR-Sendeplan.git`
3.  Gå inn i mappen: `cd RR-Sendeplan`
4.  Lag et virtualenv som bruker python3: `virtualenv -p python3 venv`
5.  Aktiver det: `. venv/bin/activate`
6.  Installer avhengigheter: `pip install -r requirements.txt`
7.  Åpne `settings.yaml.template` og fyll inn manglende innstillinger (`nano` er grei editor for de som ikke har lært `vim`). Lagre som `settings.yaml`
    (i Vim gjør du dette ved å skrive `:w settings.yaml`)
8.  Lag en ny bruker som skal kjøre denne applikasjonen: `sudo useradd rr-sendeplan`.
9.  Åpne `rr-sendeplan.conf.template` og fyll inn manglende variabler der (hvis 
    du bruker upstart; gjør det samme med `rr-sendeplan.service.template` hvis du bruker 
    SystemD). Lagre som `rr-sendeplan.conf` (`rr-sendeplan.service` hvis du bruker SystemD).
10. Åpne `start-sendeplan.template` og fyll inn manglende variabler der. Lagre som `start-sendeplan`.
11. Sørg for at fila `start-sendeplan` er kjørbar for brukeren du lagde i steg 8: `chmod g-w,g+x start-sendeplan; sudo chgrp rr-sendeplan start-sendeplan`
12. Kopier `rr-sendeplan.conf` inn i `/etc/init` (krever sudo!) hvis du bruker Upstart,
    kopier `rr-sendeplan.service` inn i `/etc/systemd/system` og kjør `sudo systemctl enable rr-sendeplan` hvis du bruker SystemD (kopiering gjøres med `cp`).
13. Start rr-sendeplan ved å kjøre `sudo service rr-sendeplan start` hvis du bruker Upstart, `sudo systemctl start rr-sendeplan` hvis du bruker SystemD.
14. Åpne `rr-sendeplan-apache.conf` og fyll inn manglende variabler der. Lagre som `rr-sendeplan-apache.conf`.
15. Kopier `rr-sendeplan-apache.conf` inn i `/etc/apache2/sites-available` (hvertfall på Debian-systemer) eller integrer den i konfigurasjonen
    til en annen VirtualHost hvis du ønsker det, avhengig av hvor du vil ha det hen. Aktiver den konfigurasjonen, hvis du lagde ny fil (a2ensite).
    Jeg vet dette er veldig vagt, det er best å få hjelp av noen som allerede kan litt Apache2-konfigurasjon, eller lese seg litt opp
    på det selv. Det er ikke så _veldig_ vanskelig.
16. Restart Apache: `sudo apache2ctl graceful` (dette vil kjøre en test på konfigurasjonen før Apache restarter, så feil i konfigurasjonen
    ikke fører til at serveren går ned. Det vil også sørge for at ingen får sin tilkobling avbrutt.)

