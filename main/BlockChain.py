from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from hashlib import sha256
from main.tools import *
import os
import time

class Block:
    def __init__(self, _from, _to, data, parent_address, parent_hash):
        self.address = '0x' + os.urandom(16).hex()
        self._from = _from
        self._to = _to
        self.data = data
        self.parent_address = parent_address
        self.parent_hash = parent_hash
        self.timeStamp = time.time()

class BLOCKCHAIN:
    def __init__(self):
        with open('BlockChain/chain.chn', 'rb') as f:
            self.chain = eval(f.read().decode())

        self.pending_transaction = []
        self.difficulty = 5

    def newBlock(self, pucket, proof):
        transaction = pucket['Transaction']
        if not self.verfyPoW(transaction, proof):
            return "!PoW invalid"

        if time.time() - transaction['timeStamp'] > 300:
            return "!Expiration"

        public_key_pem = transaction['PublicKey']
        signature = pucket['Signature']
        
        public_key = serialization.load_pem_public_key(
            bytes(public_key_pem),
            backend=default_backend()
            )
        
        try:
            public_key.verify(
                signature,
                dump(transaction),
                padding.PSS(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        
        except :
            return "Invalid siganture!"
        
        parent_address = None
        parent_hash = None
        if self.chain:
            parent_address = self.chain[-1]['address']
            parent_hash = sha256(dump(self.chain[-1])).hexdigest()

        _from = transaction['From']
        _to = transaction['To']
        data = transaction['data']
        block = Block(_from, _to, data, parent_address, parent_hash)
        self.chain.append(block.__dict__)
        with open('BlockChain/chain.chn', 'wb') as f:
            f.write(f'{self.chain}'.encode())
        
        return f"""
        Send: {data}
        From: {_from}
        To: {_to}
        blockIndex: {len(self.chain)}
        blockHash: {sha256(dump(block.__dict__)).hexdigest()}
        blockAddress: {block.address}
        """

    def verfyPoW(self, transaction, proof):
        result = str(transaction) + str(proof)
        result = sha256(result.encode()).hexdigest()
        if result[:self.difficulty] == '0' * self.difficulty:
            return True
        
        else:
            return False