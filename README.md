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
2. Installiere folgende python Module per Kommandozeile (pip install <modulname>)
mechanize und validators
Siehe auch:
https://riptutorial.com/de/python/example/15322/installation-externer-module-mit-pip
3. Starte AralActivator.py per Doppelklick.

## Vorbereitung
Du solltest wissen, wie viele Karten noch aktiviert werden müssen um das Ergebnis gegenprüfen zu können.
Du musst deine aral-supercard.de Zugangsdaten UND deine E-Mail Zugangsdaten samt IMAP-URL wissen.
Achtung! Deine Zugangsdaten werden unverschlüsselt im Ordner des Scripts gespeichert!

## Anleitung [Vollautomatische Version - empfohlen]
1. Starte das Script(AralActivator.py). Es wird dich beim ersten Start nach deinen Aral-Supercard.de Zugangsdaten UND E-Mail IMAP Zugangsdaten fragen.

**GMail Benutzer aufgepasst: Ihr müsst den Zugriff durch weniger sichere Apps erlauben: https://myaccount.google.com/lesssecureapps**
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

## Anleitung [AralOrderer - erworbene Aral Gutscheincodes automatisch bestellen]
1. Starte das Script AralOrderer.py.
2. Gib die z.B. bei Groupon erworbenen Gutscheincodes ein. Du kannst auch den kompletten Inhalt der PDF, die die gutscheincodes enthält einfügen.
2. Das Script wird dich ggf. nach deinen aral-supercard.de Zugangsdaten fragen.
3. Gib die URL zum Aktionsartikel an.
4. Nun sollten alle Gutscheincodes automatisch eingeloest/bestellt werden.
Du kannst das prüfen, indem du danach in deiner Bestellübersicht schaust:
https://www.aral-supercard.de/services/bestellungen/

## Fehler und deren Bedeutung
1. "Email crawler failed: Length mismatch":
Vermutlich hat Aral die Textbausteine der Aktivierungs-Mails geändert. Bitte lass' mir eine (zensierte) Fassung deiner Mails zukommen, damit ich das aktualisieren kann.
2. "Fehler: Konnte Informationen aus E-Mails nicht extrahieren" --> Eventuell hat sich der Inhalt der Aral E-Mails geändert und das Script benoetigt ein Update

#### Wie kann ich die Aktivierung bestimmter Bestellnummern vermeiden?
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
- SuperCards sind ab Aktivierungsdatum 36 Monate lang' gültig
- Manche der gratis Karten werden erst zu einem bestimmten Datum automatisch von Aral aktiviert
- SuperCards sind idR. erst ab dem nächsten Tag nach Aktivierung gültig
- [03.01.2020] Man kann an der Tankstellen-Kasse beliebig viele Karten verwenden; es gab mal eine angebliche Maximalsumme von 100€, die aber nicht mehr zu existieren scheint: https://www.mydealz.de/comments/permalink/24512889

# Das große Aral FAQ - alles rund um Kauf- und Aktivierung von SuperCards, Cashback usw.
## Aral FAQ
####  Weiter unten findet ihr noch ein Cashback FAQ
**Wie kommen die SuperCards an?**

Per Brief - jede Bestellung in einem Brief also idR. 2 Karten pro Brief.

**Wie kann ich die höherwertigen 30/40€ Karten von den 4/6€ vor-aktivierten 'gratis' Karten unterscheiden? / Woran erkenne ich die bereits aktivierten Karten?**

Über die Seriennummer auf dem Lieferschein im Brief.
Die aufgelistete Seriennummer ist immer die 30/40€ Karte - die andere die 4/6€ Karte.
Falls du bei der JP Aktion mitgemacht hast:
Die 'schicke' JP Karte ist immer die höherwertige.
Man sollte trotzdem die Seriennummer abgleichen um sicherzugehen, dass man die Karte mit der auf dem Lieferschein aufgeführten Seriennummer erhalten hat!
Tipp: Markiere die Karten mit einem Permanentmarker

**Kommen die Aktivierungscodes per Post oder E-Mail?**

Per E-Mail.

**Was kommt sonst noch per Mail?**

Wenn du z.B. 10 einzelne Bestellungen bei Aral aufgegeben hast wirst du folgende E-Mails von Aral bekommen:
1. 10x Bestellbestätigung
2. 10x Rechnung
3. 10x Aktivierungscodes
--> Letztlich 10x Briefe mit den SuperCards (jeweils zwei Karten pro Brief [Stand: Aktion Dezember 2019])

**Wann kommen die Aktivierungscodes?**

Nachdem die SuperCards verschickt wurden. Es kann auch passieren, dass die Karten noch auf dem Weg sind und die Aktivierungscodes bereits da sind.
Es empfielt sich, SuperCards erst zu aktivieren wenn sie angekommen sind.

**Muss ich die 5/6€ Karten auch aktivieren?**

Nein diese sind bereits bei Ankunft aktiviert.

**Wie/Wo kann ich die SuperCards aktivieren?**

Es gibt mehrere Möglichkeiten:
1. Schnellste Möglichkeit: Über dieses Script (nach oben Scrollen, siehe Anleitung).
2. Über aral-supercard.de/services/bestellungen/ --> Bei jeder Bestellung auf "Detailansicht" klicken --> Zur Kartenaktivierung
Dann jeweils in den E-Mails nach der Bestellnummer suchen um den dazugehörigen Aktivierungscode zu finden.
3. Umständlichster Weg:
https://www.aral-supercard.de/services/karte-aktivieren/

**Achtung: Aktivierte Karten sind nie sofort einsetzbar! Immer erst am nächsten Tag / 24H später!**

Kann man mit den SuperCards alles\* (auch Zigaretten) kaufen?
Ja.

\* Außer Gutscheine/Geschenkkarten/Prepaid Aufladekarten/Paysafecards

**Kann man mit den SuperCards andere Gutscheine/Geschenkkarten/Prepaid Aufladekarten/Paysafecards kaufen?**

Nein, nicht mehr.

**Wie viele SuperCards kann man pro Einkauf in einer Aral Tankstelle einlösen?**

Maximal 10. Manche Filialen erlauben das Einlösen von mehr Karten, aber um Probleme zu vermeiden sollte man maximal 10 pro Einkauf verwenden.

Achtung: Solltest du genau 10 SuperCards verwenden und deren Guthaben nicht ausreichen um die Rechnung vollständig zu bezahlen kann es passieren, dass du diesen nur in Bar zahlen kannst (hört sich komisch an, ist aber meine eigene Erfahrung)!

Auch MyDealz User können dies bestätigen: https://www.mydealz.de/comments/permalink/24384188

**Gibt es einen Maximalbetrag, den man an AralTankstellen mit SuperCards bezahlen kann?**

Nein. Auf MyDealz finden sich Gerüchte bzlg. einer Grenze von 100€ aber dies bezieht sich auf den Maximalbetrag an Tankkarten, die ein Kunde erwerben darf.
Das hat somit nichts mit dem Bezahlvorgang mit SuperCards zu tun! 

**Wie kann ich herausfinden, wie viel Guthaben/Restguthaben auf meinen SuperCards ist?**

Wenn du gerade eingekauft hast steht das Restguthaben aller verwendeten Karten auf dem Kassenbon.
Wenn du das Guthaben separat abfragen willst geht das hier:

https://www.aral-supercard.de/services/kartenguthaben-abrufen/

Falls du deine SuperCards registriert hast kannst du das Guthaben ohne die Eingabe der Sicherheitscodes hier einsehen:

https://www.aral-supercard.de/services/kartenverwaltung/

(Eine Registrierung der SuperCards ist nicht notwendig und zeitaufwändig)

**Auf meiner neu erhaltenen Karte sind angeblich 0€ drauf was soll ich tun?**

Karten, die bereits vor-aktiviert werden sollten werden von Aral manchmal etwas verspätet aktiviert.
Prüfe das Guthaben in 1-2 Tagen erneut und wende dich erst an den Aral Support, falls das Guthaben dann noch immer nicht vorhanden ist.

**Werden die 5/6€ gratis SuperCards irgendwo im Bestellverlauf oder Warenkorb angezeigt?**

Nein. Im Bestellverlauf sollte ein Hinweis angezeigt werden, aber kein extra "5€ SuperCard gratis" Artikel.
Anhand der E-Mails oder auch des Namens der Aktion auf der Detailseite einer Bestellung kann man herausfinden, ob/welche Gratis-SuperCards dazu gehören: aral-supercard.de/services/bestellungen/detailansicht/<Bestellnummer>

**Wie lange sind die SuperCards gültig?**

Laut offiziellem Aral FAQ (unten verlinkt) ab Aktivierung 36 Monate.

**Wie lange habe ich Zeit, die Karten zu aktivieren?**

Bis Dezember 2049.

Quelle: https://www.mydealz.de/comments/permalink/24098442

**Kann ich Karten automatsich zu einem bestimmten Datum in der Zukunft aktivieren lassen?**

Ja über die Aktivierung in der Bestellübersicht kannst du z.B. heute schon festlegen, dass deine Karten in 2 Jahren erst aktiviert werden sollen.

**Meine Frage taucht hier nicht auf wo finde ich eine Antwort?**

Schau ins offizielle Aral FAQ:
https://www.aral-supercard.de/uebersicht/fragen-und-antworten/

**Wie lautet die Support E-Mail Adresse von Aral?**

service@aral-supercard.de


## Cashback Aral / Groupon FAQ

**Wo gibt es Cashback beim kauf von Aral Gutscheinen per Groupon?**

PayBack, Shopbuddies, Aklamio, iGraal, Shoop, uvm.
Es gibt unterschiedliche Erfahrungen was die Zuverlässigkeit dieser Anbieter angeht.

**Mein Cashback / PayBack Punkte wurde nicht oder nicht korrekt erfasst was kann ich tun?**

Warte 1-2 Tage ab und kontaktiere dann den Support des jeweiligen Cashback Anbieters.
PayBack kann hartnäckig sein und man muss das Kontaktformular ggf. mehrmals mit denselben Daten ausfüllen um die Punkte nachträglich zu bekommen.

**Wo kann ich bei PayBack eine Nachbuchungsanfrage stellen?**
https://www.payback.de/pb/kontakt_call_center/

Es gibt keine anderen Kontaktmöglichkeiten. Falls man eine Anfrage stellt und weitere Daten nachliefern muss muss man nochmal über diesen Weg gehen - auf E-Mails von PayBack kann man nicht einfach per E-Mail antworten!

**Wo finde ich meine Groupon Kundennummer/User-ID [oft für Cashback Nachbuchungsanfragen benötigt]?**

Navigiere auf Groupon oben rechts zu "Meine Bestellungen" und klicke rechts bei einem beliebigen Gutschein auf "Details anzeigen".
Eine PDF öffnet sich und in der Adresszeile deines Browsers findest du deine Kundennummer:

groupon.de/users/**<DEINE_KUNDENNUMMER>**/groupons/vouchers/<VOUCHER_ID>

Die Kundennummer besteht aus 32 Stellen und enthält Bindestriche z.B.:
dddd1234-9ab8-12e9-b89a-0cad4d1234c0

Falls du die Kundennummer im PayBack Kontaktformular eingeben willst: Sie ist zu lang für das vorgesehene Feld. Trage sie unten als Kommentar ein!

**Wo finde ich immer aktuelle Aral PayBack X-fach Coupons?**

Siehe unten bei den Links.

## Links
Karten hier 'manuell' bzw. ohne sich einzuloggen aktivieren:
https://www.aral-supercard.de/services/karte-aktivieren/

Mehrere Karten/Bestellungen hier (einfacher) aktivieren, wenn man eingeloggt ist:
https://www.aral-supercard.de/services/bestellungen/

Hier Guthaben abfragen (Captcha notwendig!):
https://www.aral-supercard.de/services/kartenguthaben-abrufen/

Warum man bei Aral tanken sollte bzw. wie man dort günstiger tanken kann [von mydealz.de/profile/Remy_Scherer]:
https://docs.google.com/document/d/1qPv0Z4vss3M9wdyS4efymtHG_wVNo0bCACLaEnb6Iv0

Aktuelle PayBack (Aral) Coupons [oben die Tabelle 'Aral' auswählen]:
https://docs.google.com/spreadsheets/d/e/2PACX-1vTJuNdXygioH8a3ti_8kWlFsBcVyEOsF3NE2ze2f5tuIfx6RS94-kZWcC4-UoVU0x6nc0u01hlRrNIk/pubhtml?sfns=mo#

Quelle: Ist in der Tabelle verlinkt