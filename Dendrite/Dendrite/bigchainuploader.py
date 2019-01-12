from flask_login import current_user
import pprint
import datetime
import string
import random
from Dendrite import generate_keypair, bdb

class BigChainUploader:
    def __init__(self):
        self.bigchaindb = bdb
        self.metadata = []
        self.fulfilled_block_id = None

    def UploadData(self, asset, asset_name, contracts, batch_n, keys=generate_keypair()):
        self.asset = asset
        self.asset_name = asset_name
        self.contract_files = contracts
        self.batch_number = batch_n
        self.keypairs = keys

    @staticmethod
    def get_sender():
        return current_user.username

    @staticmethod
    def timestamp():
        return datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    def get_contracts(self):
        return self.contract_files

    def get_asset(self):
        return self.asset

    def get_asset_name(self):
        return self.asset_name

    @staticmethod
    def UniqueID():
        return "".join([random.choice(string.digits + string.ascii_lowercase) for i in range(10)] )

    def create_asset_data(self):
        data = {
            'name': self.get_asset_name(),
            'sender': self.get_sender(),
            'Properties': self.get_asset(), 
            'timestamp': self.timestamp(),
            'contracts': self.get_contracts(),
            'BatchID': self.UniqueID(),
            'ItemsPerBatch': self.batch_number
        }
        return data

    def get_asset_data(self):
        data = self.create_asset_data()
        asset = {
            'data': data
        }
        return asset

    def send_transaction(self, fulfilled_block):
        self.bigchaindb.transactions.send_commit(fulfilled_block)

    def fulill_transaction(self, prepared_block):
        f = self.bigchaindb.transactions.fulfill(
            prepared_block,
            private_keys=self.keypairs.private_key
        )
        self.fulfilled_block = f
        self.fulfilled_outputs = f['outputs'][0]
        return f


    def get_metadata(self):
        meta = self.metadata
        metadata = {}
        for data in meta:
            metadata[data['DEPARTMENT']] = [data['METADATA'], data['TIMESTAMP'], data['ROLE']]
        return metadata

    def prepare_genesis_transaction(self):
        return self.bigchaindb.transactions.prepare(
            operation='CREATE',
            signers=self.keypairs.public_key,
            asset=self.get_asset_data(),
            metadata=self.get_metadata()
        )

    def stage_metadata(self, metadata, sender):
        meta = {
            'ROLE': current_user.role,
            'DEPARTMENT': sender,
            'METADATA': metadata,
            'TIMESTAMP': self.timestamp()
        }
        self.metadata.append(meta)

    def CreateGenesisBlock(self):
        try:
            #Send Genesis Block
            self.send_transaction(
                self.fulill_transaction(
                    self.prepare_genesis_transaction()
                )
            )
            return {'Success': True, 'block': self.fulfilled_block, 'output':self.fulfilled_outputs}
        except Exception as e:
            return {'Success': False, 'Exception': e}

    def getTransferInput(self):
        transfer_input = {
            'fulfills': {
                'transaction_id': self.prev_fulfilled_block['id'],
                'output_index': 0
            },
            'owners_before': [self.owner.public_key],
            'fulfillment': self.prev_block_output['condition']['details']
        }
        return transfer_input

    def UploadTransferData(self, prev_fulfilled_block, prev_block_output, owner, recipient):
        self.prev_fulfilled_block = prev_fulfilled_block
        self.prev_block_output = prev_block_output
        self.owner = owner
        self.recipient = recipient

    def TransferBlock(self):
        # Prepare
        prepared_transfer_tx = bdb.transactions.prepare(
            operation='TRANSFER',
            asset={'id': self.prev_fulfilled_block['id']},
            metadata=self.get_metadata(),
            inputs=self.getTransferInput(),
            recipients=self.recipient.public_key
        )
        # Fullfill Transactions
        fulfilled_transfer_tx = bdb.transactions.fulfill(
            prepared_transfer_tx,
            private_keys=self.owner.private_key
        )
        # Change the previous block data to current block to accomodate next block
        self.prev_fulfilled_block = fulfilled_transfer_tx
        self.prev_block_output = fulfilled_transfer_tx['outputs'][0]
        # Send Transaction
        bdb.transactions.send_commit(fulfilled_transfer_tx)
        return {'Success': True, 'block': self.prev_fulfilled_block, 'output':self.prev_block_output}



