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
Jeder Bestellung, die idealerweise nur eine zu aktivierende Karte enthält ist ein Lieferschein mit folgenden relevanten Informationen beigelegt:
- Bestellnummer (9-stellig[?])
- Aktivierungscode (6-10-stellig [Lt. Webseite, Stand 27.11.2019])

Zudem stehen auf jeder Aral Karte Folgende Infos:
- Aral SuperCard Nr. (19-stellig, meist sind mind. die ersten 8 Stellen gegeben)
- Registrierungscode (4-stellig)
- Seriennummer (10-stellig) [irrelevant]
Per E-Mail bekommt man dann einen Aktivierungscode, der für die gesamte Bestellung(?) gilt - meistens muss man sowieso nur eine Karte aktivieren.

## Grundsätzliche Idee
Man macht Bilder auf denen jeweils ein- oder mehrere Karten und die dazugehörigen Lieferscheine sind (im Idealfall gehen mehrere Karten & Lieferscheine pro Bild).
Dann kopiert man alle Texte aller Mails mit den Aktivierungscodes in ein Textdokument.
Das Script filtert aus den Mails die Bestellnummern + Aktivierungscodes heraus.
Die Bilder werden per OCR Erkennung in Text umgewandelt.
Danach kann man über die Bestellnummer alle nötigen Informationen zum Aktivieren verknüpfen und alle Karten automatisiert aktivieren.
Diese Informationen könnte man noch abspeichern - so könnte man später das Guthaben (benötigt Eingabe von Captcha-Code) halb-automatisiert abfragen falls man sich bei einzelnen bereits verwendeten Karten nach dem Einkauf/Tanken nicht gemerkt hat, wie viel noch übrig ist.

## Anleitung [Halbautomatische Version]
1. Lege alle zu aktivierenden Aral Karten samt Lieferschein auf eine Oberfläche in der Nähe deines PCs.
2. Sammle die Inhalte aller Aral Aktivierungs-Mails und kopiere sie in eine Textdatei mit dem Namen 'mails.txt'.
Kopiere diese in den Ordner, in dem auch das Script liegt.
Tipp: Im GMail Webmailer findest du die Mails z.B. so:
`subject:("aktivierung ihrer aral supercard")`
3. Starte das Script. Es sollte alle Bestellnummern samt Aktivierungscodes automatisch erfassen und dich nach den restlichen Informationen fragen.
4. Solltest du keine Lust mehr auf weitere Aktivierungsvorgänge hast, beende das Programm übers Menü und nicht über das "X", sodass der status gespeichert werden kann.

Du kannst bei jedem Start neue mails in die mails.txt legen - es macht nichts, wenn bereits hinzugefügte Mails in der Datei verbleiben.

## Einstellungen (settings.json)
setting_max_voucher_failures_before_stop = Max. Anzahl unbekannter Fehler bei der Aktivierung hintereinander
setting_save_log = Log speichern?

## Fehler und deren Bedeutung
1. Email crawler failed: Length mismatch: Vermutlich hat Aral die Textbausteine der Aktivierungs-Mails geändert. Bitte lass' mir eine (zensierte) Fassung deiner Mails zukommen, damit ich das aktualisieren kann.

## Dateien und deren Inhalt
vouchers.json:
Enthält alle vom Script gesammelten Infos zu deinen Karten.
Du solltest diese Datei nicht löschen - nur dann kann der Activator auch in Zukunft zuverlässig funktionieren (z.B. bereits hinzugefügte Bestellungen/Karten überspringen).
settings.json:
Enthält die Einstellungen des Scripts

## TODOs (Geordnet nach Prioritäten)
- Mehr Fehlertoleranz
- OCR Erkennung der Infos auf Aral Karten
- Guthaben prüfen (unklar wie sinnvoll das ist, die Captchas sind sehr nervig!)

## Links
OCR Software / Library:
https://pypi.org/project/pytesseract/

Karten hier aktivieren:
https://www.aral-supercard.de/services/karte-aktivieren/

Hier Guthaben abfragen (Captcha notwendig!):
https://www.aral-supercard.de/services/kartenguthaben-abrufen/