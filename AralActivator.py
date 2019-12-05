'''
Created on 26.11.2019

@author: over_nine_thousand
'''

import os, json, re, sys, mechanize, time

# Global variables
INTERNAL_VERSION = '0.3.4'
PATH_STORED_VOUCHERS = os.path.join('vouchers.json')
PATH_STORED_SETTINGS = os.path.join('settings.json')
PATH_STORED_COOKIES = os.path.join('cookies.txt')
PATH_INPUT_MAILS = os.path.join('mails.txt')


BASE_DOMAIN = 'https://www.aral-supercard.de'


def isLoggedIN(html):
    return 'class=\"login-link logout\"' in html

def userInputDefinedLengthNumber(exact_length):
    while True:
        input_str = input()
        if len(input_str) != exact_length:
            print('Eingabe ist groesser oder kleiner als ' + str(exact_length) + ' Stellen')
            continue
        if not input_str.isdecimal():
            print('Bitte gib eine ZAHL ein')
            continue
        return int(input_str)
    # Function END

    
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
    if supercard_hint == None or len(supercard_hint) >= 19 or  not supercard_hint.isdecimal():
        # 2019-12-02: Fallback to hardcoded value
        supercard_hint = '70566074'
    # TODO: Remove this check
    if supercard_hint != None and len(supercard_hint) < 19 and supercard_hint.isdecimal():
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
    print('Gib den Wert deiner Karten ein (alle Karten, die du einfuegst sollten jeweils denselben Wert in Euro haben):')
    return userInputNumber()

def getHTML(response):
    return response.read().decode('utf-8')

def getFormIndexBySubmitKey(br, submitKey):
    if submitKey == None:
        return None
    #print('Form debugger:')
    target_index = -1
    current_index = 0
    for form in br.forms():
        #print('Form index ' + str(current_index))
#         if form.name != None:
#             print ('Form name = ' + form.name)
        for control in form.controls:
#             print(control)
#             print(control.type)
#             print(control.name)
            if control.name != None:
                print('submitKey: ' + control.name)
            if control.name != None and control.name == submitKey:
                #print('Found form')
                target_index = current_index
                break
        current_index += 1
    return target_index

def getFormIndexByActionContains(br, actionPart):
    if actionPart == None:
        return None
    #print('Form debugger:')
    target_index = -1
    current_index = 0
    for form in br.forms():
        #print('Form index ' + str(current_index))
        if form.action == None:
            continue
        if actionPart in form.action:
            target_index = current_index
            break
        current_index += 1
    return target_index

def activateSemiAutomatic(br, orderArray):
    numberof_un_activated_cards = 0
    for currOrder in orderArray:
        isActivated = currOrder['activated']
        if isActivated == False:
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
            print('Aktiviere Karte von Bestellnummer %d / %d: %d' % (attemptedActivations, numberof_un_activated_cards, currOrder['order_number']))
            # Not needed anymore
            # print('Aktiviere Bestellung: %d' % currOrder['order_number'])
            
            response = br.open('https://www.aral-supercard.de/services/karte-aktivieren/')
            html = getHTML(response)
            # TODO: Improve this to make sure we got the correct form
            try:
                br.select_form(nr=2)
                card_number_hint = br['supercardnumber']
            except:
                # Fatal failure
                print('Form konnte nicht gefunden werden')
                raise
            
            # TODO: Add errorhandling for typos
            # TODO: Grab card number beginning from website so user has to type in less
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
                # TODO: Add higher error tolerance
                print('Unbekannter Fehler --> Stoppe')
                break
            
            successfullyActivatedOrdersCounter += 1
            # Update voucher status
            currOrder['activated'] = True
            # TODO: Add possibility to skip current voucher
            print('Aktiviere weitere Karten? 0 = Abbrechen')
            if loopCounter + 1 < len(orderArray) - 1:
                user_decision = input()
                if user_decision.isdecimal() and int(user_decision) == 0:
                    break
        finally:
            loopCounter += 1


    if successfullyActivatedOrdersCounter != numberof_un_activated_cards:
        print('Anzahl fehlgeschlagener/uebersprungener Aktivierungen: ')
    else:
        print('Alle %d neuen Karten wurden erfolgreich aktiviert' % numberof_un_activated_cards)
    # Def end
    
def crawlOrderNumbers(br, accountCrawledOrderNumbers, emailOrders):
    # TODO: Optimize to stop on known codes on last site --> Orders are sorted from newest --> oldest --> Saves time and http requests
    page_counter = 0
    max_items_per_page = 20
    while True:
        page_counter+= 1
        print('Lade Bestellnummern Seite %d von ?' % page_counter)
        response = br.open('https://www.aral-supercard.de/services/bestellungen?page=' + str(page_counter))
        html = getHTML(response)
        try:
            currentCrawledOrderNumbers = re.compile(r'/bestellungen/detailansicht/(\d+)').findall(html)
        except:
            print('Auf dieser Seite konnten keine Bestellnummern gefunden werden')
            break
        found_new_entry = False
        for currCrawledOrderNumber in currentCrawledOrderNumbers:
            if emailOrders != None or currCrawledOrderNumber not in emailOrders:
                found_new_entry = True
                accountCrawledOrderNumbers.append(int(currCrawledOrderNumber))
        page_check = '?page=' + str(page_counter + 1)
        # Stop-conditions and fail-safes
        if page_check not in html:
            print('Alle Bestellnummern gefunden(?)')
            break
        elif len(currentCrawledOrderNumbers) < max_items_per_page:
            # Double-check
            print('Alle Bestellnummern gefunden(?) --> Aktuelle Seite enthaelt weniger als %d Elemente' %  len(currentCrawledOrderNumbers))
            break
        elif found_new_entry == False:
            # TODO: Check if this works
            print('Stoppe Suche nach neuen Bestellnummern, da die letzten %d Eintraege bereits vom letzten Crawlvorgang bekannt sind' % len(currentCrawledOrderNumbers))
            break
        time.sleep(2)
        # Continue
    print('Anzahl gefundener Bestellnummern: %d auf insgesamt %d Seiten' % (len(accountCrawledOrderNumbers), page_counter))
    # End of while loop
    
def activateAutomatic(br, orderArray):
    max_numberof_failures_in_a_row = 3
    numberof_failures_in_a_row = 0
    numberof_un_activated_cards = 0
    for currOrder in orderArray:
        if currOrder['activated'] == False:
            numberof_un_activated_cards += 1
    # Crawl all OrderNumbers from website
    accountCrawledOrderNumbers = []
    crawlOrderNumbers(br, accountCrawledOrderNumbers, orderArray)
    if len(orderArray) == 0:
        print('Es konnten keine Bestellnummern gefunden werden --> Fehler im Script oder ungueltige Zugangsdaten')
        return None
    for element in accountCrawledOrderNumbers:
        print('Found orderNumber: ' + str(element))
    
    # Now find out which orders are not yet activated AND have their activation_code given
    progressCounter = 0
    successfullyActivatedOrdersCounter = 0
    orderActivationImpossibleArray = []
    for accountCrawledOrderNumber in accountCrawledOrderNumbers:
        try:
            progressCounter += 1
            # Try to find activation code for current order number which should have been crawled beforehand from the users' emails
            mailOrder = None
            for tmpOrder in orderArray:
                order_number = tmpOrder['order_number']
                if order_number == accountCrawledOrderNumber:
                    mailOrder = tmpOrder
                    break
            if mailOrder == None:
                # TODO: Add new items without activationnumber so we can improve the speed of our OrderCrawler
                # Skip such items as we do not have the activation-number
                #print('Bestellnummer konnte keiner E-Mail Bestellnummer zugeordnet werden --> Ueberspringe diese Nummer')
                orderActivationImpossibleArray.append({'order_number':accountCrawledOrderNumber,'failure_reason':'Aktivierungscode konnte nicht gefunden werden'})
                continue
            print('Arbeite an Bestellung: ' + str(accountCrawledOrderNumber))
            isActivated = mailOrder['activated']
            activationCode = mailOrder['activation_code']
            print('Bestellnummer = %d --> Aktivierungscode = %d' %(accountCrawledOrderNumber, activationCode))
            
            if isActivated:
                # Skip already activated cards
                print('Diese Bestellnummer wurde bereits zuvor (per Script?) aktiviert')
                continue
            # TODO: Make sure that we're always logged-in!
            response = br.open('https://www.aral-supercard.de/services/bestellungen/detailansicht/' + str(accountCrawledOrderNumber))
            html = getHTML(response)
            try:
                # TODO: Fix this so it will work for other card names as well
                voucher_money_valueStr =  re.compile(r'Individueller Wert Aral SuperCard[^<>]*</td>\s*<td>1</td>\s*<td>(\d+,\d{1,2}) €</td>').search(html).group(1).replace(',', '.')
                # TODO: Check for old balance value. Only set new value if old one does not exist or is lower than new one!
                mailOrder['balance'] = float(voucher_money_valueStr)
                print('Kartenwert gefunden: %s €' % voucher_money_valueStr)
            except:
                # Failed to find money value --> Not a big problem
                print('Kartenwert nicht gefunden')
                pass
            isActivatedAccordingToOrderOverview = '<h3>Aktivierte Karten</h3>' in html
            #isActivatedAccordingToOrderOverview = bool(re.match(r'<h3>\s*Aktivierte Karten\s*</h3>', html))
            if isActivatedAccordingToOrderOverview:
                print('Bestellung ist laut Bestelluebersicht bereits aktiviert')
                mailOrder['activated'] = True
                continue
            print('Aktivierung Schritt 1 ...')
            time.sleep(2)
            response = br.open('https://www.aral-supercard.de/services/bestellungen/bestellung-aktivieren/' + str(accountCrawledOrderNumber))
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
            print('Aktivierung Schritt 2 ...')
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
                orderActivationImpossibleArray.append({'order_number':accountCrawledOrderNumber,'failure_reason':'Aktivierungscode ist falsch(?)'})
                continue
            elif 'ist erfolgreich bei uns eingegangen' not in html:
                print('Unbekannter Fehler')
                orderActivationImpossibleArray.append({'order_number':accountCrawledOrderNumber,'failure_reason':'Unbekannter Fehler'})
                continue
            # Success! Yeey!
            mailOrder['activated'] = True
            successfullyActivatedOrdersCounter += 1
            # Reset that counter
            numberof_failures_in_a_row = 0
            # Cooldown
            time.sleep(2)
            # Continue with the next voucher
        finally:
            if numberof_failures_in_a_row >= max_numberof_failures_in_a_row:
                print('Mehr als %d unbekannte Fehler hintereinander --> Abbruch')
                break
    
    if len(orderActivationImpossibleArray) > 0:
        print('Liste von Bestellnummern, die noch nicht aktiviert werden konnten --> (Noch) kein Aktivierungscode vorhanden?')
        for failedOrder in orderActivationImpossibleArray:
            print(str(failedOrder['order_number']) + ' --> ' + failedOrder['failure_reason'])
    
    if successfullyActivatedOrdersCounter > 0:
        print('Anzahl erfolgreich aktivierter Karten: ' + str(successfullyActivatedOrdersCounter))
    else:
        print('Es wurden keine neuen Karten aktiviert --> Fehler oder es gibt (noch) keine neuen Aktivierungscodes zu ausstehenden Bestellungen')
    if successfullyActivatedOrdersCounter != numberof_un_activated_cards:
        print('Anzahl fehlgeschlagener/uebersprungener Aktivierungen: ')
    else:
        print('Alle %d neuen Karten wurden erfolgreich aktiviert' % numberof_un_activated_cards)
    # Def end
    
# Main script START
print('Welcome to AralActivator %s' % INTERNAL_VERSION)

print('Achtung: Dieses Script kann nur Bestellungen mit jeweils einer zu aktivierenden Karte verarbeiten und nur Bestellungen auf diesem Account!')

settings = {}
# Load settings
try: 
    readFile = open(PATH_STORED_SETTINGS, 'r')
    settingsJson = readFile.read()
    settings = json.loads(settingsJson)
    readFile.close
except:
    print('Failed to load ' + PATH_STORED_SETTINGS)
    
settings.setdefault('email', None)
settings.setdefault('password', None)
settings.setdefault('requires_account', True)
account_email = settings['email']
account_password = ['password']
requires_account = settings['requires_account']

# Prepare browser
br = mechanize.Browser()
# br.set_all_readonly(False)    # allow everything to be written to
br.set_handle_robots(False)  # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.set_handle_referer(True)
br.set_handle_redirect(True)
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36')]

if requires_account == False:
    # Continue without loggin in
    print('Fahre ohne login fort')
else:
    # Try to login via stored cookies first - Aral only allows one active session which means we will most likely have to perform a full login
    cookies = mechanize.LWPCookieJar(PATH_STORED_COOKIES)
    br.set_cookiejar(cookies)
    
    response = br.open(BASE_DOMAIN)
    html = getHTML(response)
    logged_in = isLoggedIN(html)
    if not logged_in:
        print('Versuche vollstaendigen Login')
        response = br.open(BASE_DOMAIN + '/login')
        # TODO: Improve this to make sure we got the correct form
        try:
            br.select_form(nr=2)
            email_field = br['email']
            password_field = br['password']
        except:
            # Fatal failure
            print('Login-Form konnte nicht gefunden werden')
            raise
        br['email'] = settings['email']
        br['password'] = settings['password']
        response = br.submit()
        html = getHTML(response)
        if not isLoggedIN(html):
            print('Login failed')
            logged_in = False
        else:
            print('Vollstaendiger Login erfolgreich')
            logged_in = True
    else:
        print('Login ueber gueltige Cookies erfolgreich')
    
    # Save cookies and logindata
    cookies.save()
    with open(PATH_STORED_SETTINGS, 'w') as outfile:
        json.dump(settings, outfile)
    if settings['email'] == None or settings['password'] == None:
        print('Gib deine aral-supercard.de Zugangsdaten ein')
        print('Gib deine E-Mail ein:')
        settings['email'] = input()
        print('Gib dein Passwort ein:')
        settings['password'] = input()
    else:
        print('Gespeicherte Zugangsdaten wurden erfolgreich geladen')
        print('Verwende email: ' + account_email)

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
# Load mails
try: 
    readFile = open(PATH_INPUT_MAILS, 'r')
    emailSource = readFile.read()
    readFile.close
except:
    print('Failed to load ' + PATH_INPUT_MAILS)

# TODO: Maybe add the possibility to let the user add vouchers manually

# Crawl data from emailSource
if emailSource != None:
    print('Extrahiere Bestellnummern und Aktivierungscodes aus den E-Mails ...')
    crawledOrderNumbers = re.compile(r'Ihre Aral SuperCard Bestellung\s*(\d+)').findall(emailSource)
    crawledActivationCodes = re.compile(r'Der Aktivierungscode lautet\s*:\s*(\d+)').findall(emailSource)
    numberof_new_vouchers = 0
    if len(crawledOrderNumbers) != len(crawledActivationCodes):
        print('Email crawler failed: Length mismatch')
    else:
        for i in range(len(crawledOrderNumbers)):
            orderNumberStr = crawledOrderNumbers[i]
            orderNumber = int(orderNumberStr)
            activationCode = int(crawledActivationCodes[i])
            alreadyExists = False
            for o in orderArray:
                if orderNumber == o['order_number']:
                    alreadyExists = True
                    break
            if alreadyExists:
                # Skip existing mails
                # Debug, TODO: Use official logging functionality
                # print('Ueberspringe bereits existierende Bestellnummer: ' + orderNumberStr)
                continue
            #print('Bestellnummer:Aktivierungscode --> ' + orderNumberStr + ':' + str(activationCode))
            currOrder = {'order_number':orderNumber,'activation_code':activationCode,'activated':False}
            # TODO: Add activation date (= current date)
            # TODO: Add valid_until field (+ 3 years from activation date on)
            orderArray.append(currOrder)
            numberof_new_vouchers += 1
        if numberof_new_vouchers > 0:
            print('%d neue Bestellungen gefunden' % numberof_new_vouchers)
        else:
            print('Deine E-Mails enthielten keine neuen Bestellungen')

if orderArray == None:
    # There is nothing we can do --> Exit
    print('Es konnten keine Bestellungen gefunden werden --> Abbruch')
    sys.exit()

# TODO: Crawel all order-IDs from here, then activate all orders for which we do have activationCodes for: https://www.aral-supercard.de/services/bestellungen?page=1
#ordersInAccount = []

if logged_in == False and requires_account == True:
    print('Anmeldung fehlgeschlagen und manuelles Aktivieren deaktiviert --> Abbruch')
    sys.exit()

try:
    if requires_account == False:
        activateSemiAutomatic(br, orderArray)
    else:
        activateAutomatic(br, orderArray)

finally:
    # Make sure to always save orders!
    with open(PATH_STORED_VOUCHERS, 'w') as outfile:
        json.dump(orderArray, outfile)
    
    print('Done - druecke ENTER zum Schließen des Fensters')
    # Debug
    #raise
    input()
    sys.exit()
