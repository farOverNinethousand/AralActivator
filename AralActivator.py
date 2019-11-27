'''
Created on 26.11.2019

@author: over_nine_thousand
'''


import os, json, re, sys

# Global variables
INTERNAL_VERSION = '0.0.1'
PATH_STORED_VOUCHERS = os.path.join('vouchers.json')
PATH_INPUT_MAILS = os.path.join('mails.txt')


def userInputDefinedLengthNumber(exact_length):
    while True:
        input_str = input()
        print('Input = ' + input_str)
        if len(input_str) != exact_length:
            print('Code is more or less than ' + str(exact_length) + ' digits')
            continue
        if not input_str.isdecimal():
            print('Please enter a NUMBER')
            continue
        break
    # Function END
    
def userInputNumber():
    while True:
        input_str = input()
        try:
            input_int = int(input_str)
            return input_int
        except:
            print('Please enter a NUMBER')
            continue
    # Function END

def getRegistrationCode():
    print('Enter registration code (4 digits):')
    return userInputDefinedLengthNumber(4)
    # Function END
    
def getSerialNumber():
    print('Enter serial number (10 digits):')
    return userInputDefinedLengthNumber(10)
    # Function END
    
def getSupercardNumber():
    # According to their website, their card numbers are really 19 digits lol
    print('Enter supercard number (19 digits):')
    return userInputDefinedLengthNumber(19)
    # Function END
    
def getActivationCode():
    # TODO: Length of 19 is probably wrong!
    print('Enter activation code (10 digits):')
    return userInputDefinedLengthNumber(10)
    # Function END

def getVoucherBalance():
    print('Enter amount (all cards you add should have the same balance in Euro):')
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

for currOrder in orderArray:
    currVoucher = currOrder['vouchers'][0]
    isActivated = currVoucher['activated']
    if isActivated:
        continue
    print('Activate order: %d' % currOrder['order_number'])
    currVoucher['card_number'] = getSupercardNumber()
    # We do not need this information
    #currVoucher['serial_number'] = getSerialNumber()
    currVoucher['registration_code'] = getRegistrationCode()
    # TODO: Add activation function
    # TODO: Add balance checker function (low priority)
    #currVoucher['activated'] = True
    # Simple 'UI'
    # TODO: Only ask if we're not already working on the last element
    print('Activate more? 0 = Stop')
    user_decision = userInputDefinedLengthNumber(1)
    # TODO: Fix this
    if user_decision == 0 or True:
        break
    

# Save orders
with open(PATH_STORED_VOUCHERS, 'w') as outfile:
    json.dump(orderArray, outfile)

print('Done')
sys.exit()
