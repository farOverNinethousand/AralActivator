import mechanize, json, os, time, sys

# Returns user input with defined number of digits
def userInputDefinedLengthNumber(numberof_digits):
    while True:
        input_str = input()
        if len(input_str) != numberof_digits:
            print('Eingabe ist groesser oder kleiner als ' + str(numberof_digits) + ' Stellen')
            continue
        if not input_str.isdecimal():
            print('Bitte gib eine ZAHL ein')
            continue
        return int(input_str)

def loadSettings():
    settings = {}
    # Load settings
    try:
        readFile = open(getSettingsPath(), 'r')
        settingsJson = readFile.read()
        settings = json.loads(settingsJson)
        readFile.close
    except:
        # print('Failed to load ' + getSettingsPath())
        pass

    settings.setdefault('login_aral_email', None)
    settings.setdefault('login_aral_password', None)
    settings.setdefault('requires_aral_account', True)
    return settings

def getVersion():
    return '0.6.6'


def getSettingsPath():
    return os.path.join('settings.json')


def getCookiesPath():
    return os.path.join('cookies.txt')


def getBaseDomain():
    return 'https://www.aral-supercard.de'


# Converts html bytes from response object to String
def getHTML(response):
    return response.read().decode('utf-8', 'ignore')


def prepareBrowser():
    # Prepare browser
    br = mechanize.Browser()
    # br.set_all_readonly(False)    # allow everything to be written to
    br.set_handle_robots(False)  # ignore robots
    br.set_handle_refresh(False)  # can sometimes hang without this
    br.set_handle_referer(True)
    br.set_handle_redirect(True)
    br.addheaders = [('User-agent',
                      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36')]
    return br


def getFormIndexBySubmitKey(br, submitKey):
    if submitKey is None:
        return None
    # print('Form debugger:')
    target_index = -1
    current_index = 0
    for form in br.forms():
        # print('Form index ' + str(current_index))
        #         if form.name != None:
        #             print ('Form name = ' + form.name)
        for control in form.controls:
            #             print(control)
            #             print(control.type)
            #             print(control.name)
            #             if control.name != None:
            #                 print('submitKey: ' + control.name)
            if control.name is None:
                continue
            if control.name == submitKey:
                # print('Found form')
                target_index = current_index
                break
        current_index += 1
    return target_index


def getFormIndexByActionContains(br, actionPart):
    if actionPart is None:
        return None
    # print('Form debugger:')
    target_index = -1
    current_index = 0
    for form in br.forms():
        # print('Form index ' + str(current_index))
        if form.action is None:
            continue
        if actionPart in form.action:
            target_index = current_index
            break
        current_index += 1
    return target_index

# Returns object of orderArray where 'order_number' == orderNumber
def findOrderObjectByOrderNumber(orderArray, orderNumber):
    currOrder = None
    for o in orderArray:
        if orderNumber == o['order_number']:
            currOrder = o
            break
    return currOrder

# Returns object of orderArray where 'order_number' == orderNumber
def findOrderObjectIndexByOrderNumber(orderArray, orderNumber):
    currOrder = None
    index = 0
    for o in orderArray:
        if orderNumber == o['order_number']:
            return index
        index += 1
    return -1

def loginAccount(br, settings):
    cookies = mechanize.LWPCookieJar(getCookiesPath())
    if settings.get('login_aral_email', None) is None or settings.get('login_aral_password', None) is None:
        print('Login aral-supercard.de Account')
        print('Erster Start!')
        print(
            'Falls du Karten ueber mehrere Accounts bestellt hast musst du dieses Script jeweils 1x pro Account in verschiedenen Ordnern duplizieren!')
        print(
            'Bedenke, dass auch die jeweiligen E-Mail Konten moeglichst nur die E-Mails enthalten sollten, die auch zu den Bestellungen des eingetragenen Aral Accounts passen ansonsten wird der Aktivierungsprozess unnötig lange dauern und es erscheinen ggf. Fehlermeldungen.')
        print('Achtung: Logge dich NICHT per Browser auf der Aral Webseite ein waehrend dieses Script laeuft!')
        print('Gib deine aral-supercard.de Zugangsdaten ein')
        print('Gib deine E-Mail ein:')
        settings['login_aral_email'] = input()
        print('Gib dein Passwort ein:')
        settings['login_aral_password'] = input()
    elif cookies is not None and os.path.exists(getCookiesPath()):
        # Try to login via stored cookies first - Aral only allows one active session which means we will most likely have to perform a full login
        print('Login aral-supercard.de Account | %s' % settings['login_aral_email'])
        print('Versuche Login ueber zuvor gespeicherte Cookies ...')
        br.set_cookiejar(cookies)
    account_email = settings['login_aral_email']
    account_password = ['login_aral_password']
    response = br.open(getBaseDomain())
    html = getHTML(response)
    logged_in = isLoggedIN(html)
    if not logged_in:
        if cookies is not None and os.path.exists(getCookiesPath()):
            print('Login ueber Cookies fehlgeschlagen --> Versuche vollstaendigen Login')
        else:
            print('Login aral-supercard.de Account | %s' % settings['login_aral_email'])
        response = br.open(getBaseDomain() + '/login')
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
            print(
                'Login fehlgeschlagen - Ungueltige Zugangsdaten? Korrigiere deine eingetragenen Zugangsdaten in der Datei %s bevor du dieses Script wieder startest!' % getSettingsPath())
            logged_in = False
        else:
            print('Vollstaendiger Login erfolgreich')
            logged_in = True
    else:
        print('Login ueber gueltige Cookies erfolgreich')

    if cookies is not None:
        # Save cookies and logindata
        print('Speichere Cookies in ' + getCookiesPath())
        cookies.save()
    else:
        print('Keine Cookies zum Speichern vorhanden')
    with open(getSettingsPath(), 'w') as outfile:
        json.dump(settings, outfile)
    return logged_in


def isLoggedIN(html):
    return 'class=\"login-link logout\"' in html


def printSeparator():
    print('*******************************************************************')

def smoothExit():
    end_wait = 600
    print('Dieses Fenster schliesst sich in %d Sekunden von selbst' % end_wait)
    # Debug
    # raise
    time.sleep(end_wait)
    # input()
    sys.exit()