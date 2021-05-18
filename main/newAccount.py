from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from main.tools import dump
import os

class AccountMaker:
    def __init__(self):
        self.address = '0x' + os.urandom(16).hex()
        self.txnCount = 0
        self.balance = 0
        self.privateKey = self.genPrivKey()
    
    def genPrivKey(self):
        privateKey = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        privateKey = privateKey.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            )
        
        return privateKey
    
    def accountData(self):
        return dump(self.__dict__)
        
    def genAccount(self):
        accountName = self.address + '-account.act'
        with open('Accounts/' + accountName, 'wb') as f:
            f.write(self.accountData())
        
        return accountName
if __name__ == '__main__':
    manager = AccountMaker()
    accountName = manager.genAccount()
    
    print(f"Account data at: Accounts/{accountName}")