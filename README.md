# AralActivator
Script zum automatischen Aktivieren von gekauften Aral Karten (Aral "SuperCard").

## Problemstellung
Aral Karten können ohne Aktivierung nicht verwendet werden.
Das händische Aktivieren vieler Aral Karten kostet Zeit - diese wollen wir uns sparen.
Aral Karten kauft man idR nur, wenn es Rabatte gibt wie z.B. hier (Nov. 2019):

https://www.mydealz.de/deals/aral-supercard-fur-50-kaufen-5-geschenkt-1465573

https://www.mydealz.de/deals/aral-supercard-einkaufen-und-tanken-fur-30-kaufen-5-supercard-einkaufen-und-tanken-geschenkt-jeweils-36-monate-gultig-1477242

## Was das Script tut
- Aral E-Mails mit Bestellnummern + Aktivierungscode abgreifen
- Bestellungen aus dem Aral Account automatisch aktivieren:

https://www.aral-supercard.de/services/bestellungen/

## Installation (Windows)
1. Installiere Python 3
2. Installiere folgende python Module:
mechanize und imaplib
3. Starte AralActivator.py per Doppelklick.

## Vorbereitung
Du solltest wissen, wie viele Karten noch aktiviert werden müssen um das Ergebnis gegenprüfen zu können.
Du musst deine aral-supercard.de Zugangsdaten UND deine E-Mail Zugangsdaten samt IMAP-URL wissen.
Achtung! Deine Zugangsdaten werden unverschlüsselt im Ordner des Scripts gespeichert!

## Anleitung [Vollautomatische Version - empfohlen]
1. Starte das Script(AralActivator.py). Es wird dich beim ersten Start nach deinen Aral-Supercard.de Zugangsdaten UND E-Mail IMAP Zugangsdaten fragen.
2. Das Script wird nun alle Karten aus deiner Aral Bestellübersicht aktivieren zu denen es in deinen Mails die passenden Aktivierungscodes findet.
Am Ende wird ggf. eine Übersicht der fehlgeschlagenen Aktivierungen angezeigt.

##### Anleitung [Halbautomatische Version - veraltet nicht empfohlen!]
Um diesen Modus verwenden zu können, musst den in der settings.json Datei den Wert "requires_aral_account" auf "false" setzen.
1. Lege alle zu aktivierenden Aral Karten samt Lieferschein auf eine Oberfläche in der Nähe deines Computers.
2. Sammle die Inhalte aller Aral Aktivierungs-Mails und kopiere sie in eine Textdatei mit dem Namen 'mails.txt'.
Kopiere diese in den Ordner, in dem auch das Script liegt.
Tipp: Im GMail Webmailer findest du die Mails z.B. so:
`subject:("aktivierung ihrer aral supercard")`
3. Starte das Script(AralActivator.py). Es sollte alle Bestellnummern samt Aktivierungscodes automatisch erfassen und dich nach den restlichen Informationen fragen.
4. Solltest du keine Lust mehr auf weitere Aktivierungsvorgänge hast, beende das Programm übers Menü und nicht über das "X", sodass der status gespeichert werden kann.

Du kannst bei jedem Start neue mails in die mails.txt legen - es macht nichts, wenn bereits hinzugefügte Mails in der Datei verbleiben.

Tipps für die halbautomatische Version:
Füge maximal 10 zu aktivierende Karten/EMails gleichzeitig ein es sei denn du bist sehr gut organisiert, hast gute Augen und eine große Fläche zum Ausbreiten von Karten samt Lieferscheinen.

## Fehler und deren Bedeutung
1. "Email crawler failed: Length mismatch":
Vermutlich hat Aral die Textbausteine der Aktivierungs-Mails geändert. Bitte lass' mir eine (zensierte) Fassung deiner Mails zukommen, damit ich das aktualisieren kann.
2. "Fehler: Konnte Informationen aus E-Mails nicht extrahieren" --> Eventuell hat sich der Inhalt der Aral E-Mails geändert und das Script benoetigt ein Update

## Wie kann ich die Aktivierung bestimmter Bestellnummern vermeiden?
Falls du manche Bestellungen aus irgewndwelchen Gründen noch nicht aktivieren möchtest (z.B. Aktivierungscode kam bereits an, Karte aber noch nicht) gibt es zwei Möglichkeiten:
1. Einfachste Möglichkeit: Lösche die E-Mail mit dem Aktivierungscode dieser Bestellnummer endgültig (inhalt davor sichern).
2. Kompliziertere Möglichkeit: Ändere im Script die Zeile 'use_old_mail_crawler = False' auf 'use_old_mail_crawler = True'.
Das deaktiviert das automatische Crawlen von E-Mails.
Weitere Infos dazu siehe Punkt "Halbautomatische Version".

## Dateien und deren Inhalt
cookies.txt
Gespeicherte Cookies deines Aral Accounts.

vouchers.json:
Enthält alle vom Script gesammelten Infos zu deinen Karten.
Du solltest diese Datei nicht löschen - nur dann kann der Activator auch in Zukunft zuverlässig funktionieren (z.B. bereits hinzugefügte Bestellungen/Karten überspringen).
Enthält ausschließlich Bestellungen, zu denen Aktivierungscodes in den E-Mails gefunden wurden.
TODO: Auch alte Bestellungen aus dem Aral Account hinzufügen, die bereits älter sind und händisch aktiviert wurden.

orders.json:
Enthält die aus dem Aral Account gesammelten Infos zu deinen Bestellungen.
Wird benötigt, damit der Crawler beim nächsten Start weiß, welche Bestellnummern er bereits erfasst hat und somit schneller ist.

settings.json:
Enthält alle Zugangsdaten und sonstige Einstellungsmöglichkeiten.
requires_account --> Falls deaktiviert lassen sich Codes auch manuell und ohne aral-supercard.de Account aktivieren (nicht empfohlen).

## Bekannte Fehler auf der Aral Webseite
Wenn man eine komplette Bestellung aus Versehen mehrfach aktiviert, enthält die Detailansicht (/services/bestellungen/detailansicht/<Bestellnummer>) mehrere Einträge, obwohl eigentlich nur eine Karte aktiviert wird.
Screenshot:
![alt text](https://raw.githubusercontent.com/farOverNinethousand/AralActivator/master/testing/Screenshots/2019_12_05_Bug_eine_Bestellung_mehrmals_aktivieren.png "Veranschaulichung Zugangsdaten in Script eintragen")

## TODOs (Geordnet nach Prioritäten)
- Mehr Fehlertoleranz
- Testen
- Schönere Ausgaben
- Kleinere Fehlerbehebungen


## Unnützes Wissen über Aral-Supercards

### Eigenschaften von Aral (Tank-)Karten
Die Karten kommen per Post.
Jeder Bestellung, die idealerweise nur eine zu aktivierende Karte enthält ist ein Lieferschein mit folgenden relevanten Informationen beigelegt:
- Bestellnummer (9-stellig[?])
- Aktivierungscode (6-10-stellig [Lt. Webseite, Stand 27.11.2019])

Zudem stehen auf jeder Aral Karte Folgende Infos:
- Aral SuperCard Nr. (19-stellig, meist sind mind. die ersten 8 Stellen gegeben)
- Registrierungscode (4-stellig)
- Seriennummer (10-stellig) [irrelevant]
Per E-Mail bekommt man dann einen Aktivierungscode, der für die gesamte Bestellung(?) gilt - meistens muss man sowieso nur eine Karte aktivieren.

### Haltbarkeit und Einlösebedingungen
- SuperCards sind ab Aktivierungsdatum 3 Jahre lang' gültig
- Manche der gratis Karten werden erst zu einem bestimmten Datum automatisch von Aral aktiviert
- SuperCards sind idR. erst ab dem nächsten Tag nach Aktivierung gültig
- [20.12.2019] Man kann an der Tankstellen-Kasse beliebig viele Karten verwenden, allerdings ist der Maximalbetrag, den man in einem Vorgang damit bezahlen kann 100€

## Links
Karten hier 'manuell' bzw. ohne sich einzuloggen aktivieren:
https://www.aral-supercard.de/services/karte-aktivieren/
Mehrere Karten/Bestellungen hier (einfacher) aktivieren, wenn man eingeloggt ist:
https://www.aral-supercard.de/services/bestellungen/

Hier Guthaben abfragen (Captcha notwendig!):
https://www.aral-supercard.de/services/kartenguthaben-abrufen/