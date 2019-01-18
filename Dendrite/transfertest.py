from bigchaindb_driver import BigchainDB  # This imports the BigchainDB which has been running on the system
from bigchaindb_driver.crypto import generate_keypair  # This imports the generate_keypair module which is required for creating private and public kets

bdb_root_url = 'http://35.200.197.117:9984/'
bdb = BigchainDB(bdb_root_url)  # This denotes the fact that we are not using authentication tokens
# Manufacturer = generate_keypair()
# Logistics = generate_keypair()
# Retailer = generate_keypair()
# Customer = generate_keypair()


Manufacturer, Logistics, Retailer = generate_keypair(), generate_keypair(), generate_keypair()
tx = bdb.transactions.prepare(
    operation='CREATE',
    signers=Manufacturer.public_key,
    asset={'data': {'message': 'ABC'}})
signed_tx = bdb.transactions.fulfill(
    tx,
    private_keys=Manufacturer.private_key)
bdb.transactions.send_commit(signed_tx)

# Generates public and private key for Manufacturer and Logistics
'''
Here the asset being transferred is a bicycle which belongs to Manufacturer
The variable below contains a data property which contains the information about the bicycle
'''

bicycle = {
    'data': {
        'bicycle': {
            'serial_number': 'XX2334C',
            'manufacturer': 'bkfab',
        },

    },
}
metadata = {'Country': 'France'}  # Any dictionary can be used as Metadata
prepared_creation_tx = bdb.transactions.prepare(operation='CREATE', signers=Manufacturer.public_key, asset=bicycle,
                                                metadata=metadata)  # This creates a digital asset
fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx,
                                                 private_keys=Manufacturer.private_key)
sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)  # the authorized transaction is now sent over to the BigchainDB

txid = fulfilled_creation_tx['id']  # contains the transaction id
creation_tx = fulfilled_creation_tx  # Manufacturer retrieves the transaction
print("Manufacturer retrieves", creation_tx)

'''
Preparing a transaction
To get inforamtion about the id of the asset we are transferrring
'''
asset_id = creation_tx['id']
transfer_asset = {
    'id': asset_id,
}

'''
Transfer transaction
'''
output_index = 0
output = creation_tx['outputs'][output_index]
transfer_input = {
    'from': "FritoLayFactories",
    'to': "DTDC",
    'fulfillment': output['condition']['details'],
    'fulfills': {
        'output_index': output_index,
        'transaction_id': creation_tx['id'],
    },
    'owners_before': output['public_keys'],
}
prepared_transfer_tx = bdb.transactions.prepare(
    operation='TRANSFER',
    asset=transfer_asset,
    inputs=transfer_input,
    recipients=Logistics.public_key,
)
# Fulfillment of transfer
fulfilled_transfer_tx = bdb.transactions.fulfill(
    prepared_transfer_tx,
    private_keys=Manufacturer.private_key,
)
# send_commit it across the Node
sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)
print("Fulfilled transfer looks like", fulfilled_transfer_tx)
print("Is the Logistics the owner?", sent_transfer_tx['outputs'][0]['public_keys'][0] == Logistics.public_key)
print("Was Manufacturer the previous owner? ", fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == Manufacturer.public_key)
transfer_tx = fulfilled_transfer_tx

'''
Transfer transaction again
'''
asset_id = transfer_tx['asset']['id']
transfer_asset = {
    'id': asset_id,
}
print("Helllooo")
print(transfer_tx['asset']['id'])

output = creation_tx['outputs'][output_index]
transfer_input = {
    'from': "DTDC",
    'to': "FradeepStores",
    'fulfillment': output['condition']['details'],
    'fulfills': {
        'output_index': output_index,
        'transaction_id': transfer_tx['id'],
    },
    'owners_before': [Logistics.public_key]
}

prepared_transfer_tx_again = bdb.transactions.prepare(
    operation='TRANSFER',
    asset=transfer_asset,
    inputs=transfer_input,
    recipients=Retailer.public_key,
)
# Fulfillment of transfer
fulfilled_transfer_tx_again = bdb.transactions.fulfill(
    prepared_transfer_tx_again,
    private_keys=Logistics.private_key,
)
# send_commit it across the Node
sent_transfer_tx_again = bdb.transactions.send_commit(fulfilled_transfer_tx_again)
print("Fulfilled transfer looks like")
print(fulfilled_transfer_tx_again)

print("Is Retailer the owner?", sent_transfer_tx_again['outputs'][0]['public_keys'][0] == Retailer.public_key)
print("Was Logistics the previous owner? ", fulfilled_transfer_tx_again['inputs'][0]['owners_before'][0] == Logistics.public_key)