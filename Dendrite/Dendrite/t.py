import threading
from queue import Queue
import time
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import datetime
import random
import string
import multiprocessing

start = time.time()

BIGCHAIN_IP = 'http://127.0.0.1'
bdb = BigchainDB(f'{BIGCHAIN_IP}:9984/')

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
    'name': 'Tesla XYZ',
    'sender': 'Foxconn',
    'timestamp': datetime.datetime.now().strftime('%d-%m-%Y')
}

user = generate_keypair()

# print_lock = threading.Lock()

# def exampleJob(worker):
#     rnd = "".join( [random.choice(string.digits + string.ascii_lowercase) for i in range(10)] )
#     data['AssetProductID'] = rnd
#     bdb.transactions.send_commit(
#         bdb.transactions.fulfill(
#             bdb.transactions.prepare(
#                 operation = 'CREATE',
#                 signers = user.public_key,
#                 asset = {
#                     'data': data
#                 }
#             ),
#             private_keys=user.private_key
#         )
#     )
#     time.sleep(0.2)
#     with print_lock:
#         print(f'{threading.current_thread().name} WORKER: {worker}')

# def threader():
#     while True:
#         worker = q.get()
#         exampleJob(worker)
#         q.task_done()

# q = Queue()

# # Number of Workers
# for x in range(20):
#     t = threading.Thread(target=threader)
#     t.daemon = True
#     t.start()

# start = time.time()

# #Number of Times Target Function should run
# for worker in range(40):
#     q.put(worker)

# q.join()

# print(f"Entire Job took {time.time() - start}s")
 

import threading

start = time.time()

def send_10():
    for i in range(10):
        rnd = "".join( [random.choice(string.digits + string.ascii_lowercase) for i in range(10)] )
        data['AssetProductID'] = rnd
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
        print(f"Sent Transcation {i} SEND_10")

def send_20():
    for i in range(20):
        rnd = "".join( [random.choice(string.digits + string.ascii_lowercase) for i in range(10)] )
        data['AssetProductID'] = rnd
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
        print(f"Sent Transcation {i}: SEND_20")

p1 = threading.Thread(target=send_10)
p2 = threading.Thread(target=send_20)

p1.start()
p2.start()

p1.join()
p2.join()

end = time.time()

print(f"Finished In {end-start}s.")