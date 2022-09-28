import requests
import pprint
# import matplotlib.pyplot as plt
import pickle

dicti = {}
commoncards = []
ascendedcards = []
fiftycards = []
specialcards = []
mocards = []
cards = []
# teamaddresses = ['5YG5F4Y4BTGVSDEAKZTLINX2RRJAIFRBCAYOL5T3VAV2GDDADC4KJ7DDNA', 'ALGMD6LOC2ND6IWCPLYIRO7TC7GAMLLFNK2Y656A4FAJUI47TJ6MI4ZMNU', '47WJDNVMEDLAZFCPLR6IZ6ZXUBL45HBW24PRBRUPNTY27RJKC6WPAM2F5A', 'GLKUYWISCEZ3EJPJMQI6TA74NQBTVSFNKFQNK5PL4I3T6TE7Z236CQ3TFU']
teamaddresses = ['5YG5F4Y4BTGVSDEAKZTLINX2RRJAIFRBCAYOL5T3VAV2GDDADC4KJ7DDNA', 'ALGMD6LOC2ND6IWCPLYIRO7TC7GAMLLFNK2Y656A4FAJUI47TJ6MI4ZMNU']
url = "https://algoindexer.algoexplorerapi.io/v2/accounts/5YG5F4Y4BTGVSDEAKZTLINX2RRJAIFRBCAYOL5T3VAV2GDDADC4KJ7DDNA"
answer = requests.get(url)
print(answer.status_code)
res = answer.json()['account']

createdassets = res['created-assets']

#sorts asset IDs in common, ascended and special
for a in createdassets:
    if a['params']['total'] == 1000 or a['params']['total'] == 500:
        commoncards.append(a['index'])
        cards.append(a['index'])
    if a['params']['total'] == 150:
        ascendedcards.append(a['index'])
        cards.append(a['index'])
    if a['params']['total'] == 30:
        specialcards.append(a['index'])
        cards.append(a['index'])
    if a['params']['total'] == 1:
        mocards.append(a['index'])
        cards.append(a['index'])
    if a['params']['total'] == 50:
        fiftycards.append(a['index'])
        cards.append(a['index'])

#goes through every asset IDs - common, ascended, special, etc.
for asset in cards:
    response = requests.get("https://algoindexer.algoexplorerapi.io/v2/assets/"+str(asset)+"/balances?currency-greater-than=0")
    print(response.status_code)

    balances = response.json()['balances']

    #check the addresses that own the asset and the amount they hold
    for a in balances:
        address = a['address']
        amount = 0
        if asset in commoncards:
            amount = a['amount']*2
        if asset in ascendedcards:
            amount = a['amount']*6
        if asset in specialcards:
            amount = a['amount']*20
        if asset in mocards:
            amount = a['amount']*30
        if asset in fiftycards:
            amount = a['amount']*20
        #add the addresses to dictionary and the points depending on the assets they hold
        if address in dicti:
            points = dicti.get(address)
            points = points + amount
            dicti[address] = points
        elif address in teamaddresses:
            amount = 0
        else:
            dicti[address] = amount
sorteddicti = sorted(dicti.items(), key=lambda x: x[1], reverse=True)

pp = pprint.PrettyPrinter(depth=4)
pp.pprint(sorteddicti)
print(len(sorteddicti))

#write to file to be used by API transactions
#use pickle for convenience of transfering data
with open('staking_algomond.data', 'wb') as filehandle:
    pickle.dump(sorteddicti, filehandle)
filehandle.close()