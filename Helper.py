import mechanize, json, os

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
        print('Failed to load ' + getSettingsPath())

    settings.setdefault('login_aral_email', None)
    settings.setdefault('login_aral_password', None)
    settings.setdefault('requires_aral_account', True)
    return settings

def getVersion():
    return '0.5.7'


def getSettingsPath():
    return os.path.join('settings.json')


def getCookiesPath():
    return os.path.join('cookies.txt')


def getBaseDomain():
    return 'https://www.aral-supercard.de'


# Converts html bytes from response object to String
def getHTML(response):
    return response.read().decode('utf-8')


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


def loginAccount(br, settings):
    if settings.get('login_aral_email', None) is None or settings.get('login_aral_password', None) is None:
        print('Gib deine aral-supercard.de Zugangsdaten ein')
        print(
            'Falls du ueber mehrere Accounts bestellt hast musst du dieses Script jeweils 1x pro Account in verschiedenen Ordnern duplizieren!')
        print(
            'Bedenke, dass auch die jeweiligen E-Mail Adressen möglichst nur die Mails enthalten sollten, die auch zu den Bestellungen des eingetragenen Aral Accounts passen ansonsten wird der Aktivierungsprozess unnötig lange dauern und es erscheinen ggf. Fehlermeldungen.')
        print('Achtung: Logge dich NICHT per Browser auf der Aral Webseite ein, solange dieses Script laeuft!')
        print('Gib deine E-Mail ein:')
        settings['login_aral_email'] = input()
        print('Gib dein Passwort ein:')
        settings['login_aral_password'] = input()
    else:
        print('Gespeicherte aral-supercard Zugangsdaten wurden erfolgreich geladen')
        # Try to login via stored cookies first - Aral only allows one active session which means we will most likely have to perform a full login
        cookies = mechanize.LWPCookieJar(getCookiesPath())
        if cookies is not None:
            print('Versuche Login ueber zuvor gespeicherte Cookies ...')
            br.set_cookiejar(cookies)
    account_email = settings['login_aral_email']
    account_password = ['login_aral_password']
    response = br.open(getBaseDomain())
    html = getHTML(response)
    logged_in = isLoggedIN(html)
    if not logged_in:
        if cookies is not None:
            print('Login ueber Cookies fehlgeschlagen --> Versuche vollstaendigen Login')
        print('Login Aral Account | %s' % settings['login_aral_email'])
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

    # Save cookies and logindata
    cookies.save()
    with open(getSettingsPath(), 'w') as outfile:
        json.dump(settings, outfile)
    return logged_in


def isLoggedIN(html):
    return 'class=\"login-link logout\"' in html


def printSeparator():
    print('*******************************************************************')
