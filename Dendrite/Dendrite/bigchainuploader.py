from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from flask_login import current_user
import pprint
import datetime
import string
import random

BIGCHAIN_IP = 'http://127.0.0.1'

class BigChainUploader:
    def __init__(self):
        self.bigchaindb = BigchainDB(f'{BIGCHAIN_IP}:9984/')
        self.keypairs = generate_keypair()
        self.metadata = []
        self.fulfilled_block_id = None

    def UploadData(self, asset, asset_name, contracts, batch_n):
        self.asset = asset
        self.asset_name = asset_name
        self.contract_files = contracts
        self.batch_number = batch_n

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
        self.fulfilled_block_id = f['id']
        return f


    def get_metadata(self):
        meta = self.metadata
        print(f"METADATA LIST: {self.metadata}")
        metadata = {}
        for data in meta:
            metadata[data['DEPARTMENT']] = [data['METADATA'], data['TIMESTAMP']]
        print(f"X: {metadata}")
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
            return {'Success': True, 'block_id': self.fulfilled_block_id}
        except Exception as e:
            return {'Success': False, 'Exception': e}

    

# Sample of the Created Asset
'''
'data': {
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
                        'CT0005.pdf'],
        'name': 'Tesla Model Y',
        'sender': 'Foxconn',
        'timestamp': datetime.datetime(2019, 1, 9, 18, 43, 9, 491580)
    }

    Foxconn://Tesla Model Y:1
'''