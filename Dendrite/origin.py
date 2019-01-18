from Dendrite import db
from Dendrite.models import User
from bigchaindb_driver import BigchainDB
import pprint
from pymongo import MongoClient
import random
import string

BIGCHAIN_IP = 'http://127.0.0.1'
bdb = BigchainDB(f'{BIGCHAIN_IP}:9984/')

client = MongoClient('localhost', 27017)
bigchain_database = client['bigchain']
asset_db = bigchain_database['assets']
tx_db = bigchain_database['transactions']
meta_db = bigchain_database['metadata']

def get_prev_owners():
    try:
        public_key_list = []
        found_keys = []
        users_keypairs = [{"key": x.keypair.public_key, "username": x.username, "role":x.role} for x in User.query.all()]
        transactions = [x for x in tx_db.find()]
        for i in transactions:
            kvp = {"public_key": [y['public_keys'] for y in i.get('outputs')][0][0], "owners_before": [ y['owners_before'] for y in i.get('inputs')][0][0]}
            found_keys.append(kvp)
        
        owners = []
        for i in range(len(found_keys)):
            for j in range(len(users_keypairs)):
                if(found_keys[i].get('public_key') == users_keypairs[j].get('key')):
                    owners.append({"username": users_keypairs[j].get('username'), "role": users_keypairs[j].get('role')})
    except Exception as e:
        print("Exception Occured", e)
        return {'status': 500, 'exception': e}
    return {'status': 200, 'returns': owners}

def get_all_metadata():
    try:
        metadata = [x.get('metadata') for x in meta_db.find()][-1]
        metadata_list = []
        for x in metadata:
            key = x
            meta = metadata.get(key)
            desc = meta[0]
            timestamp = meta[1]
            role = meta[2]
            metadata_list.append({"stage":key, "data": {"description":desc, "timestamp":timestamp, "role":role}})
    except Exception as e:
        print("Exception occured", e)
        return {'status': 500, 'exception': e}
    return {'status': 200, 'returns': metadata_list}
    

def get_asset(batch_id):
    #6sj2fpsa4e BATCH ID
    try:
        asset = [x for x in asset_db.find({"data.BatchID":batch_id})]
        if(len(asset) > 0):
            asset = asset[-1]
        else:
            return {'status': 404}
    except Exception as e:
        print("Exception Occured", e)
        return {'status': 500, 'exception': e}
    return {'status': 200, 'returns': asset.get('data')}
    
def start(batch_id):
    try:
        rx = get_asset(batch_id)
        if(rx.get('status') == 200):
            pprint.pprint(rx)
            print("\n")
            pprint.pprint(get_all_metadata())
            print("\n")
            pprint.pprint(get_prev_owners())
            return {'status':200}
        else:
            return {'status': 404, 'error': "This Batch ID is invalid"}
    except Exception as e:
        return {'status': 500, 'exception': e}

def generate_dendrite_id(batch_number):
    id_store = []
    for i in range(batch_number):
        batch_id = "".join([random.choice(string.digits + string.ascii_lowercase) for i in range(8)])
        id_store.append(f'DX-{batch_id}-C')
    pprint.pprint(id_store)

#print(start("6sj2fpsa4e"))
generate_dendrite_id(25)

