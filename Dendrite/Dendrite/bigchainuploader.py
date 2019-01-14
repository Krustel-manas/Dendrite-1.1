from flask_login import current_user
import pprint
import datetime
import string
import random
from Dendrite import generate_keypair, bdb
import json

class BigChainUploader:
    def __init__(self):
        self.bigchaindb = bdb
        self.metadata = []
        self.manufacturer = generate_keypair()
        self.logistics = generate_keypair()
        self.retailer = generate_keypair()

    def get_metadata(self):
        meta = self.metadata
        metadata = {}
        for data in meta:
            metadata[data['DEPARTMENT']] = [data['METADATA'], data['TIMESTAMP'], data['ROLE']]
        return metadata

    def stage_metadata(self, metadata, sender):
        meta = {
            'ROLE': current_user.role,
            'DEPARTMENT': sender,
            'METADATA': metadata,
            'TIMESTAMP': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        self.metadata.append(meta)

    def CreateGenesis(self, asset_name, properties, contracts, items_per_batch):
        asset = {
            'data' : {
                'name': asset_name,
                'sender': current_user.username,
                'Properties': properties, 
                'timestamp': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                'contracts': contracts,
                'BatchID': "".join([random.choice(string.digits + string.ascii_lowercase) for i in range(10)]),
                'ItemsPerBatch': items_per_batch
            }
        }
        prepared_creation_tx = bdb.transactions.prepare(
            operation='CREATE',
            signers=self.manufacturer.public_key,
            asset=asset,
            metadata=self.get_metadata()
        )
        fulfilled_creation_tx = bdb.transactions.fulfill(
            prepared_creation_tx,
            private_keys=self.manufacturer.private_key
        )
        sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

        #Saving to Dump File
        with open("blockoutputs.txt", 'w') as f:
            f.write(json.dumps(fulfilled_creation_tx))

        return {'status': True}

    def TransferToLogistics(self):
        #get previous block information
        with open("blockoutputs.txt", 'r') as f:
            x = f.readlines()
            out = x[0]
        out = json.loads(out.replace("'", '"'))

        #Asset to Transfer
        asset_to_transfer = {'id': out['id']}
        #Previous output
        output = out['outputs'][0]
        #Transfer Input
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': 0,
                'transaction_id': out['id'],
            },
            'owners_before': output['public_keys'],
        }
        # Prepare
        prepared_transfer_tx = bdb.transactions.prepare(
            operation='TRANSFER',
            asset=asset_to_transfer,
            inputs=transfer_input,
            recipients=self.logistics.public_key,
            metadata=self.get_metadata()
        )
        # Fulfill
        fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=self.manufacturer.private_key,
        )
        # Send
        sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

        #Append to Dump File
        with open("blockoutputs.txt", "w") as f:
            f.truncate()
            f.write(json.dumps(fulfilled_transfer_tx))

        #Check if Sent
        if(sent_transfer_tx['outputs'][0]['public_keys'][0] == self.logistics.public_key and fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == self.manufacturer.public_key):
            return {'status': True}


    def TransferToRetailer(self):
        #get previous block information
        with open("blockoutputs.txt", 'r') as f:
            x = f.readlines()
            out = x[0]
        out = json.loads(out.replace("'", '"'))

        #Asset to Transfer
        asset_to_transfer = {'id': out['asset']['id']}
        #Previous output
        output = out['outputs'][0]
        #Transfer Input
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': 0,
                'transaction_id': out['id'],
            },
            'owners_before': [self.logistics.public_key],
        }
        # Prepare
        prepared_transfer_tx = bdb.transactions.prepare(
            operation='TRANSFER',
            asset=asset_to_transfer,
            inputs=transfer_input,
            recipients=self.retailer.public_key,
            metadata=self.get_metadata()
        )
        # Fulfill
        fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=self.logistics.private_key,
        )
        # Send
        sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

        #Append to Dump File
        with open("blockoutputs.txt", "w") as f:
            f.truncate()
            f.write(json.dumps(fulfilled_transfer_tx))
        
        #Check if Sent
        if(sent_transfer_tx['outputs'][0]['public_keys'][0] == self.retailer.public_key and fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == self.logistics.public_key):
            return {'status': True}
