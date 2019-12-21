import re, sys, time
from Helper import *

# Removes all products from the shopping cart
def dumpShoppingCart(br):
    response = br.open('https://www.aral-supercard.de/shop/abschluss')
    html = getHTML(response)
    try:
        try:
            articleDeleteURLs = re.compile(r'\"(https?://www.aral-supercard\.de/shop/warenkorb/artikel-loeschen/[^<>\"]+)\"').findall(html)
        except:
            print('Warenkorb ist bereits leer')
            return
        print('Anzahl gefundener Artikel im Warenkorb: %d' % len(articleDeleteURLs))
        delete_article_index = 0
        for articleDeleteURL in articleDeleteURLs:
            delete_article_index += 1
            print('Loesche Artikel %d % %d' % (delete_article_index, len(articleDeleteURLs)))
            response = br.open(articleDeleteURL)
            # html = getHTML(response)
    except:
        print('Fehler beim Leeren des Warenkorbs oder keine Artikel')
    return

print('Welcome to AralActivator %s' % getVersion())
print('Gib deine Gutscheine ein und druecke 2x ENTER.')
print('Falls  du diese per Groupon [PDF] bekommen hast, markiere den kompletten Text der PDF und fuege ihn hier ein!')

voucherSource = None

total_numberof_vouchers = 0
voucher_input_loop_counter = 0
crawledVouchers = None

settings = loadSettings()
br = prepareBrowser()

while total_numberof_vouchers == 0:
    voucherSource = ''
    print('Gib deine Gutscheincodes oder den kompletten Inhalt der Groupon PDF ein (druecke dann 2x ENTER dann geht\'s weiter):')
    # Improvised multi line input: https://stackoverflow.com/questions/30239092/how-to-get-multiline-input-from-user
    counter_lines_of_input = 0
    currInput = '_TEST_'
    while currInput != '' and counter_lines_of_input <= 5000:
        currInput = input()
        voucherSource += currInput + '\n'
        counter_lines_of_input += 1
        # End of user input handling
    crawledVouchers = set(re.compile(r'([A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4})').findall(voucherSource))
    total_numberof_vouchers = len(crawledVouchers)

print('Anzahl gefundener Gutscheine: ' + str(len(crawledVouchers)))
index = 0
for voucher in crawledVouchers:
    index += 1
    print('Gutschein %d : %s' % (index, voucher))

logged_in = loginAccount(br, settings)
if not logged_in:
    print('Login-Fehler')
    sys.out()

print('Achtung! Alle Gutscheine werden auf deine bevorzugte Adresse bestellt! Pruefe deine Adresse bevor du die Einloesung startest!')
print('Falls die eingegebenen Gutscheincodes fuer 30+5€ Karten sind, druecke ENTER im den Vorgang zu starten; falls nicht, gib jetzt den Link zum passenden Aktionsartikel ein z.B. \'https://www.aral-supercard.de/shop/produkt/jp-performance-einkaufen-tanken-individueller-wert-sondermotiv-motor-show-2124\'')
user_input_article_url = input()
if 'http' in user_input_article_url:
    print('Gueltige eingabe --> Verwende eingegebenen Artikel-Link')
    article_url = user_input_article_url
else:
    print('Kein Link oder ungueltige Eingabe --> Verwende 30+5 Artikel-Link')
    article_url = 'https://www.aral-supercard.de/shop/produkt/aral-supercard-einkaufen-tanken-30-2123'

print('Verwende folgende URL als Artikel-Link: ' + article_url)

printSeparator()

index = 0
successful_vounter = 0
wait_seconds_between_requests = 1
# TODO: Add html loggers
numberof_steps = 7
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
        response = br.open(article_url)
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
        response = br.open('https://www.aral-supercard.de/shop/abschluss')
        html = getHTML(response)
        # Next step
        print('Schritt 4 / %d: Fuege Gutschein ein und pruefe Gueltigkeit' % numberof_steps)
        form_index = getFormIndexBySubmitKey(br, 'voucher_1')
        if form_index == -1:
            print('Konnte GutscheinForm nicht finden')
            sys.exit()
        br.select_form(nr=form_index)
        voucherElements = currentVoucher.split('-')
        br['voucher_1'] = voucherElements[0]
        br['voucher_2'] = voucherElements[1]
        br['voucher_3'] = voucherElements[2]
        time.sleep(wait_seconds_between_requests)
        response = br.submit()
        html = getHTML(response)
        if 'Der Gutscheincode ist unbekannt oder nicht mehr' in html:
            print('Gutschein ungueltig oder bereits eingeloest')
            continue
        # Important errorhandling!
        try:
            cart_amountStr = re.compile(r'<span>Zwischensumme</span>\s*<span>\s*([0-9]+,[0-9]+)').search(html).group(1)
            cart_amountStr = cart_amountStr.replace(',', '.')
            cart_amount = float(cart_amountStr)
            # With our voucher we should always pay 0€
            if cart_amount > 0:
                print('Fehler: Zwischensumme ist groesser als 0€')
                continue
        except:
            # print(html)
            print('Fehler: Konnte Zwischensumme nicht finden')
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
        print('Schritt 6 / %d: Weiter von den Rechnungsadresse --> Lieferadresse' % numberof_steps)
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

print('Anzahl erfolgreich eingeloester Gutscheine: %d / %d' %(successful_vounter, len(crawledVouchers)))

print('Done')