'''
Created on 26.11.2019

@author: over_nine_thousand
'''

import os, json, re, sys, mechanize

# Global variables
INTERNAL_VERSION = '0.1.4'
PATH_STORED_VOUCHERS = os.path.join('vouchers.json')
PATH_STORED_SETTINGS = os.path.join('settings.json')
PATH_STORED_COOKIES = os.path.join('cookies.txt')
PATH_INPUT_MAILS = os.path.join('mails.txt')


BASE_DOMAIN = 'https://www.aral-supercard.de'


def isLoggedIN(html):
    return b'class=\"login-link logout\"' in html

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

if settings['email'] == None or settings['password'] == None:
    print('Gib deine aral-supercard.de Zugangsdaten ein')
    print('Gib deine E-Mail ein:')
    settings['email'] = input()
    print('Gib dein Passwort ein:')
    settings['password'] = input()
else:
    print('Gespeicherte Zugangsdaten wurden erfolgreich geladen')
    print('Verwende email: ' + account_email)


# Prepare browser
br = mechanize.Browser()
# br.set_all_readonly(False)    # allow everything to be written to
br.set_handle_robots(False)  # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36')]
# Try to login via stored cookies first - Aral only allows one active session which means we will most likely have to perform a full login
cookies = mechanize.LWPCookieJar(PATH_STORED_COOKIES)
br.set_cookiejar(cookies)

response = br.open(BASE_DOMAIN)
html = response.read()
if not isLoggedIN(html):
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
    html = response.read()
    if not isLoggedIN(html):
        print('Login failed')
        sys.exit()
    else:
        print('Vollstaendiger Login erfolgreich')
else:
    print('Login ueber gueltige Cookies erfolgreich')

# Save cookies and logindata
cookies.save()
with open(PATH_STORED_SETTINGS, 'w') as outfile:
    json.dump(settings, outfile)

# TODO: 
# Load settings and user data
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
    voucherBalance = 0
    crawledOrderNumbers = re.compile(r'Ihre Aral SuperCard Bestellung\s+(\d+)').findall(emailSource)
    crawledActivationCodes = re.compile(r'Der Aktivierungscode lautet:\s*(\d+)').findall(emailSource)
    numberof_new_vouchers = 0
    if len(crawledOrderNumbers) != len(crawledActivationCodes):
        print('Email crawler failed: Length mismatch')
    else:
        voucherBalance = 0
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
                print('Ueberspringe bereits existierende Bestellnummer: ' + orderNumberStr)
                continue
            if voucherBalance == 0:
                voucherBalance = getVoucherBalance()
            # print('Adding ' + orderNumberStr + ':' + activationCodeStr)
            tmpVoucherList = []
            currOrder = {'order_number':orderNumber}
            # TODO: Add activation date (= current date)
            # TODO: Add valid_until field (+ 3 years from activation date on)
            currVoucher = {'activation_code':activationCode, 'activated':False, 'start_balance':voucherBalance, 'current_balance':voucherBalance}
            tmpVoucherList.append(currVoucher)
            currOrder['vouchers'] = tmpVoucherList
            orderArray.append(currOrder)
            numberof_new_vouchers += 1
        print('%d neue Bestellungen gefunden' % numberof_new_vouchers)
        if numberof_new_vouchers > 0:
            print('Gesamtwert aller neuen Bestellungen: %d' % (numberof_new_vouchers * voucherBalance))
        else:
            print('Deine E-Mails enthielten keine neuen Bestellungen')

if orderArray == None:
    # There is nothing we can do --> Exit
    print('Es konnten keine Bestellungen gefunden werden --> Abbruch')
    sys.exit()

# TODO: Crawel all order-IDs from here, then activate all orders for which we do have activationCodes for: https://www.aral-supercard.de/services/bestellungen?page=1
#ordersInAccount = []

# TODO: Add functionality
# print('What do you want to do?')
# print('(0) = exit')
# print('(1) = activate cards')
# print('(2) = add new cards')

numberof_un_activated_cards = 0
for currOrder in orderArray:
    currVoucher = currOrder['vouchers'][0]
    isActivated = currVoucher['activated']
    if isActivated == False:
        numberof_un_activated_cards += 1

try:
    card_number_hint = None
    loopCounter = 0
    attemptedActivations = 0
    successfullyActivatedOrdersCounter = 0
    for currOrder in orderArray:
        try:
            currVoucher = currOrder['vouchers'][0]
            isActivated = currVoucher['activated']
            if isActivated:
                # Skip already activated cards
                continue
            attemptedActivations += 1
            print('Aktiviere Karte von Bestellnummer %d / %d: %d' % (attemptedActivations, numberof_un_activated_cards, currOrder['order_number']))
            # Not needed anymore
            # print('Aktiviere Bestellung: %d' % currOrder['order_number'])
            
            response = br.open('https://www.aral-supercard.de/services/karte-aktivieren/')
            html = response.read()
            # TODO: Improve this to make sure we got the correct form
            try:
                br.select_form(nr=2)
                card_number_hint = br['supercardnumber']
            except:
                # Fatal failure
                print('Form konnte nicht gefunden werden')
                raise
            
            # Debug: output contents of form
            # for f in br.forms():
            #     print(f)
            
            # TODO: Add errorhandling for typos
            # TODO: Grab card number beginning from website so user has to type in less
            currVoucher['card_number'] = getSupercardNumber(card_number_hint)
            # We do not need this information
            # currVoucher['serial_number'] = getSerialNumber()
            currVoucher['registration_code'] = getRegistrationCode()
            # We already have our activation code!
            # currVoucher['activation_code'] = getActivationCode()
            
            br['supercardnumber'] = str(currVoucher['card_number'])
            br['activationcode'] = str(currVoucher['activation_code'])
            br['securecode'] = str(currVoucher['registration_code'])
            response = br.submit()
            html = response.read()
            # TODO: Remove byte-comparison, change type of variable html to String
            # General errormessage html class: <div class="ap-message ap-message--error ap-message--icon">
            if b'Ihr Karte konnte nicht aktiviert werden' in html:
                # <li>Ihr Karte konnte nicht aktiviert werden. Bitte kontrollieren Sie Ihre Aral SuperCard Nummer.</li>
                print('Karte konnte nicht aktiviert werden')
                continue
            if b'Karte ist bereits aktiv' in html:
                # <li>Karte ist bereits aktiv! <a href="https://www.aral-supercard.de/services/kartenguthaben-abrufen">Hier Ihr Guthaben abfragen!</a></li>
                print('Karte wurde bereits vorher (per Webseite?) aktiviert')
            elif b'Kartenaktivierung erfolgreich' in html:
                # >Kartenaktivierung erfolgreich</h1>
                print('Karte wurde erfolgreich aktiviert')
            else:
                # TODO: Add higher error tolerance
                print('Unbekannter Fehler --> Stoppe')
                break
            
            successfullyActivatedOrdersCounter += 1
            # Update voucher status
            currVoucher['activated'] = True
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

finally:
    # Make sure to always save orders!
    with open(PATH_STORED_VOUCHERS, 'w') as outfile:
        json.dump(orderArray, outfile)
    
    print('Done - druecke ENTER zum Schließen des Fensters')
    # Debug
    # raise
    input()
    sys.exit()
