import re, sys, time, validators
from Helper import *


# Removes all products from the shopping cart
def dumpShoppingCart(br):
    response = br.open('https://www.aral-supercard.de/shop/warenkorb')
    html = getHTML(response)
    try:
        try:
            articleDeleteURLs = re.compile(
                r'\"(https?://www.aral-supercard\.de/shop/warenkorb/artikel-loeschen/[^<>\"]+)\"').findall(html)
        except:
            print('Warenkorb ist bereits leer')
            return
        print('Anzahl gefundener Artikel im Warenkorb: %d' % len(articleDeleteURLs))
        delete_article_index = 0
        numberof_article_delete_errors = 0
        for articleDeleteURL in articleDeleteURLs:
            delete_article_index += 1
            print('Loesche Artikel %d / %d' % (delete_article_index, len(articleDeleteURLs)))
            try:
                response = br.open(articleDeleteURL)
                html = getHTML(response)
            except:
                numberof_article_delete_errors += 1
        if numberof_article_delete_errors > 0:
            print(
                'Warnung: %d Elemente aus dem Warenkorb konnten eventuell nicht geloescht werden' % numberof_article_delete_errors)
        else:
            print('Warenkorb sollte leer sein')
    except:
        print('Fehler beim Leeren des Warenkorbs oder keine Artikel')
    # print(html)
    return


print('Welcome to AralActivator %s' % getVersion())
print('Gib deine Gutscheine ein und druecke 2x ENTER.')
print('Falls  du diese per Groupon [PDF] bekommen hast, markiere den kompletten Text der PDF und fuege ihn hier ein!')

voucherSource = None

total_numberof_vouchers = 0
voucher_input_loop_counter = 0
crawledVouchers = None

settings = loadSettings()
br = getNewBrowser()

while total_numberof_vouchers == 0:
    voucherSource = ''
    print(
        'Gib deine Gutscheincodes oder den kompletten Inhalt der Groupon PDF ein (druecke dann 2x ENTER dann geht\'s weiter):')
    # Improvised multi line input: https://stackoverflow.com/questions/30239092/how-to-get-multiline-input-from-user
    counter_lines_of_input = 0
    currInput = '_TEST_'
    while currInput != '' and counter_lines_of_input <= 5000:
        currInput = input()
        voucherSource += currInput + '\n'
        counter_lines_of_input += 1
        # End of user input handling
    # Use set to prevent duplicated entries
    crawledVouchers = set(re.compile(r'([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})').findall(voucherSource))
    total_numberof_vouchers = len(crawledVouchers)

print('Anzahl gefundener Gutscheine: ' + str(len(crawledVouchers)))
printSeparator()

index = 0
for voucher in crawledVouchers:
    index += 1
    print('Gutschein %d : %s' % (index, voucher))
printSeparator()

logged_in = loginAccount(br, settings)
if not logged_in:
    print('Login-Fehler')
    sys.out()

printSeparator()
user_input_article_url = None
url_article_30euro = 'https://www.aral-supercard.de/shop/produkt/aral-supercard-einkaufen-tanken-30-2123'
url_article_40eurojp = 'https://www.aral-supercard.de/shop/produkt/jp-performance-einkaufen-tanken-individueller-wert-sondermotiv-motor-show-2124'
while True:
    print(
        'Achtung! Alle Gutscheine werden auf deine bevorzugte Adresse bestellt! Pruefe deine Adresse bevor du die Einloesung startest!')
    print('Waehle, aus welcher Aktion deine Gutscheine kommen:')
    print('1 = 30+5Euro --> Aktionsurl: %s' % url_article_30euro)
    print('2 = 40+6Euro_JP --> Aktionsurl: %s' % url_article_40eurojp)
    print('3 = Andere Aktion / Link zum Aktionsartikel selbst eingeben')
    user_input = userInputDefinedLengthNumber(1)
    if user_input < 0 or user_input > 3:
        # Bad user input
        print('Ungueltige Eingabe')
        continue
    if user_input == 1:
        user_input_article_url = url_article_30euro
    elif user_input == 2:
        user_input_article_url = url_article_40eurojp
    else:
        print('Gib den Link zum Aktionsartikel ein:')
        user_input_article_url = input()
        if not validators.url(user_input_article_url):
            print('Ungueltige URL')
            continue
    # Done - step out of loop
    break

print('Verwende folgende URL zum Aktionsartikel: ' + user_input_article_url)

printSeparator()

index = 0
successful_vounter = 0
wait_seconds_between_requests = 2
wait_seconds_on_wait_error = 30
# TODO: Save vouchers / log in file so users will not lose information when they close the window
# TODO: Add html / mechanize loggers
numberof_steps = 7
try:
    for currentVoucher in crawledVouchers:
        index += 1
        try:
            # Dump shopping cart before each loop to ensure that we never try to buy multiple items
            print('Arbeite an Gutschein %d / %d : %s' % (index, len(crawledVouchers), currentVoucher))
            print('Schritt 0 / %d: Warenkorb leeren' % numberof_steps)
            dumpShoppingCart(br)
            # First step
            print('Schritt 1 / %d: Oeffne Artikelseite' % numberof_steps)
            time.sleep(wait_seconds_between_requests)
            response = br.open(user_input_article_url)
            html = getHTML(response)
            # Next step
            print('Schritt 2 / %d: Fuelle Warenkorb' % numberof_steps)
            form_index = getFormIndexBySubmitKey(br, 'value')
            if form_index == -1:
                print('Fehler: Konnte ArtikelForm nicht finden')
                # print(html)
                continue
            br.select_form(nr=form_index)
            time.sleep(wait_seconds_between_requests)
            response = br.submit()
            html = getHTML(response)
            # Next step
            print('Schritt 3 / %d: Oeffne Bestelluebersicht' % numberof_steps)
            time.sleep(wait_seconds_between_requests)
            try_counter = 0
            max_tries = 20
            wait_error = True
            while True:
                try_counter += 1
                response = br.open('https://www.aral-supercard.de/shop/abschluss')
                html = getHTML(response)
                # Next step - only display this once so output looks nicer!
                print('Schritt 4 / %d | Versuch %d / %d : Fuege Gutschein ein und pruefe Gueltigkeit' % (
                numberof_steps, try_counter, max_tries))
                form_index = getFormIndexBySubmitKey(br, 'voucher_1')
                if form_index == -1:
                    print('Konnte GutscheinForm nicht finden')
                    smoothExit()
                br.select_form(nr=form_index)
                voucherElements = currentVoucher.split('-')
                br['voucher_1'] = voucherElements[0]
                br['voucher_2'] = voucherElements[1]
                br['voucher_3'] = voucherElements[2]
                time.sleep(wait_seconds_between_requests)
                response = br.submit()
                html = getHTML(response)
                if 'Zu viele Versuche' in html:
                    # This may happen when user enters a lot of invalid vouchers. In my tests (2019-12-27) this would always happen on the 8th entered voucher. In my tests I never needed to wait more than 180 seconds. Wait time will be cleared serverside once waited once.
                    print('Fehler: \'Zu viele Versuche. Bitte versuchen Sie es in ein paar Minuten erneut.\'')
                    if try_counter >= max_tries:
                        # Give up
                        print('Zu viele Fehlversuche --> Stoppe')
                        break
                    print('Warte %d Sekunden bis Neuversuch ...' % wait_seconds_on_wait_error)
                    time.sleep(wait_seconds_on_wait_error)
                    continue
                wait_error = False
                break
            if wait_error:
                # Try next code but chances are high that it will fail too
                continue
            elif 'Der Gutscheincode ist unbekannt oder nicht mehr' in html:
                print('Gutschein ungueltig oder bereits eingeloest')
                continue
            # Important errorhandling! We do not want to order random stuff or random amounts of cards ;)
            try:
                cart_amountStr = re.compile(
                    r'<th>Summe<br/>\s*<small>inkl\. MwSt\.</small>\s*</th>\s*<th>([0-9]+,[0-9]+)').search(html).group(
                    1)
                cart_amountStr = cart_amountStr.replace(',', '.')
                cart_amount = float(cart_amountStr)
                # With our voucher we should always 'pay' 0€
                if cart_amount > 0:
                    print('Fehler: Summe ist groesser als 0€ --> %s --> Ueberspringe aktuellen Code' % cart_amountStr)
                    continue
            except:
                # print(html)
                print('Fehler: Konnte Summe nicht finden --> Ueberspringe aktuellen Code')
                continue
            # Next step - from now on, there is no failure reason anymore - process should always be the same!
            print('Schritt 5 / %d: Weiter von den Bestelldetails --> Rechnungsadresse' % numberof_steps)
            form_index = getFormIndexByActionContains(br, 'shop/abschluss')
            if form_index == -1:
                print('Konnte \'shop/abschluss\' Form nicht finden')
            br.select_form(nr=form_index)
            time.sleep(wait_seconds_between_requests)
            response = br.submit()
            html = getHTML(response)
            # Next step
            print('Schritt 6 / %d: Weiter von Rechnungsadresse --> Lieferadresse' % numberof_steps)
            form_index = getFormIndexByActionContains(br, 'shop/abschluss/adressen')
            if form_index == -1:
                print('Konnte \'shop/abschluss/adressen\' Form nicht finden')
            br.select_form(nr=form_index)
            time.sleep(wait_seconds_between_requests)
            response = br.submit()
            html = getHTML(response)
            # Last step
            print('Schritt 7 / %d: Weiter von Lieferadresse --> Bestaetigung' % numberof_steps)
            form_index = getFormIndexBySubmitKey(br, 'orderConfirmData')
            if form_index == -1:
                print('Konnte \'shop/abschluss/adressen\' Form nicht finden')
            br.select_form(nr=form_index)
            # br['orderConfirmData'] = '1'
            br.form['orderConfirmData'] = ['1']
            br.form['orderConfirmTerms'] = ['1']
            br.form['confirmPrivacyPolicy'] = ['1']
            # br['orderConfirmTerms'] = '1'
            # br['confirmPrivacyPolicy'] = '1'
            response = br.submit()
            html = getHTML(response)
            if '>Wir freuen uns, dass Sie sich' in html:
                print('Erfolgreich eingeloest')
            else:
                print('Status unklar - vermutlich erfolgreich eingeloest')
            # We'll trust our result anyways
            successful_vounter += 1
        finally:
            printSeparator()
except:
    print('Unbekannter Fehler')
    # raise
    pass
print('Anzahl erfolgreich eingeloester Gutscheine: %d / %d' % (successful_vounter, len(crawledVouchers)))

print('Druecke ENTER zum Schließen des Fensters')
input()
sys.exit()
