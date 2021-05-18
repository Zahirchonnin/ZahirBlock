from threading import Thread
from main.tools import *
from main.BlockChain import BLOCKCHAIN
from hashlib import sha256
import asyncio
import time


class BlockChainServer(asyncio.Protocol):
    def __init__(self):
        self.blockchain = BLOCKCHAIN()

    def connection_made(self, transport):
        self.transport = transport
    
    def data_received(self, data):
        print("data received")
        pucket = load(data)
        response = {}

        if time.time() - pucket['timeStamp'] > 20:
            response['TYPE'] = 'ERROR'
            response['MESSAGE'] = "pucket too old."
            response['timeStamp'] = time.time()
            self.transport.write(dump(response))
        
        elif pucket['TYPE'] == 'ERROR':
            print(f"ERROR MESSAGE: {pucket['MESSAGE']}")

        elif pucket['TYPE'] == 'POST':
            print("Transaction recevied.")
            _pucket = load(pucket['pucket'])
            response['TYPE'] = 'PANDING'
            response['MESSAGE'] = "Working on transaction..."
            response['timeStamp'] = time.time()
            self.blockchain.pending_transaction.append(_pucket['Transaction'])
            t = Thread(target=self.mining, args=(_pucket, len(self.blockchain.pending_transaction) - 1))
            t.start()
            self.transport.write(dump(response))
        
        elif pucket['TYPE'] == 'GET /':
            print("Sending chain data...")
            response['TYPE'] = 'DATA'
            response['MESSAGE'] = pprint(self.blockchain.chain)
            response['timeStamp'] = time.time()
            self.transport.write(dump(response))
        
        elif pucket['TYPE'] == 'close':
            print("Closing connection...")
            self.transport.close()
    
    def mining(self, pucket, index):
        print(f"Start mining...\n difficulty: {self.blockchain.difficulty}")
        hashed_txn = str(pucket['Transaction'])
        for nonce in range(2**32):
            new_hash = hashed_txn + str(nonce)
            new_hash = sha256(new_hash.encode()).hexdigest()
            if new_hash[:self.blockchain.difficulty] == '0' * self.blockchain.difficulty:
                print(f"Proof found: {nonce}")
                print(f"Hash result: {new_hash}")
                response = {
                    "TYPE": "RESULT",
                    "MESSAGE": self.blockchain.newBlock(pucket, nonce),
                    'timeStamp': time.time()
                }

                try:
                    del self.blockchain.pending_transaction[index]
                except IndexError:
                    pass
                
                return self.transport.write(dump(response))

def pprint(chain):
    content = ''
    for index, block in enumerate(chain):
        if block['parent_address']:
            parnet_address = block['parent_address']
        
        else:
            parnet_address = "ROOT"
        
        content += f"""
    --------Address: {block['address']}--------
        * Data: {block['data']}
        * Parent address: {parnet_address}
        * Parent hash: {block['parent_hash']}
        * Block index: {index + 1}
        """
    
    return content


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(
        lambda: BlockChainServer(),
        '127.0.0.1', 8888
        )
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()