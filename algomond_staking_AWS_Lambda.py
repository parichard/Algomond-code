import json
import requests
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction

def lambda_handler(event, context):
    dicti = {}
    commoncards = []
    ascendedcards = []
    fiftycards = []
    specialcards = []
    mocards = []
    cards = []
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
    
    ## now we have a list of sorted wallets and their elligible towards MOND reward.
    ## next we filter the wallets so we only keep those that have opted into MOND, 
    ## so we don't pointlessly try to send them MOND later on.
    
    optedInMondWallets = [] #all wallets that have MOND opted in
    balances = requests.get("https://algoindexer.algoexplorerapi.io/v2/assets/871370770/balances")
    bal = balances.json()['balances']
    for entry in bal:
        optedInMondWallets.append(entry['address'])
    
    ## now we send the transactions
    # Function from Algorand Inc.
    def wait_for_confirmation(client, txid):
        last_round = client.status().get('last-round')
        txinfo = client.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            print('Waiting for confirmation')
            last_round += 1
            client.status_after_block(last_round)
            txinfo = client.pending_transaction_info(txid)
        print('Transaction confirmed in round', txinfo.get('confirmed-round'))
        return txinfo
    
    algod_address = 'https://node.algoexplorerapi.io'
    
    # Initalize throw-away account for this example - check that is has funds before running script
    mnemonic_phrase = 'insert mnemonic here'
    account_private_key = mnemonic.to_private_key(mnemonic_phrase)
    account_public_key = mnemonic.to_public_key(mnemonic_phrase)
    
    algodclient = algod.AlgodClient('', algod_address, '')
    
    for entry in sorteddicti:
        
        if entry[0] in optedInMondWallets:
            print("wallet: " + entry[0] + ", MOND to send: " + str(entry[1]))
            # get suggested parameters from Algod
            params = algodclient.suggested_params()
        
            gh = params.gh
            first_valid_round = params.first
            last_valid_round = params.last
            fee = params.min_fee
            #adjust the send amount value here
            send_amount = entry[1]
            index = 871370770 #MOND asset ID
        
            existing_account = account_public_key
            send_to_address = entry[0]
            # send_to_address = "MONDWLP4BRKVWPOWL6FJWUMHRL65UJ4CS7S4JFXFI3K7SY7233ZO3A5P7I"
        
            # Create and sign transaction
            tx = transaction.AssetTransferTxn(existing_account, fee, first_valid_round, last_valid_round, gh, send_to_address,
                                    send_amount, index, flat_fee=True)
            signed_tx = tx.sign(account_private_key)
        
            try:
                tx_confirm = algodclient.send_transaction(signed_tx)
                print('Transaction sent with ID', signed_tx.transaction.get_txid())
                # wait_for_confirmation(algodclient, txid=signed_tx.transaction.get_txid())
            except Exception as e:
                print(e)
    
    return {
        'statusCode': 200,
        'body': json.dumps(sorteddicti)
    }


# TO ADD PYTHON PACKAGE TO LAMBDA IN WINDOWS TERMINAL (requests and py-algorand-sdk):
# docker pull lambci/lambda
# docker run -v ${pwd}:/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install -r requirements.txt -t python/lib/python3.8/site-packages/; exit"
# powershell Compress-Archive python staking.zip