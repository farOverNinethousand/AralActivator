'''
Created on 05.12.2019

@author: over_nine_thousand
'''

import re, sys, imaplib


def crawl_mails(settings, orderArray):
#     print('INBOX Status:')
#     print(connection.status('INBOX', '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)'))
    # Select main inbox so we will later only work on this!
    connection = None
    try:
        connection = login_mail(settings)
        # 2019-12-10: Tested with gmail and MS Outlook/Hotmail
        typ, data = connection.select('INBOX', readonly=True)
        if typ != 'OK':
            # E.g. NO = Invalid mailbox (should never happen)
            print("Keine E-Mails gefunden")
            return
        #print(typ, data)
        #num_msgs = int(data[0])
        #print('There are %d messages in INBOX' % num_msgs)
        # Search for specific messages by subject
        typ, [msg_ids] = connection.search(None, '(SUBJECT "Aktivierung Ihrer Aral SuperCard")')
        #print('INBOX', typ, msg_ids)
        if len(msg_ids) == 0:
            print('Es konnten keinerlei ARAL E-Mails gefunden werden')
        # TODO: Sort from newest to oldest
        aral_mails = []
        numberof_new_vouchers = 0
        print('Suche nach Daten in E-Mails ...')
        for msg_id in msg_ids.split():
            #print('Fetching mail with ID %s' % msg_id)
            typ, msg_data = connection.fetch(msg_id, '(BODY.PEEK[TEXT])')
            complete_mail = ''
            for response_part in msg_data:
                #print('Printing response part:')
                if isinstance(response_part, tuple):
                    #print('\n%s:' % msg_id)
                    mail_part = response_part[1].decode('utf-8')
                    #print(mail_part)
                    complete_mail += mail_part
            try:
                order_infoMatchObject = re.compile(r'Ihre Aral SuperCard Bestellung\s*(\d+)\s*vom\s*(\d{2}\.\d{2}\.\d{4})').search(complete_mail)
                orderNumber = int(order_infoMatchObject.group(1))
                orderDate = order_infoMatchObject.group(2)
                activationCode = re.compile(r'Aktivierungscode lautet\s*:\s*(\d+)').search(complete_mail).group(1)
                currOrder = None
                for o in orderArray:
                    if orderNumber == o['order_number']:
                        currOrder = o
                        break
                if currOrder != None and 'activation_code' in currOrder:
                    # Skip already existing objects
                    continue
                if currOrder == None:
                    currOrder = {'order_number':orderNumber}
                currOrder ['activation_code'] = activationCode
                currOrder ['order_date'] = orderDate
                orderArray.append(currOrder)
                numberof_new_vouchers += 1
                print('Bestellnummer: %s, Bestelldatum: %s, Aktivierungscode: %s' % (orderNumber, orderDate, activationCode))
            except:
                print('Fehler: Informationen konnten nicht aus E-Mail geparsed werden')
                raise
            aral_mails.append(complete_mail)
        if numberof_new_vouchers > 0:
            print('%d neue Bestellungen gefunden' % numberof_new_vouchers)
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
    if settings.get('login_email_username', None) == None or settings.get('login_email_password', None) == None or settings.get('login_email_imap', None) == None:
        print('Gib deine E-Mail Zugangsdaten ein')
        print('Gehe sicher, dass die Mails deiner Bestellungen des eingegebenen Aral Accounts an diese E-Mail Adresse verschickt werden!')
        print('Falls du GMail verwendest, leite die Mails auf ein anderes Postfach um und verwende dieses oder erlaubt Zugriff durch weniger sichere Apps: https://myaccount.google.com/lesssecureapps')
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
    
    
    
    rv, mailboxes = connection.list(directory='INBOX')
    return connection