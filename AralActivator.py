'''
Created on 26.11.2019

@author: over_nine_thousand
'''

import os, json, re, sys, mechanize, time
from EmailCrawler import crawl_mails
from html.parser import HTMLParser
from datetime import date

# Global variables
INTERNAL_VERSION = '0.4.1'
PATH_STORED_VOUCHERS = os.path.join('vouchers.json')
PATH_STORED_ORDERS = os.path.join('orders.json')
PATH_STORED_SETTINGS = os.path.join('settings.json')
PATH_STORED_COOKIES = os.path.join('cookies.txt')
PATH_INPUT_MAILS = os.path.join('mails.txt')


BASE_DOMAIN = 'https://www.aral-supercard.de'

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
#             if control.name != None:
#                 print('submitKey: ' + control.name)
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
            form_index = getFormIndexBySubmitKey(br, 'supercardnumber')
            if form_index == -1:
                print('SuperCardForm konnte nicht gefunden werden')
                return
            br.select_form(nr=form_index)
            
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


    if successfullyActivatedOrdersCounter > 0:
        print('Es wurden %d neue Karten aktiviert' % successfullyActivatedOrdersCounter)
#     if successfullyActivatedOrdersCounter != numberof_un_activated_cards:
#         print('Anzahl fehlgeschlagener/uebersprungener Aktivierungen: ')
#     else:
#         print('Alle %d neuen Karten wurden erfolgreich aktiviert' % numberof_un_activated_cards)
    return
    
def crawlOrderNumbersFromMail(settings, orderArray):
        # TODO: Crawl order-date from mails and save it later on
        # Load mails
    use_old_crawler = False
    if use_old_crawler == True:
        try: 
            readFile = open(PATH_INPUT_MAILS, 'r')
            emailSource = readFile.read()
            readFile.close
        except:
            print('Failed to load ' + PATH_INPUT_MAILS)
        
        # Crawl data from emailSource
        if emailSource != None:
            print('Extrahiere Bestellnummern und Aktivierungscodes aus E-Mails ...')
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
                    currOrder = None
                    for o in orderArray:
                        if orderNumber == o['order_number']:
                            currOrder = o
                            break
                    if currOrder != None and 'activation_code' in currOrder:
                        # Skip existing orders that already have assigned order_numbers
                        # Debug, TODO: Use official logging functionality
                        # print('Ueberspringe bereits existierende Bestellnummer: ' + orderNumberStr)
                        continue
                    if currOrder == None:
                        currOrder = {'order_number':orderNumber}
                    currOrder ['activation_code'] = activationCode
                    orderArray.append(currOrder)
                    numberof_new_vouchers += 1
                if numberof_new_vouchers > 0:
                    print('%d neue Bestellungen gefunden' % numberof_new_vouchers)
                else:
                    print('Deine E-Mails enthielten keine neuen Bestellungen')
    else:
        crawl_mails(settings, orderArray)
    return

def crawlOrderNumbersFromAccount(br):
    # Load vouchers and activation codes from email source
    accountOrdersArray = []
    try: 
        readFile = open(PATH_STORED_ORDERS, 'r')
        settingsJson = readFile.read()
        readFile.close
        accountOrdersArray = json.loads(settingsJson)
    except:
        print('Failed to load ' + PATH_STORED_VOUCHERS)
    # TODO: Optimize to stop on known codes on last site --> Orders are sorted from newest --> oldest --> Saves time and http requests
    page_counter = 0
    max_items_per_page = 20
    numberof_new_items = 0
    while True:
        page_counter+= 1
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
            print('Alle Bestellnummern gefunden(?)')
            break
        elif len(currentCrawledOrderNumbers) < max_items_per_page:
            # Double-check
            print('Alle Bestellnummern gefunden(?) --> Aktuelle Seite enthaelt weniger als %d Elemente' %  len(currentCrawledOrderNumbers))
            break
        elif found_new_entry == False:
            # This improves speed significantly for users who have many orders in their account
            print('Stoppe Suche nach neuen Bestellnummern, da die letzten %d Eintraege bereits vom letzten Crawlvorgang bekannt sind' % len(currentCrawledOrderNumbers))
            break
        time.sleep(2)
        # Continue
    print('Anzahl neu erfasster Bestellnummern (seit dem letzten Start): %d auf insgesamt %d Seiten' % (numberof_new_items, page_counter))
    # Save these
    with open(PATH_STORED_ORDERS, 'w') as outfile:
        json.dump(accountOrdersArray, outfile)
    return accountOrdersArray
    
def activateAutomatic(br, orderArray):
    max_numberof_failures_in_a_row = 3
    numberof_failures_in_a_row = 0
    numberof_un_activated_cards = 0
    # Crawl all OrderNumbers from website
    accountOrderArray = crawlOrderNumbersFromAccount(br)
    if len(orderArray) == 0:
        print('Es konnten keine Bestellnummern im Account gefunden werden')
        return None
        
    for currOrder in orderArray:
        if 'activated' not in currOrder or currOrder['activated'] == False:
            numberof_un_activated_cards += 1
    
    # Now find out which orders are not yet activated AND have their activation_code given
    progressCounter = 0
    successfullyActivatedOrdersCounter = 0
    orderActivationImpossibleArray = []
    printSeparator()
    for orderInfo in orderArray:
        try:
            progressCounter += 1
            # Try to find activation code for current order number which should have been crawled beforehand from the users' emails
            order_number = orderInfo['order_number']
            # TODO: Why do we have to have a cast to int here?
            activationCode = int(orderInfo.get('activation_code', 0))
            if activationCode == 0:
                # Skip such items as we do not have the activation-number
                orderActivationImpossibleArray.append({'order_number':order_number,'failure_reason':'Aktivierungscode konnte nicht gefunden werden'})
                continue
            elif order_number not in accountOrderArray:
                orderActivationImpossibleArray.append({'order_number':order_number,'failure_reason':'Bestellnummer aus E-Mail existiert nicht im Aral Account'})
                continue
            print('Arbeite an Bestellung: %d mit Aktivierungscode %d' % (order_number, activationCode))
            isActivated = orderInfo.get('activated', False)
            #print('Bestellnummer = %d --> Aktivierungscode = %d' %(order_number, activationCode))
            
            if isActivated == True:
                # Skip already activated cards
                print('Diese Bestellnummer wurde bereits zuvor (per Script?) aktiviert')
                continue
            # TODO: Make sure that we're always logged-in!
            response = br.open('https://www.aral-supercard.de/services/bestellungen/detailansicht/' + str(order_number))
            html = getHTML(response)
            if 'Diese Bestellung konnte nicht angezeigt werden' in html:
                orderActivationImpossibleArray.append({'order_number':order_number,'failure_reason':'Ungueltige Bestellnummer --> Ueber einen anderen Aral Account bestellt??'})
                continue
            try:
                # TODO: Fix this so it will work for other card names as well
                card_infoMatchObject = re.compile(r'<th>Kartenart</th>\s*<th>Anzahl</th>\s*<th>Kartenwert EUR</th>\s*</tr>\s*<tr>\s*<td>(.*?)</td>\s*<td>1</td>\s*<td>(\d+,\d{1,2}) €</td>').search(html)
                voucher_name = card_infoMatchObject.group(1)
                # TODO: Replace this so we do not use this deprecated method!
                voucher_name = HTMLParser().unescape(voucher_name)
                #voucher_name = html.unescape(voucher_name)
                voucher_money_valueStr =  card_infoMatchObject.group(2).replace(',', '.')
                # TODO: Check for old balance value. Only set new value if old one does not exist or is lower than new one!
                orderInfo['balance'] = float(voucher_money_valueStr)
                # E.g. 'Aral SuperCard For You - Ostern - Eier    '
                orderInfo['voucher_name'] = voucher_name
                print('Kartenwert gefunden: %s €' % voucher_money_valueStr)
            except:
                # Failed to find money value --> Not a big problem
                print('Kartenwert nicht gefunden')
                pass
            isActivatedAccordingToOrderOverview = '<h3>Aktivierte Karten</h3>' in html
            #isActivatedAccordingToOrderOverview = bool(re.match(r'<h3>\s*Aktivierte Karten\s*</h3>', html))
            if isActivatedAccordingToOrderOverview:
                print('Bestellung ist laut Bestelluebersicht bereits aktiviert')
                orderInfo['activated'] = True
                continue
            print('Aktivierung Schritt 1 ...')
            time.sleep(2)
            response = br.open('https://www.aral-supercard.de/services/bestellungen/bestellung-aktivieren/' + str(order_number))
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
                orderActivationImpossibleArray.append({'order_number':order_number,'failure_reason':'Aktivierungscode ist falsch(?)'})
                continue
            elif 'ist erfolgreich bei uns eingegangen' not in html:
                print('Unbekannter Fehler')
                orderActivationImpossibleArray.append({'order_number':order_number,'failure_reason':'Unbekannter Fehler'})
                continue
            # Success! Yeey!
            # TODO: Save activation-date
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
    
    printSeparator()
    if len(orderActivationImpossibleArray) > 0:
        print('Liste von Bestellnummern, die noch nicht aktiviert werden konnten --> (Noch) kein Aktivierungscode vorhanden?')
        for failedOrder in orderActivationImpossibleArray:
            print(str(failedOrder['order_number']) + ' --> ' + failedOrder['failure_reason'])
    
    printSeparator()
    if successfullyActivatedOrdersCounter > 0:
        print('Anzahl erfolgreich aktivierter Karten: ' + str(successfullyActivatedOrdersCounter))
        print('Bedenke: SuperCards sind idR. erst ab dem naechsten Tag nach der Aktivierung gueltig!')
    else:
        print('Es wurden keine neuen Karten aktiviert --> Entweder es wurden bereits alle Karten aktiviert oder fuer manche Karten/Bestellungen existieren noch keine Aktivierungscodes')
#     if successfullyActivatedOrdersCounter != numberof_un_activated_cards:
#         print('Anzahl fehlgeschlagener/uebersprungener Aktivierungen: ')
#     else:
#         print('Alle %d neuen Karten wurden erfolgreich aktiviert' % numberof_un_activated_cards)
    return
    

def printSeparator():
    print('*******************************************************************')

def isLoggedIN(html):
    return 'class=\"login-link logout\"' in html

def loginAccount(br, settings):
    # Try to login via stored cookies first - Aral only allows one active session which means we will most likely have to perform a full login
    cookies = mechanize.LWPCookieJar(PATH_STORED_COOKIES)
    br.set_cookiejar(cookies)
    if settings['login_aral_email'] == None or settings['login_aral_password'] == None:
        print('Gib deine aral-supercard.de Zugangsdaten ein')
        print('Falls du ueber mehrere Accounts bestellt hast musst du dieses Script jeweils 1x pro Account in verschiedenen Ordnern duplizieren!')
        print('Bedenke, dass auch die jeweiligen E-Mail Adressen möglichst nur die Mails enthalten sollten, die auch zu den Bestellungen des eingetragenen Aral Accounts passen ansonsten wird der Aktivierungsprozess unnötig lange dauern und es erscheinen ggf. Fehlermeldungen.')
        print('Achtung: Logge dich NICHT per Browser auf der Aral Webseite ein solange dieses Script laeuft')
        print('Gib deine E-Mail ein:')
        settings['login_aral_email'] = input()
        print('Gib dein Passwort ein:')
        settings['login_aral_password'] = input()
    else:
        print('Gespeicherte aral-supercard Zugangsdaten wurden erfolgreich geladen')
        print('Verwende E-Mail: ' + account_email)
    response = br.open(BASE_DOMAIN)
    html = getHTML(response)
    logged_in = isLoggedIN(html)
    if not logged_in:
        print('Login aral | %s' % settings['login_aral_email'])
        response = br.open(BASE_DOMAIN + '/login')
        form_index = getFormIndexBySubmitKey(br, 'email')
        if form_index == -1:
            print('Login-Form konnte nicht gefunden werden')
            return False
        br.select_form(nr=form_index)
        br['email'] = settings['login_aral_email']
        br['password'] = settings['login_aral_password']
        response = br.submit()
        html = getHTML(response)
        if not isLoggedIN(html):
            print('Login fehlgeschlagen - Ungueltige Zugangsdaten? Korrigiere deine eingetragenen Zugangsdaten in der Datei %s bevor du dieses Script wieder startest!' % PATH_STORED_SETTINGS)
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
    return logged_in
    
    
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
    
settings.setdefault('login_aral_email', None)
settings.setdefault('login_aral_password', None)
settings.setdefault('requires_aral_account', True)
account_email = settings['login_aral_email']
account_password = ['login_aral_password']
requires_account = settings['requires_aral_account']

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
    logged_in = loginAccount(br, settings)


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
    # Save (account-) settings
    with open(PATH_STORED_SETTINGS, 'w') as outfile:
        json.dump(settings, outfile)
    
    print('Done - druecke ENTER zum Schließen des Fensters')
    # Debug
    # raise
    input()
    sys.exit()
