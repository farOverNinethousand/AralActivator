# AralActivator
Script zum automatischen Aktivieren von gekauften Aral Karten (Aral "SuperCard").

## Problemstellung
Aral Karten können ohne Aktivierung nicht verwendet werden.
Das händische Aktivieren vieler Aral Karten kostet Zeit - diese wollen wir uns sparen.
Aral Karten kauft man idR.nur, wenn es Rabatte und/oder Cashback - Beispiele:
- https://www.mydealz.de/deals/aral-supercard-fur-50-kaufen-5-geschenkt-1465573
- https://www.mydealz.de/deals/aral-supercard-einkaufen-und-tanken-fur-30-kaufen-5-supercard-einkaufen-und-tanken-geschenkt-jeweils-36-monate-gultig-1477242
- https://www.mydealz.de/deals/42eur-aral-supercard-fur-40eur-einlosbar-ab-1801-groupon-1719400

## Was das Script tut
- Aral E-Mails mit Bestellnummern + Aktivierungscode abgreifen
- Bestellungen aus dem Aral Account automatisch aktivieren:

https://www.aral-supercard.de/services/bestellungen/

## Installation (Windows)
1. [Installiere Python](https://gist.github.com/farOverNinethousand/2efc03be38c9932a338f1336fbef7977#python-installieren-windows)
2. Installiere folgende Python Module nach [DIESER Anleitung](https://gist.github.com/farOverNinethousand/2efc03be38c9932a338f1336fbef7977#python-module-installieren-windows):  
` mechanize `  
und  
`validators`  
3. Starte die AralActivator.py per Doppelklick.

## Vorbereitung
Du solltest wissen, wie viele Karten noch aktiviert werden müssen um das Ergebnis gegenprüfen zu können.
Du musst deine aral-supercard.de Zugangsdaten UND deine E-Mail Zugangsdaten samt IMAP-URL wissen.
**Achtung!** Deine Zugangsdaten werden unverschlüsselt im Ordner des Scripts gespeichert!

## Anleitung [Vollautomatische Version - empfohlen]
1. Starte das Script(AralActivator.py). Es wird dich beim ersten Start nach deinen Aral-Supercard.de Zugangsdaten UND E-Mail IMAP Zugangsdaten fragen.
**GMail Benutzer aufgepasst: Ihr müsst den [Zugriff durch weniger sichere Apps erlauben](https://myaccount.google.com/lesssecureapps).**

2. Das Script wird nun alle Karten aus deiner Aral Bestellübersicht aktivieren zu denen es in deinen Mails die passenden Aktivierungscodes findet.
Am Ende wird ggf. eine Übersicht der fehlgeschlagenen Aktivierungen angezeigt.

##### Anleitung 1 [Halbautomatische Version - veraltet nicht empfohlen!]
Um diesen Modus verwenden zu können, musst den in der settings.json Datei den Wert "requires_aral_account" auf "false" setzen.
1. Lege alle zu aktivierenden Aral Karten samt Lieferschein auf eine Oberfläche in der Nähe deines Computers.
2. Sammle die Inhalte aller Aral Aktivierungs-Mails und kopiere sie in eine Textdatei mit dem Namen 'mails.txt'.
Kopiere diese in den Ordner, in dem auch das Script liegt.
Tipp: Im GMail Webmailer findest du die Mails z.B. so:  
`subject:("aktivierung ihrer aral supercard")`
3. Starte das Script(AralActivator.py). Es sollte alle Bestellnummern samt Aktivierungscodes automatisch erfassen und dich nach den restlichen Informationen fragen.
4. Solltest du keine Lust mehr auf weitere Aktivierungsvorgänge hast, beende das Programm übers Menü und nicht über das "X", sodass der status gespeichert werden kann.

Du kannst bei jedem Start neue Mails in die mails.txt legen - es macht nichts, wenn bereits hinzugefügte Mails in der Datei verbleiben.

## Anleitung 2 [AralOrderer - erworbene Aral Gutscheincodes automatisch bestellen]
1. Starte das Script `AralOrderer.py`.
2. Gib die z.B. bei Groupon erworbenen Gutscheincodes ein. Du kannst auch den kompletten Inhalt der PDF, die die gutscheincodes enthält einfügen.
2. Das Script wird dich ggf. nach deinen aral-supercard.de Zugangsdaten fragen.
3. Gib die URL zum Aktionsartikel an.
4. Nun sollten alle Gutscheincodes automatisch eingeloest/bestellt werden.
Du kannst das prüfen, indem du danach in [deiner Bestellübersicht](https://www.aral-supercard.de/services/bestellungen/) schaust.
   
## Anleitung 3 [AralCardChecker - Seriennummern von Karten mit Datenbestand des AralOrderers abgleichen]
Hast du viele Karten gekauft und suchst eine Möglichkeit, möglichst schnell und ohne viel zu tippen den Satensatz einzelner Karten zu finden z.B. um voraktivierte Karten von selbst aktivierten Karten zu unterscheiden?
1. Starte das Script `AralCardChecker.py`.
2. Gib den Wert ein, der genommen werden soll, falls eine Seriennummer nicht zugeordnet werden kann.
3. Gib Seriennummern von Karten ein.
Vor-aktivierte Karten werden nicht gefunden somit kannst du diese identifizieren.
   Alle Ergebnisse werden in den Dateien `found_cards.json` und `found_cards.csv` gespeichert.
4. Falls du die Eingabe beendest und später erneut startest, wird mit dem vorherigen Stand fortgefahren, sofern die letzte `found_cards.json` noch existiert.

## Fehler und deren Bedeutung
1. `"Email crawler failed: Length mismatch"`:
Vermutlich hat Aral die Textbausteine der Aktivierungs-Mails geändert. Bitte lass' mir eine (zensierte) Fassung deiner Mails zukommen, damit ich das aktualisieren kann.
2. `"Fehler: Konnte Informationen aus E-Mails nicht extrahieren"`:  
   Eventuell hat sich der Inhalt der Aral E-Mails geändert und das Script benoetigt ein Update

## Bekannte Bugs
* Das Script kann keine Pagination: Bei manchen Mail-Anbietern (z.B. Yandex) werden max. 50 E-Mails mit Aktivierungscodes gefunden, auch wenn mehr vorhanden sind. Workaround: E-Mails zu einem anderen Anbieter schicken z.B. GMail

#### Wie kann ich die Aktivierung bestimmter Bestellnummern vermeiden?
Falls du manche Bestellungen aus irgewndwelchen Gründen noch nicht aktivieren möchtest (z.B. Aktivierungscode kam bereits an, Karte aber noch nicht) gibt es zwei Möglichkeiten:
1. Einfachste Möglichkeit: Lösche die E-Mail mit dem Aktivierungscode dieser Bestellnummer endgültig (inhalt davor sichern).
2. Kompliziertere Möglichkeit: Ändere im Script die Zeile `use_old_mail_crawler = False` auf `use_old_mail_crawler = True`.
Das deaktiviert das automatische Crawlen von E-Mails.
Weitere Infos dazu siehe Punkt "Halbautomatische Version".

## Dateien und deren Inhalt
cookies.txt
Gespeicherte Cookies deines Aral Accounts.

vouchers.json:  
Enthält alle vom Script gesammelten Infos zu deinen Karten.
Du solltest diese Datei nicht löschen - nur dann kann der Activator auch in Zukunft zuverlässig funktionieren (z.B. bereits hinzugefügte Bestellungen/Karten überspringen).
Enthält ausschließlich Bestellungen, zu denen Aktivierungscodes in den E-Mails gefunden wurden.

orders.json:  
Enthält die aus dem Aral Account gesammelten Infos zu deinen Bestellungen.
Wird benötigt, damit der Crawler beim nächsten Start weiß, welche Bestellnummern er bereits erfasst hat und somit schneller ist.

settings.json:  
Enthält alle Zugangsdaten und sonstige Einstellungsmöglichkeiten.
requires_account --> Falls deaktiviert lassen sich Codes auch manuell und ohne aral-supercard.de Account aktivieren (nicht empfohlen).

## TODOs (Geordnet nach Prioritäten)
- Bugfixing beim nächsten Aral Deal bei dem die Karten manuell aktiviert werden müssen
- Möglichkeit, ein Aktivierungsdatum einzutragen --> Aral würde die Karten nach dem Activator Durchlauf dann automatisch zu diesem Datum aktivieren [Anfrage eines MyDealz Users]
- Mithilfe von OCR alle fehlenden Infos von Karten auslesen
- Karten (optional) automatisch registrieren und Wunsch-PIN setzen


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
- SuperCards sind ab Aktivierungsdatum 36 Monate lang gültig
- Manche der gratis Karten werden erst zu einem bestimmten Datum automatisch von Aral aktiviert
- SuperCards sind idR. erst ab dem nächsten Tag nach Aktivierung gültig
- [03.01.2020] Man kann an der Tankstellen-Kasse beliebig viele Karten verwenden; es gab mal eine angebliche Maximalsumme von 100€, die aber nicht mehr zu existieren scheint siehe: https://www.mydealz.de/comments/permalink/24512889

# Das große Aral FAQ - alles rund um Kauf- und Aktivierung von SuperCards, Cashback usw.
## Aral FAQ
####  Weiter unten findet ihr noch ein Cashback FAQ
**Wie kommen die SuperCards an?**  
Per Brief - jede Bestellung in einem Brief also idR. 2 Karten pro Brief.

**Muss ich die Karten überhaupt aktivieren, wenn sie ankommen?**  
Das variiert von Aktion zu Aktion.  
Bei [dieser](https://www.mydealz.de/deals/aral-supercard-einkaufen-und-tanken-fur-30-kaufen-5-supercard-einkaufen-und-tanken-geschenkt-jeweils-36-monate-gultig-1477242) im November 2019 musste man sie aktivieren und bei [dieser](https://www.mydealz.de/deals/42eur-aral-supercard-fur-40eur-einlosbar-ab-1801-groupon-1719400) im Dezember 2020 nicht.

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

**Wie viele SuperCards kann man pro Einkauf in einer Aral Tankstelle einlösen? Gibt es ein Limit?**  
Maximal 10. Manche Filialen erlauben das Einlösen von mehr Karten, aber um Probleme zu vermeiden sollte man maximal 10 pro Einkauf verwenden.  
**Achtung:** Solltest du genau 10 SuperCards verwenden und deren Guthaben nicht ausreichen um die Rechnung vollständig zu bezahlen kann es passieren, dass du diesen nur in Bar zahlen kannst (hört sich komisch an, ist aber meine eigene Erfahrung)! Achtest du nicht drauf, können z.B. [Situationen wie diese](https://www.mydealz.de/comments/permalink/24913895) auftreten ;)  
Auch MyDealz User können dies bestätigen: https://www.mydealz.de/comments/permalink/24384188

**Gibt es einen Maximalbetrag, den man an AralTankstellen mit SuperCards bezahlen kann?**  
Nein. Auf MyDealz finden sich Gerüchte bzlg. einer Grenze von 100€ aber dies bezieht sich auf den Maximalbetrag an Tankkarten, die ein Kunde erwerben darf.
Das hat somit nichts mit dem Bezahlvorgang mit SuperCards zu tun! 

**Wie kann ich herausfinden, wie viel Guthaben/Restguthaben auf meinen SuperCards ist?**  
Wenn du gerade eingekauft hast steht das Restguthaben aller verwendeten Karten auf dem Kassenbon.
Wenn du das Guthaben separat abfragen willst geht das hier:  
https://www.aral-supercard.de/services/kartenguthaben-abrufen/  
Falls du deine SuperCards registriert hast, kannst du das Guthaben und das Gültigkeitsdatum jederzeit ohne die Eingabe der Sicherheitscodes hier einsehen:  
https://www.aral-supercard.de/services/kartenverwaltung/

**Was bringt mir die Registrierung von AralSupercards?**  
Du bekommst Ersatz bei Verlust und kannst das verbleibende Guthaben einfacher einsehen.

**Auf meiner neu erhaltenen Karte sind angeblich 0€ drauf was soll ich tun?**  
Karten, die bereits vor-aktiviert werden sollten werden von Aral manchmal etwas verspätet aktiviert.
Prüfe das Guthaben in 1-2 Tagen erneut und wende dich erst an den Aral Support, falls das Guthaben dann noch immer nicht vorhanden ist.

**Werden die 4/5/6€ gratis SuperCards irgendwo im Bestellverlauf oder Warenkorb angezeigt?**  
Nein. Im Bestellverlauf sollte ein Hinweis angezeigt werden, aber kein extra "5€ SuperCard gratis" Artikel.
Anhand der E-Mails oder auch des Namens der Aktion auf der Detailseite einer Bestellung kann man herausfinden, ob/welche Gratis-SuperCards dazu gehören: aral-supercard.de/services/bestellungen/detailansicht/**Bestellnummer**

**Wie lange sind die SuperCards gültig?**  
Laut offiziellem Aral FAQ (unten verlinkt) ab Aktivierung 36 Monate.  
Es scheint jedoch zu gelten: 3 Jahre ab Ende des Aktivierungsjahres.  
Beispiel: Aktivierung am: 17.01.2022  
Gültig bis: 31.12.2025  
(Danke an MyDealz User [hotspot22](https://www.mydealz.de/profile/hotspot22) - [Quelle](https://www.mydealz.de/comments/permalink/34560992))

**Wie lange habe ich Zeit, die Karten zu aktivieren?**  
Bis Dezember 2049. [[Quelle](https://www.mydealz.de/comments/permalink/24098442)]

**Kann ich Karten automatsich zu einem bestimmten Datum in der Zukunft aktivieren lassen?**  
Ja über die Aktivierung in der Bestellübersicht kannst du z.B. heute schon festlegen, dass deine Karten in 2 Jahren erst aktiviert werden sollen.  
Das geht nicht mit Karten, die nach der Bestellung automatisch zu einem bestimmten Datum aktiviert werden.

**Meine Frage taucht hier nicht auf wo finde ich eine Antwort?**  
Schau ins [offizielle Aral FAQ](https://www.aral-supercard.de/uebersicht/fragen-und-antworten/)

**Wie lautet die Support E-Mail Adresse von Aral?**  
`service@aral-supercard.de`

# MeinAral (App) FAQ

**Wichtig: Stand 01.01.2022 sind die MeinAral Accounts der mein.aral.de Webseite und die, die in der [MeinAral App](https://mein.aral.de/service-tools/meinaral-app/) erstellt wurden unterschiedliche Accounts/Zugangsdaten!**  
Dieses FAQ bezieht sich lediglich auf die MeinAral App und die darin enthaltenen Coupons!!  
Coupons der mein.aral.de Webseite sind idR. mit Payback und Payback Mehrfachcoupons kombinierbar ([Beispiel](https://www.mydealz.de/deals/1-liter-kraftstoff-gratis-ab-30-liter-im-aral-adventskalender-1919227)).

**Sind MeinAral Coupons mit Payback kombinierbar?**  
Ja, aber nur wenn du dein Payback Konto zuvor mit dem MeinAral App Konto verknüpfst.

**Muss ich meine Payback Karte an der Kasse zeigen, wenn ich meine MeinAral Kundenkarte zeige und Payback bereits damit verknüpft habe?**  
Nein - lediglich die MeinAral Karte und ggf. Payback Mehrfachcoupons.

**Auf meinem Kassenbon wird Payback nicht aufgeführt, obwohl ich meine MeinAral Kundenkarte vorgezeigt habe, woran liegt das?**  
Stand 07.01.2022 fehlen diese Informationen auf dem Kassenbon mangels Implementation seitens Aral.  
Auch die Kassierer Fragen manchmal noch nach der Payback Karte, wenn man nur die MeinAral Karte und einen Mehrfachcoupon zeigt jedoch werden die Punkte am Ende ohne zusätzliches Zeigen der Payback Karte gutgeschrieben.  
Du solltest deine Payback Punkte kurz nach dem Tankvorgang in der App sehen.  
Das wird hoffentlich bald von Aral nachgebessert.

**Ich habe mehrere Coupons in der MeinAral App - welcher wird verwendet und kann ich das beeinflussen?**  
Bisher wurde immer der 'bessere' verwendet (oder der, der zuerst abläuft?).  
Gab es z.B. gleichzeitig einen '2 Cent pro Liter Rabatt' ([Beispiel](https://www.mydealz.de/deals/aral-app-3-cent-ab-26-liter-sparen-1905779)) Coupon und einen '1L gratis ab 20L' ([Beispiel](https://www.mydealz.de/deals/aral-1l-gratis-bei-20l-1925481?page=3#thread-comments)), wurde der letztere verwendet.  
Da man die Coupons in der MeinAral App nicht aktivieren kann/muss, kann man keinen Einfluss darauf nehmen.

**Kann ich dasselbe Payback Konto mit mehreren verschiedenen MeinAral Konten verknüpfen?**  
Diese frage ist noch nicht geklärt.

## Cashback Aral / Groupon FAQ

# Cashback FAQ

**Wo gibt es Cashback beim kauf von Aral Gutscheinen per Groupon?**  
PayBack, Shopbuddies, ~~Aklamio~~, iGraal, Shoop, uvm.  
Es gibt unterschiedliche Erfahrungen was die Zuverlässigkeit dieser Anbieter angeht.
Aklamio hat am 20.01.2020 die Bedingungen aktualisiert und bietet kein Cashback mehr für Groupon Aral Käufe.  
Generell gab es seit anfang 2020 nur noch sehr selten Cashback auf Aral Deals.  
[Quelle1](https://www.aklamio.com/de/shops/groupon_de) | [Quelle2](https://www.mydealz.de/comments/permalink/24747098)

**Mein Cashback / Payback Punkte wurde nicht oder nicht korrekt erfasst was kann ich tun?**  
Warte 6-7 Werktage ab und kontaktiere dann den Support des jeweiligen Cashback Anbieters.

**Wo kann ich bei Paynack eine Nachbuchungsanfrage stellen?**
Du kannst PayBack über [das Kontaktformular](https://www.payback.de/pb/kontakt_call_center/)  und den [WhatsApp Support](https://www.payback.de/info/whatsapp1) erreichen.  
PayBack E-Mails, die man als Antwort auf eine Anfrage über's Kontaktformular bekommt kann man nicht einfach per E-Mail beantworten - Antworten geht nur, indem man das Kontaktformular mitsamt aller Informationen erneut ausfüllt!

**Wo finde ich immer aktuelle Aral Payback X-fach Coupons?**  
Siehe unten bei den Links.

# Groupon FAQ

**Wo finde ich meine Groupon Kundennummer/User-ID [oft für Cashback Nachbuchungsanfragen benötigt]?**  
Navigiere auf Groupon oben rechts zu "Meine Bestellungen" und klicke rechts bei einem beliebigen Gutschein auf "Details anzeigen".
Eine PDF öffnet sich und in der Adresszeile deines Browsers findest du deine Kundennummer:  
groupon.de/users/**<DEINE_KUNDENNUMMER>**/groupons/vouchers/<VOUCHER_ID>  
Die Kundennummer besteht aus 32 Stellen und enthält Bindestriche z.B.:
dddd1234-9ab8-12e9-b89a-0cad4d1234c0  
Falls du deine Groupon Kundennummer in das PayBack Kontaktformular eingeben willst: Sie ist zu lang für das vorgesehene Feld. Trage sie unten als Kommentar ein!

**Wie ist die bei Groupon angegebene Gültigkeit zu verstehen bzw. was bedeutet z.B. `Das Guthaben auf der Aral SuperCard muss bis 31.12.2025 abgegolten werden.` und wie lange sind über Groupon gekaufte Karten wirklich gültig?**  
* Die **Gültigkeit**, die Groupon angibt liegt oft 1-2 Monate in der Zukunft und kann ignoriert werden.
* Die Karten werden oft am Anfang/Ende eines Monats automatisch aktiviert: z.B. Gültigkeit 31.12.2022, Versand am 14.01.2022, **Aktivierung** am 17.01.2022 --> Echte Gültigkeit bis: 31.12.2025 (steht unter den Konditionen bei `...abgegolten werden`)

## Links
Karten hier 'manuell' bzw. ohne sich einzuloggen aktivieren:  
https://www.aral-supercard.de/services/karte-aktivieren/

Mehrere Karten/Bestellungen hier (einfacher) aktivieren, wenn man eingeloggt ist:  
https://www.aral-supercard.de/services/bestellungen/

Hier Guthaben abfragen (Captcha notwendig!):  
https://www.aral-supercard.de/services/kartenguthaben-abrufen/

Warum man bei Aral tanken sollte bzw. wie man dort günstiger tanken kann - von MyDealz User [Remy_Scherer](https://www.mydealz.de/profile/Remy_Scherer):  
https://docs.google.com/document/d/1qPv0Z4vss3M9wdyS4efymtHG_wVNo0bCACLaEnb6Iv0

MeinAral Webseite/App:  
https://mein.aral.de/service-tools/meinaral-app/

Aktuelle PayBack (Aral) Coupons:
* https://www.mydealz.de/search?q=aral+payback
* Alte Google Tabelle (ist nun eine geschlossene FB Gruppe): https://docs.google.com/spreadsheets/d/e/2PACX-1vTJuNdXygioH8a3ti_8kWlFsBcVyEOsF3NE2ze2f5tuIfx6RS94-kZWcC4-UoVU0x6nc0u01hlRrNIk/pubhtml?sfns=mo#

Aktuelle Aral Groupon Angebote:
* https://www.mydealz.de/search?q=aral+groupon