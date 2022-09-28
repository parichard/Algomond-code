# 1.4.0 update to add flat-fee=True to avoid bug in the SDK
# In 1.4.0 it is no longer necessary to declare the content type of the send_transaction
# headers={'content-type': 'application/x-binary'}

import pickle
from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction


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
mnemonic_phrase = '' #insert mnemonic here
account_private_key = mnemonic.to_private_key(mnemonic_phrase)
account_public_key = mnemonic.to_public_key(mnemonic_phrase)

algodclient = algod.AlgodClient('', algod_address, '')

with open('./staking_algomond.data', 'rb') as filehandle:
    sorteddicti = pickle.load(filehandle)
filehandle.close()

for entry in sorteddicti:
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

    # Create and sign transaction
    tx = transaction.AssetTransferTxn(existing_account, fee, first_valid_round, last_valid_round, gh, send_to_address,
                            send_amount, index, flat_fee=True)
    signed_tx = tx.sign(account_private_key)

    try:
        tx_confirm = algodclient.send_transaction(signed_tx)
        print('Transaction sent with ID', signed_tx.transaction.get_txid())
        wait_for_confirmation(algodclient, txid=signed_tx.transaction.get_txid())
    except Exception as e:
        print(e)