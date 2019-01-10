from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
from flask_login import current_user
import pprint
import datetime

BIGCHAIN_IP = 'http://34.73.171.107'
bdb = BigchainDB(f'{BIGCHAIN_IP}:9984/')


def CreateAndUploadGenesisBlock(asset, name, quantity, contracts):
    sender = current_user.username
    data = {
        'name': name,
        'sender': sender,
        'Properties': asset, 
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data['contracts'] = contracts
    pprint.pprint(data, compact=True)
    for _ in range(int(quantity)):
        user = generate_keypair()
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
    return True

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
'''