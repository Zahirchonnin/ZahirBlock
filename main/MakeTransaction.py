from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from main.tools import *
import os
import time

class NewTXN:
    def __init__(self, account):
        self.account = account
        self.private_key = serialization.load_pem_private_key(
            self.account['privateKey'],
            backend=default_backend(),
            password=None
        )
        public_key = self.private_key.public_key()
        self.public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        
        self.randAddr = lambda: '0x' + os.urandom(16).hex()
    
    def makeTNX(self):
        pucket = {}
        _from = self.account['address']

        transaction = {
            "From": _from,
            "PublicKey": self.public_key,
            'To': input("Enter receiver address[Press enter to generate random address]: ") or self.randAddr(),
            'data': input("Enter data to send: "),
            'timeStamp': time.time()
        }
        
        signature = self.private_key.sign(
            dump(transaction),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
                ),
            hashes.SHA256()
            )
        pucket['Transaction'] = transaction
        pucket['Signature'] = signature
        
        self.account['txnCount'] += 1
        
        txn_file_name = f"{_from}-{self.account['txnCount']}-txn.txn"
        try: os.makedirs("Transactions/" + _from)
        except FileExistsError: pass
        with open(f"Transactions/{_from}/{txn_file_name}", 'wb') as txn_file:
            txn_file.write(dump(transaction))
        
        print(f"Transaction writed to: Transactions/{_from}/txn_file_name")
        return dump(pucket)