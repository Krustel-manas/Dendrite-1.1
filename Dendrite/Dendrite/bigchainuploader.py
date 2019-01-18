from flask_login import current_user
from Dendrite import generate_keypair, bdb, db, json, datetime, string, random
from Dendrite.models import TransferRecord
from Dendrite.models import User

class BigChainUploader:
    def __init__(self):
        self.metadata = []

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
        keypair = current_user.keypair
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
            signers=keypair.public_key,
            asset=asset,
            metadata=self.get_metadata()
        )
        fulfilled_creation_tx = bdb.transactions.fulfill(
            prepared_creation_tx,
            private_keys=keypair.private_key
        )
        sent_creation_tx = bdb.transactions.send_commit(fulfilled_creation_tx)

        #Saving to Dump File
        with open("blockoutputs.txt", 'w') as f:
            f.truncate()
            f.write(json.dumps(fulfilled_creation_tx))

        return {'status': True}

    def TransferToLogistics(self):
        #Get Keypair
        manufacturer_keys = User.query.filter_by(username=TransferRecord.query.filter_by(to_user=current_user.username).first().from_user).first().keypair
        logistics_keys = current_user.keypair
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
            'from': TransferRecord.query.filter_by(to_user=current_user.username).first().from_user,
            'to': current_user.username,
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
            recipients=logistics_keys.public_key,
            metadata=self.get_metadata()
        )
        # Fulfill
        fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=manufacturer_keys.private_key,
        )
        # Send
        sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

        #Append to Dump File
        with open("blockoutputs.txt", "w") as f:
            f.truncate()
            f.write(json.dumps(fulfilled_transfer_tx))

        #Check if Sent
        if(sent_transfer_tx['outputs'][0]['public_keys'][0] == logistics_keys.public_key and fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == manufacturer_keys.public_key):
            return {'status': True}


    def TransferToRetailer(self):
        #Get Keypair
        logistics_keys = User.query.filter_by(username=TransferRecord.query.filter_by(to_user=current_user.username).first().from_user).first().keypair
        retailer_keys = current_user.keypair

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
            'from': TransferRecord.query.filter_by(to_user=current_user.username).first().from_user,
            'to': current_user.username,
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': 0,
                'transaction_id': out['id'],
            },
            'owners_before': [logistics_keys.public_key],
        }
        # Prepare
        prepared_transfer_tx = bdb.transactions.prepare(
            operation='TRANSFER',
            asset=asset_to_transfer,
            inputs=transfer_input,
            recipients=retailer_keys.public_key,
            metadata=self.get_metadata()
        )
        # Fulfill
        fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=logistics_keys.private_key,
        )
        # Send
        sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

        #Append to Dump File
        with open("blockoutputs.txt", "w") as f:
            f.truncate()
            f.write(json.dumps(fulfilled_transfer_tx))

        print(fulfilled_transfer_tx['id'])
        #Check if Sent
        if(sent_transfer_tx['outputs'][0]['public_keys'][0] == retailer_keys.public_key and fulfilled_transfer_tx['inputs'][0]['owners_before'][0] == logistics_keys.public_key):
            return {'status': True}
