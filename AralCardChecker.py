import csv
import json
import os
import sys
from typing import Union


def loadJson(filepath: str):
    readFile = open(filepath, 'r')
    settingsJson = readFile.read()
    readFile.close()
    return json.loads(settingsJson)


def saveJson(jsonData, filepath):
    with open(filepath, 'w') as outfile:
        json.dump(jsonData, outfile)


def saveAsCSV(jsonData, fileapth):
    with open(fileapth, 'w', newline='') as csvfile:
        fieldnames = ['serial_number', 'activation_code', 'order_number', 'order_date', 'balance', 'voucher_name', 'order_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for order in jsonData:
            if "serial_number" not in order:
                continue
            csvFields = {}
            for fieldname in fieldnames:
                csvFields[fieldname] = order.get(fieldname, "")
            writer.writerow(csvFields)


def findOrderBySerialNumber(allOrders: list, targetSerialNumber: int) -> Union[dict, None]:
    for thisOrder in allOrders:
        if thisOrder.get("serial_number") == targetSerialNumber:
            return thisOrder
    return None

def userInputInt() -> int:
    while True:
        val = input()
        if not val.isdecimal():
            print("Please enter a number")
            continue
        return int(val)


def userInputIntMinMax(minValue, maxValue) -> int:
    while True:
        val = userInputInt()
        if val < minValue:
            print('Value is too small - please enter a value between %d and %d' % (minValue, maxValue))
        elif val > maxValue:
            print('Value is too high - please enter a value between %d and %d' % (minValue, maxValue))
        else:
            return val


allOrders = []
if not os.path.exists("vouchers.json"):
    print("Keine Stammdaten vorhanden -> Tschau")
    sys.exit()
try:
    allOrders = loadJson("vouchers.json")
except:
    print("Fehler beim Laden der Stammdaten -> Tschau")
    sys.exit()

if len(allOrders) == 0:
    print("Stammdaten sind leer -> Kann Eingaben nicht gegenprüfen -> Tschau")
    sys.exit()

""" First convert old data to CSV so user can view it more easily """
print("Umwandlung json -> CSV")
saveAsCSV(allOrders, "vouchers.csv")

print("Warte auf Kartendaten...")
""" Matches pattern of this device: https://www.amazon.de/dp/B00D3D3L8Y
 Device model as text: "Yosoo USB MSR90 Magnet Kartenleser" """
""" 2021-02-28: Attempt dropped because the card reader result us not useful for us... """
# cardScannerPattern = re.compile("(?i)ö\\d+´\\d+_")

""" Collect a list of all order items containing the property "serial_number". """
allOrdersWithSerialNumbers = []
for orderTmp in allOrders:
    serialNumberTmp = orderTmp.get("serial_number")
    if serialNumberTmp is not None:
        allOrdersWithSerialNumbers.append(orderTmp)
if len(allOrdersWithSerialNumbers) == 0:
    print("Keinen Eintrag mit Seriennummer gefunden -> Matching unmöglich -> Tschau")
    sys.exit()
""" Find base, all serial-numbers start with """
serialNumberBase = ''
exampleSerialNumberAsString = str(allOrdersWithSerialNumbers[0]["serial_number"])
for index in range(len(exampleSerialNumberAsString)):
    singleNumberAsString = exampleSerialNumberAsString[index]
    numberIsOnSamePositionForAllCards = True
    for orderTmp in allOrdersWithSerialNumbers:
        if str(orderTmp["serial_number"])[index] != singleNumberAsString:
            numberIsOnSamePositionForAllCards = False
            break
    if numberIsOnSamePositionForAllCards:
        serialNumberBase += singleNumberAsString
    else:
        break
if len(exampleSerialNumberAsString) > 0:
    print("Basis für alle Seriennummern: " + serialNumberBase)
else:
    print("Keine Basis für deine Seriennummern gefunden...")


print("Gib ein, welchen Wert Einträge für nicht matchbare Seriennummern haben sollen:")
balanceForUnmatchedCards = float(userInputIntMinMax(5, 1000))

""" Load savestate if possible """
allFoundSerialNumbers = []
try:
    foundCards = loadJson("found_cards.json")
    print("Fahre fort mit vorigem Stand gescannter Karten - Anzahl bisher: " + str(len(foundCards)))
    for scannedCard in foundCards:
        if "serial_number" in scannedCard:
            allFoundSerialNumbers.append(scannedCard["serial_number"])
except:
    """ No history data available """
    foundCards = []

while True:
    userInput = input("Gib eine Seriennummer ein und drücke ENTER oder gib 'END' zum Beenden ein (max. 10 Stellen): " + serialNumberBase)
    if userInput.isdecimal() and len(serialNumberBase + userInput) == 10:
        userInputSerialNumber = int(serialNumberBase + userInput)
        if userInputSerialNumber in allFoundSerialNumbers:
            print("Seriennummer bereits eingegeben")
            continue
        targetOrder = None
        for orderTmp in allOrdersWithSerialNumbers:
            if orderTmp["serial_number"] == userInputSerialNumber:
                targetOrder = orderTmp
                break
        if targetOrder is not None:
            print("Karte gefunden -> " + str(targetOrder.get('balance', -1)))
            foundCards.append(targetOrder)
        else:
            print("Karte nicht gefunden -> Vermuteter Wert: " + str(balanceForUnmatchedCards))
            foundCards.append({"serial_number": userInputSerialNumber, "balance": balanceForUnmatchedCards})
        """ Save this after every loop to be fail-safe. Don't care about CPU/RAM usage! """
        saveJson(foundCards, "found_cards.json")
        saveAsCSV(foundCards, "found_cards.csv")
        allFoundSerialNumbers.append(userInputSerialNumber)
    elif userInput == 'end':
        print("Beende Script...")
        break
    else:
        print("Ungueltige Eingabe!")

print("Alles erledigt")

