import os, json, re, sys, mechanize, time
from EmailCrawler import crawl_mails, crawl_mailsOLD, findOrderObjectByOrderNumber
from Helper import *
from html.parser import HTMLParser
from datetime import date

# Global variables
PATH_STORED_VOUCHERS = os.path.join('vouchers.json')
PATH_STORED_ORDERS = os.path.join('orders.json')


# Returns user input Integer
def userInputNumber():
    while True:
        input_str = input()
        try:
            input_int = int(input_str)
            return input_int
        except:
            print('Bitte gib eine ZAHL ein')
            continue
    # Function END


def getRegistrationCode():
    print('Gib den Registrierungscode ein (4-stellig):')
    return userInputDefinedLengthNumber(4)
    # Function END


def getSerialNumber():
    print('Gib die Seriennummer ein (10-stellig):')
    return userInputDefinedLengthNumber(10)
    # Function END


def getSupercardNumber(supercard_hint):
    # According to their website, their card numbers are really 19 digits lol
    exact_length = 19
    if supercard_hint is not None or len(supercard_hint) >= 19 or not supercard_hint.isdecimal():
        # 2019-12-02: Fallback to hardcoded value
        supercard_hint = '70566074'
    # TODO: Remove this check
    if supercard_hint is not None and len(supercard_hint) < 19 and supercard_hint.isdecimal():
        # Parts of our number are already given - only ask user for the rest
        exact_length = exact_length - len(supercard_hint)
        print('Gib die restlichen %d Stellen der SuperCard Nr. ein: %s' % (exact_length, supercard_hint))
        supercard_number = supercard_hint + str(userInputDefinedLengthNumber(exact_length))
        # Debug
        print('SupercardNumber = ' + supercard_number)
        return int(supercard_number)
    else:
        print('Gib die SuperCard Nr. ein (%d-stellig):' % exact_length)
        return int(userInputDefinedLengthNumber(exact_length))
    # Function END


def getActivationCode():
    print('Gib den Aktivierungscode ein (10-stellig):')
    return userInputDefinedLengthNumber(10)
    # Function END


def getVoucherBalance():
    print(
        'Gib den Wert deiner Karten ein (alle Karten, die du einfuegst sollten jeweils denselben Wert in Euro haben):')
    return userInputNumber()


def activateSemiAutomatic(br, orderArray):
    numberof_un_activated_cards = 0
    for currOrder in orderArray:
        isActivated = currOrder['activated']
        if isActivated is False:
            numberof_un_activated_cards += 1

    card_number_hint = None
    loopCounter = 0
    attemptedActivations = 0
    successfullyActivatedOrdersCounter = 0
    for currOrder in orderArray:
        try:
            isActivated = currOrder['activated']
            if isActivated:
                # Skip already activated cards
                continue
            attemptedActivations += 1
            print('Aktiviere Karte von Bestellnummer %d / %d: %d' % (
                attemptedActivations, numberof_un_activated_cards, currOrder['order_number']))
            # Not needed anymore
            # print('Aktiviere Bestellung: %d' % currOrder['order_number'])

            response = br.open('https://www.aral-supercard.de/services/karte-aktivieren/')
            html = getHTML(response)
            form_index = getFormIndexBySubmitKey(br, 'supercardnumber')
            if form_index == -1:
                print('SuperCardForm konnte nicht gefunden werden')
                return
            br.select_form(nr=form_index)
            currOrder['card_number'] = getSupercardNumber(card_number_hint)
            # We do not need this information
            # currVoucher['serial_number'] = getSerialNumber()
            currOrder['registration_code'] = getRegistrationCode()
            # We already have our activation code!
            # currOrder['activation_code'] = getActivationCode()

            br['supercardnumber'] = str(currOrder['card_number'])
            br['activationcode'] = str(currOrder['activation_code'])
            br['securecode'] = str(currOrder['registration_code'])
            response = br.submit()
            html = getHTML(response)
            # General errormessage html class: <div class="ap-message ap-message--error ap-message--icon">
            if 'Ihr Karte konnte nicht aktiviert werden' in html:
                # <li>Ihr Karte konnte nicht aktiviert werden. Bitte kontrollieren Sie Ihre Aral SuperCard Nummer.</li>
                print('Karte konnte nicht aktiviert werden')
                continue
            if 'Karte ist bereits aktiv' in html:
                # <li>Karte ist bereits aktiv! <a href="https://www.aral-supercard.de/services/kartenguthaben-abrufen">Hier Ihr Guthaben abfragen!</a></li>
                print('Karte wurde bereits vorher (per Webseite?) aktiviert')
            elif 'Kartenaktivierung erfolgreich' in html:
                # >Kartenaktivierung erfolgreich</h1>
                print('Karte wurde erfolgreich aktiviert')
            else:
                print('Unbekannter Fehler --> Stoppe')
                break

            successfullyActivatedOrdersCounter += 1
            # Update voucher status
            currOrder['activated'] = True
            print('Aktiviere weitere Karten? 0 = Abbrechen')
            if loopCounter + 1 < len(orderArray) - 1:
                user_decision = input()
                if user_decision.isdecimal() and int(user_decision) == 0:
                    break
        finally:
            loopCounter += 1

    if successfullyActivatedOrdersCounter > 0:
        print('Es wurden %d neue Karten aktiviert' % successfullyActivatedOrdersCounter)
    return

# Old function for manual mode
def crawlOrderNumbersFromMail(settings, orderArray):
    use_old_mail_crawler = False
    if use_old_mail_crawler is True:
        crawl_mailsOLD(settings, orderArray)
    else:
        crawl_mails(settings, orderArray)
    return


def crawlOrdersFromAccount(br):
    # Load vouchers and activation codes from email source
    accountOrdersArray = []
    try:
        readFile = open(PATH_STORED_ORDERS, 'r')
        ordersJson = readFile.read()
        readFile.close
        accountOrdersArray = json.loads(ordersJson)
    except:
        print('Failed to load ' + PATH_STORED_VOUCHERS)
    page_counter = 0
    max_items_per_page = 20
    numberof_new_items = 0
    while True:
        page_counter += 1
        print('Lade Bestelldaten von Aral | Seite %d von ?' % page_counter)
        response = br.open('https://www.aral-supercard.de/services/bestellungen?page=' + str(page_counter))
        html = getHTML(response)
        try:
            currentCrawledOrderNumbers = re.compile(r'/bestellungen/detailansicht/(\d+)').findall(html)
        except:
            print('Auf dieser Seite konnten keine Bestellnummern gefunden werden')
            break
        found_new_entry = False
        for currCrawledOrderNumber in currentCrawledOrderNumbers:
            currCrawledOrderNumber = int(currCrawledOrderNumber)
            if currCrawledOrderNumber not in accountOrdersArray:
                found_new_entry = True
                numberof_new_items += 1
                accountOrdersArray.append(currCrawledOrderNumber)
        next_page_available = '?page=' + str(page_counter + 1)
        # Stop-conditions and fail-safes
        if next_page_available not in html:
            print('Letzte Seite mit Bestellnummern erreicht')
            break
        elif len(currentCrawledOrderNumbers) < max_items_per_page:
            # Double-check
            print('Vermutlich alle Bestellnummern gefunden --> Aktuelle Seite enthaelt weniger als %d Elemente --> Suche nicht weiter auf naechster Seite' % max_items_per_page)
            break
        elif not found_new_entry:
            # This improves speed significantly for users who have many orders in their account
            print('Stoppe Suche nach neuen Bestellnummern, da alle Betellnummern der aktuellen Seite bereits vom letzten Crawlvorgang bekannt sind.')
            break
        time.sleep(2)
        # Continue
    print('Anzahl NEU erfasster Bestellnummern (seit dem letzten Start): %d auf insgesamt %d Seiten' % (numberof_new_items, page_counter))
    # Save found orders
    with open(PATH_STORED_ORDERS, 'w') as outfile:
        json.dump(accountOrdersArray, outfile)
    return accountOrdersArray


def activateAutomatic(br, orderArray):
    max_numberof_failures_in_a_row = 3
    numberof_failures_in_a_row = 0
    printSeparator()
    # Crawl all OrderNumbers from website
    accountOrderArray = crawlOrdersFromAccount(br)
    if len(orderArray) == 0:
        print('Es konnten keine Bestellnummern im Account gefunden werden')
        return None

    # Collect orders which can be activated
    activatable_orders = []
    un_activatable_orders = []
    for account_order_number in accountOrderArray:
        stored_order = findOrderObjectByOrderNumber(orderArray, account_order_number)
        if stored_order is None:
            new_order = {'order_number': account_order_number}
            orderArray.append(new_order)
            continue
        activated = stored_order.get('activated', False)
        activation_code = stored_order.get('activation_code', None)
        if not activated and activation_code is not None:
            activatable_orders.append(account_order_number)
            continue
        un_activatable_orders.append(account_order_number)

    if len(activatable_orders) == 0:
        print('Es wurden KEINE aktivierbaren Bestellungen gefunden')
        return
    else:
        print('%d aktivierbare Bestellungen gefunden' % len(activatable_orders))

    printSeparator()

    # Now find out which orders are not yet activated AND have their activation_code given
    progressCounter = 0
    successfullyActivatedOrdersCounter = 0
    orderActivationImpossibleArray = []
    printSeparator()
    for order_number in activatable_orders:
        try:
            progressCounter += 1
            orderInfo = findOrderObjectByOrderNumber(orderArray, order_number)
            # TODO: I made a mistake in an older version and stored this as a String so let's parse it to int just to make sure it works
            activationCode = int(orderInfo.get('activation_code', None))
            print('Arbeite an Bestellung %d / %d : Bestellnummerr: %d | Aktivierungscode: %d' % (progressCounter, len(activatable_orders), order_number, activationCode))
            print('Aktivierung Schritt 1 [services/bestellungen/detailansicht/] ...')
            response = br.open('https://www.aral-supercard.de/services/bestellungen/detailansicht/' + str(order_number))
            html = getHTML(response)
            if 'Diese Bestellung konnte nicht angezeigt werden' in html:
                # This should never happen
                orderActivationImpossibleArray.append({'order_number': order_number,
                                                       'failure_reason': 'Ungueltige Bestellnummer --> Ueber einen anderen Aral Account bestellt??'})
                continue
            try:
                card_infoMatchObject = re.compile(
                    r'<th>Kartenart</th>\s*<th>Anzahl</th>\s*<th>Kartenwert EUR</th>\s*</tr>\s*<tr>\s*<td>(.*?)</td>\s*<td>1</td>\s*<td>(\d+,\d{1,2}) €</td>').search(
                    html)
                voucher_name = card_infoMatchObject.group(1)
                # TODO: Replace this so we do not use this deprecated method!
                voucher_name = HTMLParser().unescape(voucher_name)
                # voucher_name = html.unescape(voucher_name)
                voucher_money_valueStr = card_infoMatchObject.group(2).replace(',', '.')
                balance = orderInfo.get('balance', None)
                if balance is None:
                    orderInfo['balance'] = float(voucher_money_valueStr)
                # E.g. 'Aral SuperCard For You - Ostern - Eier    '
                orderInfo['voucher_name'] = voucher_name
                print('Kartenwert gefunden: %s €' % voucher_money_valueStr)
            except:
                # Failed to find money value --> Not a big problem
                print('Kartenwert nicht gefunden')
                pass
            isActivatedAccordingToOrderOverview = '<h3>Aktivierte Karten</h3>' in html
            # isActivatedAccordingToOrderOverview = bool(re.match(r'<h3>\s*Aktivierte Karten\s*</h3>', html))
            if isActivatedAccordingToOrderOverview:
                print('Bestellung ist laut Bestelluebersicht bereits aktiviert')
                orderInfo['activated'] = True
                continue
            print('Aktivierung Schritt 2 [services/bestellungen/bestellung-aktivieren/] ...')
            time.sleep(2)
            response = br.open(
                'https://www.aral-supercard.de/services/bestellungen/bestellung-aktivieren/' + str(order_number))
            html = getHTML(response)
            form_index = getFormIndexBySubmitKey(br, 'activationCode')
            if form_index == -1:
                print('Konnte AktivierungsForm nicht finden --> Abbruch')
                break
            br.select_form(nr=form_index)
            br['activationCode'] = str(activationCode)
            # We want to activate all cards of this order at once although most users who will use this script will only have one card per order!
            br.form['order'] = ['1']
            response = br.submit()
            html = getHTML(response)
            print('Aktivierung Schritt 3 [Aktivierung bestaetigen] ...')
            form_index = getFormIndexByActionContains(br, 'aktivierung-bestaetigen')
            if form_index == -1:
                print('Konnte AktivierungsBestaetigungsForm nicht finden --> Abbruch')
                break
            br.select_form(nr=form_index)
            # Cooldown
            time.sleep(1)
            response = br.submit()
            html = getHTML(response)
            if '>Bitte überprüfen Sie Ihren Aktivierungscode<' in html:
                print('Ungueltiger Aktivierungscode')
                orderActivationImpossibleArray.append(
                    {'order_number': order_number, 'failure_reason': 'Aktivierungscode ist falsch(?)'})
                continue
            elif 'ist erfolgreich bei uns eingegangen' not in html:
                print('Unbekannter Fehler')
                orderActivationImpossibleArray.append(
                    {'order_number': order_number, 'failure_reason': 'Unbekannter Fehler'})
                continue
            # Activation successful!
            orderInfo['activated'] = True
            orderInfo['activation_date'] = date.today().strftime("%Y-%m-%d")
            successfullyActivatedOrdersCounter += 1
            # Reset that counter
            numberof_failures_in_a_row = 0
            # Cooldown
            time.sleep(2)
            # Continue with the next voucher
            print('Bestellung erfolgreich aktiviert: %d' % order_number)
        finally:
            if numberof_failures_in_a_row >= max_numberof_failures_in_a_row:
                print('Mehr als %d unbekannte Fehler hintereinander --> Abbruch')
                break
            printSeparator()

    if len(orderActivationImpossibleArray) > 0:
        print(
            'Liste von Bestellnummern, die noch nicht aktiviert werden konnten --> (Noch) kein Aktivierungscode vorhanden?')
        for failedOrder in orderActivationImpossibleArray:
            print(str(failedOrder['order_number']) + ' --> ' + failedOrder['failure_reason'])
        printSeparator()

    if successfullyActivatedOrdersCounter > 0:
        print('Anzahl erfolgreich aktivierter Karten: ' + str(successfullyActivatedOrdersCounter))
        print('Bedenke: SuperCards sind idR. erst ab dem naechsten Tag nach der Aktivierung gueltig!')
    else:
        print(
            'Es wurden keine neuen Karten aktiviert --> Entweder es wurden bereits alle Karten aktiviert oder fuer manche Karten/Bestellungen existieren noch keine Aktivierungscodes')
    return


# Main script START
print('Welcome to AralActivator %s' % getVersion())

print(
    'Achtung: Dieses Script kann nur Bestellungen aktivieren, die mit dem hier eingetragenen Aral-supercard.de Account bestellt wurden!')

printSeparator()

# Load settings
settings = loadSettings()
requires_account = settings['requires_aral_account']

br = prepareBrowser()

if requires_account is False:
    # Continue without loggin in
    print('Fahre ohne login fort')
else:
    logged_in = loginAccount(br, settings)

printSeparator()

# Load vouchers and activation codes from email source
orderArray = []
emailSource = None
try:
    readFile = open(PATH_STORED_VOUCHERS, 'r')
    settingsJson = readFile.read()
    readFile.close
    orderArray = json.loads(settingsJson)
except:
    print('Failed to load ' + PATH_STORED_VOUCHERS)

crawlOrderNumbersFromMail(settings, orderArray)

if orderArray is None:
    # There is nothing we can do --> Exit
    print('Es konnten keine Bestellungen gefunden werden --> Abbruch')
    sys.exit()

if not logged_in and requires_account:
    print('Anmeldung fehlgeschlagen und manuelles Aktivieren deaktiviert --> Abbruch')
    sys.exit()

try:
    if not requires_account:
        # Old version
        activateSemiAutomatic(br, orderArray)
    else:
        activateAutomatic(br, orderArray)

finally:
    # Make sure to always save orders!
    with open(PATH_STORED_VOUCHERS, 'w') as outfile:
        json.dump(orderArray, outfile)
    # Save (account-) settings
    with open(getSettingsPath(), 'w') as outfile:
        json.dump(settings, outfile)

    print('Druecke ENTER zum Schließen des Fensters')
    # Debug
    # raise
    input()
    sys.exit()
