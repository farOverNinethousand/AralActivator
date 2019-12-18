'''
Created on 05.12.2019

@author: over_nine_thousand
'''

import re, sys, imaplib, os, json

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

# According to docs/example: https://pymotw.com/2/imaplib/
def parse_list_response(line):
    line = line.decode('utf-8')
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    mailbox_name = mailbox_name.strip('"')
    return flags, delimiter, mailbox_name

def crawl_mails(settings, orderArray):
    #     print('INBOX Status:')
    #     print(connection.status('INBOX', '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)'))
    # Select main inbox so we will later only work on this!
    connection = None
    try:
        connection = login_mail(settings)
        # 2019-12-10: Tested with gmail and MS Outlook/Hotmail
        typ, data = connection.list()
        if typ != 'OK':
            # E.g. NO = Invalid mailbox (should never happen)
            print("Keine Postfaecher gefunden")
            return
        # print('Anzahl gefundener Postfaecher: %d' % len(data))
        # this maybe used to speed-up the checking process - users can blacklist postboxes through this list
        postbox_ignore = ['Sent']
        for line in data:
            numberof_aral_mails_in_this_mailbox = 0
            flags, delimiter, mailbox_name = parse_list_response(line)
            if mailbox_name in postbox_ignore:
                print('Ueberspringe Postfach: %s' % mailbox_name)
                continue
            print('Durchsuche Postfach %s ...' % mailbox_name)
            typ, data = connection.select(mailbox_name, readonly=True)
            if typ != 'OK':
                # E.g. NO = Invalid mailbox (should never happen)
                print('Fehler: Konnte Postfach %s nicht oeffnen' % mailbox_name)
                return
            # print(typ, data)
            # num_msgs = int(data[0])
            # print('There are %d messages in INBOX' % num_msgs)
            # Search for specific messages by subject
            typ, [msg_ids] = connection.search(None, '(SUBJECT "Aktivierung Ihrer Aral SuperCard")')
            # print('INBOX', typ, msg_ids)
            # print('Anzahl gefundener Aral E-Mails in diesem Postfach: %d' % len(msg_ids))
            aral_mails = []
            numberof_new_vouchers = 0
            print('Sammle Aral E-Mails ...')
            for msg_id in msg_ids.split():
                # print('Fetching mail with ID %s' % msg_id)
                typ, msg_data = connection.fetch(msg_id, '(BODY.PEEK[TEXT])')
                complete_mail = ''
                for response_part in msg_data:
                    # print('Printing response part:')
                    if isinstance(response_part, tuple):
                        # print('\n%s:' % msg_id)
                        mail_part = response_part[1].decode('utf-8')
                        # print(mail_part)
                        complete_mail += mail_part
                aral_mails.append(complete_mail)

        print('Anzahl insgesamt gefundener Aral E-Mails: %d' % len(aral_mails))
        print('Suche nach Daten in E-Mails ...')
        numberof_successfully_parsed_mails = 0
        for aral_mail in aral_mails:
            try:
                order_infoMatchObject = re.compile(r'Ihre Aral SuperCard Bestellung\s*(\d+)\s*vom\s*(\d{2}\.\d{2}\.\d{4})').search(aral_mail)
                orderNumber = int(order_infoMatchObject.group(1))
                orderDate = order_infoMatchObject.group(2)
                activationCode = re.compile(r'Aktivierungscode lautet\s*:\s*(\d+)').search(aral_mail).group(1)
                numberof_successfully_parsed_mails += 1
                currOrder = None
                for o in orderArray:
                    if orderNumber == o['order_number']:
                        currOrder = o
                        break
                if currOrder is not None and 'activation_code' in currOrder:
                    # Skip already existing objects
                    continue
                if currOrder is None:
                    currOrder = {'order_number': orderNumber}
                currOrder['activation_code'] = activationCode
                currOrder['order_date'] = orderDate
                orderArray.append(currOrder)
                numberof_new_vouchers += 1
                print('Neue Bestellung gefunden: Bestellnummer: %s | Bestelldatum: %s | Aktivierungscode: %s' % (orderNumber, orderDate, activationCode))
            except:
                print('Fehler: Informationen konnten nicht aus E-Mail geparsed werden')
                continue
        if numberof_successfully_parsed_mails == 0:
            print('Fehler: Konnte Informationen aus E-Mails nicht extrahieren')
        elif numberof_new_vouchers > 0:
            print('%d neue Bestellungen in E-Mails gefunden' % numberof_new_vouchers)
        else:
            print('Deine E-Mails enthielten keine neuen Bestellungen')
    #     for aral_mail in aral_mails:
    #         print(aral_mail)
    finally:
        try:
            connection.close()
        except:
            pass
        connection.logout()
    return


def login_mail(settings):
    if settings.get('login_email_username', None) is None or settings.get('login_email_password', None) is None or settings.get('login_email_imap', None) is None:
        print('Gib deine E-Mail Zugangsdaten ein')
        print(
            'Gehe sicher, dass die Mails deiner Bestellungen des eingegebenen Aral Accounts an diese E-Mail Adresse verschickt werden!')
        print(
            'Falls du GMail verwendest, leite die Mails auf ein anderes Postfach um und verwende dieses oder erlaubt Zugriff durch weniger sichere Apps: https://myaccount.google.com/lesssecureapps')
        print('Gib deinen E-Mail Postfach Benutzernamen / E-Mail ein:')
        settings['login_email_username'] = input()
        print('Gib dein E-Mail Passwort ein:')
        settings['login_email_password'] = input()
        print('''Gib deine E-Mail IMAP URL ein z.B.'imap-mail.outlook.com' oder 'imap.gmail.com':''')
        settings['login_email_imap'] = input()
    else:
        pass
    #         print('Gespeicherte E-Mail Zugangsdaten wurden erfolgreich geladen')
    #         print('Verwende E-Mail Username: ' + settings['login_email_username'])
    print('Login E-Mail | %s' % settings['login_email_username'])
    connection = imaplib.IMAP4_SSL(settings['login_email_imap'])
    try:
        connection.login(settings['login_email_username'], settings['login_email_password'])
    except imaplib.IMAP4.error:
        print("E-Mail Login fehlgeschlagen!")
        sys.exit(1)

    # rv, mailboxes = connection.list(directory='INBOX')
    return connection


# Testing space
# PATH_STORED_SETTINGS = os.path.join('settings.json')
# readFile = open(PATH_STORED_SETTINGS, 'r')
# settingsJson = readFile.read()
# settings = json.loads(settingsJson)
# readFile.close
# crawl_mails(settings, [])
# sys.exit()