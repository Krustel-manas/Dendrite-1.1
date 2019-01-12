# from bigchaindb_driver import BigchainDB  # This imports the BigchainDB which has been running on the system
# from bigchaindb_driver.crypto import \
#     generate_keypair  # This imports the generate_keypair module which is required for creating private and public kets

# bdb_root_url = 'http://test.bigchaindb.com'
# bdb = BigchainDB(bdb_root_url)  # This denotes the fact that we are not using authentication tokens
# alice = generate_keypair()
# bob = generate_keypair()
# matt = generate_keypair()


# def poll(transaction_id):
#     trials = 0

#     while trials < 100:
#         try:
#             if bdb.transactions.status(transaction_id).get('status') == 'valid':
#                 break
#         except Exception as e:
#             trials += 1
#     print(bdb.transactions.status(transaction_id))


# # Generates public and private key for Alice and Bob
# '''
# Here the asset being transferred is a bicycle which belongs to Alice
# The variable below contains a data property which contains the information about the bicycle
# '''

# bicycle = {
#     'data': {
#         'bicycle': {
#             'serial_number': 'XX2334C',
#             'manufacturer': 'bkfab',
#         },

#     },
# }
# metadata = {'Country': 'France'}  # Any dictionary can be used as Metadata
# prepared_creation_tx = bdb.transactions.prepare(operation='CREATE', signers=alice.public_key, asset=bicycle,
#                                                 metadata=metadata)  # This creates a digital asset
# fulfilled_creation_tx = bdb.transactions.fulfill(prepared_creation_tx,
#                                                  private_keys=alice.private_key)
# sent_creation_tx = bdb.transactions.send(
#     fulfilled_creation_tx)  # the authorized transaction is now sent over to the BigchainDB
# txid = fulfilled_creation_tx['id']  # contains the transaction id
# poll(txid)
# creation_tx = fulfilled_creation_tx  # Alice retrieves the transaction
# print("Alice retrieves", creation_tx)

# '''
# Preparing a transaction
# To get inforamtion about the id of the asset we are transferrring
# '''
# asset_id = creation_tx['id']
# transfer_asset = {
#     'id': asset_id,
# }

# '''
# Transfer transaction
# '''
# output_index = 0
# output = creation_tx['outputs'][output_index]
# transfer_input = {
#     'fulfillment': output['condition']['details'],
#     'fulfills': {
#         'output_index': output_index,
#         'transaction_id': creation_tx['id'],
#     },
#     'owners_before': output['public_keys'],
# }
# prepared_transfer_tx = bdb.transactions.prepare(
#     operation='TRANSFER',
#     asset=transfer_asset,
#     inputs=transfer_input,
#     recipients=bob.public_key,
# )
# # Fulfillment of transfer
# fulfilled_transfer_tx = bdb.transactions.fulfill(
#     prepared_transfer_tx,
#     private_keys=alice.private_key,
# )
# # Send it across the Node
# sent_transfer_tx = bdb.transactions.send(fulfilled_transfer_tx)
# poll(sent_transfer_tx['id'])
# print("Fulfilled transfer looks like", fulfilled_transfer_tx)
# print("Is the bob the owner?", sent_transfer_tx['outputs'][0]['public_keys'][0] == bob.public_key)
# print("Was Alice the previous owner? ", fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == alice.public_key)
# transfer_tx = fulfilled_transfer_tx

# '''
# Transfer transaction again
# '''
# asset_id = transfer_tx['asset']['id']
# transfer_asset = {
#     'id': asset_id,
# }
# print("Helllooo")
# print(transfer_tx['asset']['id'])

# output = creation_tx['outputs'][output_index]
# transfer_input = {
#     'fulfillment': output['condition']['details'],
#     'fulfills': {
#         'output_index': output_index,
#         'transaction_id': transfer_tx['id'],
#     },
#     'owners_before': [bob.public_key]
# }

# prepared_transfer_tx_again = bdb.transactions.prepare(
#     operation='TRANSFER',
#     asset=transfer_asset,
#     inputs=transfer_input,
#     recipients=matt.public_key,
# )
# # Fulfillment of transfer
# fulfilled_transfer_tx_again = bdb.transactions.fulfill(
#     prepared_transfer_tx_again,
#     private_keys=bob.private_key,
# )
# # Send it across the Node
# sent_transfer_tx_again = bdb.transactions.send(fulfilled_transfer_tx_again)
# poll(sent_transfer_tx_again['id'])
# print("Fulfilled transfer looks like")
# print(fulfilled_transfer_tx_again)

# print("Is Matt the owner?", sent_transfer_tx_again['outputs'][0]['public_keys'][0] == matt.public_key)
# print("Wa


from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import pprint
import time
import random
import string
import datetime

BIGCHAIN_IP = 'http://127.0.0.1'
bdb = BigchainDB(f'https://test.bigchaindb.com/')

data = {
    'Properties': {
        'Accent_Color': 'Gun Metal',
        'Battery-Capacity': '500KWh',
        'Body-Color': 'Space Grey',
        'Drive-Configuration': '4 Wheel Electric Drive ',
        'Gross-Vehicle-Weight-Rating': '2700 pounds',
        'Model-Name': 'P500Q',
        'Tire_Diameter': '21 Inches'
    },
    'contracts': ['CT0001.pdf', 'CT0002.pdf', 'CT0003.pdf', 'CT0004.pdf',
                    'CT0005.pdf', 'CT0001.pdf', 'CT0002.pdf', 'CT0003.pdf', 'CT0004.pdf',
                    'CT0005.pdf', 'CT0001.pdf', 'CT0002.pdf', 'CT0003.pdf', 'CT0004.pdf',
                    'CT0005.pdf', 'CT0001.pdf', 'CT0002.pdf', 'CT0003.pdf', 'CT0004.pdf',
                    'CT0005.pdf'],
    'name': 'Tesla Model A',
    'sender': 'Foxconn',
    'timestamp': datetime.datetime.now().strftime('%d-%m-%Y')
}

user = generate_keypair()
start = time.time()
for i in range(1000):
    data['AssetProductID'] = "".join( [random.choice(string.digits + string.ascii_lowercase) for i in range(10)] )
    bdb.transactions.send_commit(
        bdb.transactions.fulfill(
            bdb.transactions.prepare(
                operation = 'CREATE',
                signers = user.public_key,
                asset = {
                    'data': data
                }
            ),
            private_keys=user.private_key
        )
    )
    print(i)
print(f'Time per asset: {(time.time() - start)/9}s')