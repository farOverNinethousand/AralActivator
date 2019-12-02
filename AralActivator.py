'''
Created on 26.11.2019

@author: over_nine_thousand
'''


import os, json, re, sys

# Global variables
INTERNAL_VERSION = '0.0.2'
PATH_STORED_VOUCHERS = os.path.join('vouchers.json')
PATH_INPUT_MAILS = os.path.join('mails.txt')


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
    print('Gib den Registrierungscode ein (4 digits):')
    return userInputDefinedLengthNumber(4)
    # Function END
    
def getSerialNumber():
    print('Gib die Seriennummer ein (10 digits):')
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
    

print('Welcome to AralActivator ' + INTERNAL_VERSION)

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
    print('Crawling email source')
    voucherBalance = 0
    crawledOrderNumbers = re.compile(r'Ihre Aral SuperCard Bestellung\s+(\d+)').findall(emailSource)
    crawledActivationCodes = re.compile(r'Der Aktivierungscode lautet:\s*(\d+)').findall(emailSource)
    print(crawledOrderNumbers)
    print(crawledActivationCodes)
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
                print('Skipping already existing order: ' + orderNumberStr)
                continue
            if voucherBalance == 0:
                voucherBalance = getVoucherBalance()
            #print('Adding ' + orderNumberStr + ':' + activationCodeStr)
            tmpVoucherList = []
            currOrder = {'order_number':orderNumber}
            # TODO: Add valid_until field (+ 3 years from activation date on)
            currVoucher = {'activation_code':activationCode,'activated':False, 'start_balance':voucherBalance, 'current_balance':voucherBalance}
            tmpVoucherList.append(currVoucher)
            currOrder['vouchers'] = tmpVoucherList
            orderArray.append(currOrder)
            numberof_new_vouchers += 1
        print('Found %d new vouchers' % numberof_new_vouchers)
        print('Total value of all new vouchers: %d' % (numberof_new_vouchers * voucherBalance))

if orderArray == None:
    print('Failed to find any vouchers --> Exiting')
    sys.exit()

# TODO: Add functionality
# print('What do you want to do?')
# print('(0) = exit')
# print('(1) = activate cards')
# print('(2) = check remaining balance of existing cards')
# print('(3) = add new cards')

#TODO: Crawl card number hint from website
card_number_hint = None

orderCounter = 0
for currOrder in orderArray:
    print('Arbeite an Bestellung %d / %d' % (orderCounter + 1, len(orderArray)))
    currVoucher = currOrder['vouchers'][0]
    isActivated = currVoucher['activated']
    if isActivated:
        continue
    print('Aktiviere Bestellung: %d' % currOrder['order_number'])
    # TODO: Add errorhandling for typos
    # TODO: Grab card number beginning from website so user has to type in less
    currVoucher['card_number'] = getSupercardNumber(card_number_hint)
    # We do not need this information
    #currVoucher['serial_number'] = getSerialNumber()
    currVoucher['registration_code'] = getRegistrationCode()
    # TODO: Add activation function
    # TODO: Add balance checker function (low priority)
    #currVoucher['activated'] = True
    # TODO: Add possibility to skip current voucher
    print('Aktiviere weitere Karten? 0 = Stop')
    if orderCounter + 1 < len(orderArray) -1:
        user_decision = userInputDefinedLengthNumber(1)
        if user_decision == 0:
            break
    

# Save orders
with open(PATH_STORED_VOUCHERS, 'w') as outfile:
    json.dump(orderArray, outfile)

print('Done')
sys.exit()
