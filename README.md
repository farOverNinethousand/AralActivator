# AralActivator
Script zum automatischen Aktivieren von gekauften Aral Karten (Aral "SuperCard").

## Problemstellung
Aral Karten können ohne Aktivierung nicht verwendet werden.
Das händische Aktivieren vieler Aral Karten kostet Zeit - diese wollen wir uns sparen.
Aral Karten kauft man idR nur, wenn es Rabatte gibt wie z.B. hier (Nov. 2019):
https://www.mydealz.de/deals/aral-supercard-fur-50-kaufen-5-geschenkt-1465573
Man darf die Bestellscheine und die nicht aktivierten Karten nicht voneinander trennen ansonsten kann man nicht mehr zuordnen, welche Karte mit welchem Aktivierungscode aktiviert werden muss.

## Eigenschaften von Aral (Tank-)Karten
Die Karten kommen per Post.
Jeder Bestellung, die idealerweise nur eine zu aktivierende Karte enthält, ist eine Bestellnummer zugeordnet, die auf dem Lieferschein steht.
Zudem stehen auf jeder Aral Karte Folgende Infos:
- Aral SuperCard Nr.
- Seriennummer
- Registrierungscode (4-stellig, manchmal bzw. früher war das ein Rubbelfeld)
Per E-Mail bekommt man dann einen Aktivierungscode, der für die gesamte Bestellung(?) gilt - meistens muss man sowieso nur eine Karte aktivieren.

## Grundsätzliche Idee
Man macht Bilder auf denen jeweils ein- oder mehrere Karten und die dazugehörigen Lieferscheine sind (im Idealfall gehen mehrere Karten & Lieferscheine pro Bild).
Dann kopiert man alle Texte aller Mails mit den Aktivierungscodes in ein Textdokument.
Das Script filtert aus den Mails die Bestellnummern + Aktivierungscodes heraus.
Die Bilder werden per OCR Erkennung in Text umgewandelt.
Danach kann man über die Bestellnummer alle nötigen Informationen zum Aktivieren verknüpfen und alle Karten automatisiert aktivieren.
Diese Informationen könnte man noch abspeichern - so könnte man später das Guthaben (benötigt Eingabe von Captcha-Code) halb-automatisiert abfragen falls man sich bei einzelnen bereits verwendeten Karten nach dem Einkauf/Tanken nicht gemerkt hat, wie viel noch übrig ist.

## Wo ist das Script??
Das ist bisher nur eine Idee. Um diese umzusetzen brauche ich zum Einen noch Zeit und zum Anderen erhoffe ich mir von der frühen Erstellungs dieses GitHub Projektes Ideen / Tipps zur Umsetzung.
Aral Karten laufen nicht so schnell ab - wer also viele bestellt hat kann getrost mit der Aktivierung warten und mit etwas Glück bringt euch dieses Projekt was und falls nicht ist auch kein Weltuntergang ;)

## Links
OCR Software / Library:
https://pypi.org/project/pytesseract/
Karten hier aktivieren:
https://www.aral-supercard.de/services/karte-aktivieren/
Hier Guthaben abfragen (Captcha notwendig!):
https://www.aral-supercard.de/services/kartenguthaben-abrufen/