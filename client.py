from threading import Thread
from main.newAccount import AccountMaker
from main.MakeTransaction import NewTXN
from main.tools import *
import os
import time
import asyncio

class SendTransactionClient(asyncio.Protocol):
    def __init__(self):
        try: os.makedirs('Accounts')
        except FileExistsError: pass
        try: os.makedirs('Transactions')
        except FileExistsError: pass
        self._1 = 0

    def connection_made(self, transport):
        self.transport = transport
        self.options()
        t = Thread(target=self._options)
        t.start()

    
    def data_received(self, data):
        pucket = load(data)
        response = {}

        if time.time() - pucket['timeStamp'] > 20:
            response['TYPE'] = 'ERROR'
            response['MESSAGE'] = "Time stamp Expired!"
            response['timeStamp'] = time.time()
            self.transport.write(dump(response))
        
        elif pucket['TYPE'] == 'ERROR':
            print(f"ERROR MESSAGE: {pucket['MESSAGE']}")
        
        elif pucket['TYPE'] == 'PANDING':
            
            print(pucket['MESSAGE'])
        
        elif pucket['TYPE'] == 'RESULT':
            print(pucket['MESSAGE'])
            
        elif pucket['TYPE'] == 'DATA':
            print(pucket['MESSAGE'])
        
        
    def options(self):
        print("* Options:")
        print("\t*[1] New transaction.")
        print("\t*[2] Get data.")
        print("\t*[0] Close.")
        do = input("\t[0-2]--> ")
        if do == '1':
            self.newTxn()
            response = {
            "TYPE": "POST",
            'pucket': self._pucket,
            'timeStamp': time.time()
            }
            self.transport.write(dump(response))
        
        elif do == '2':
            response = {
                "TYPE": "GET /",
                'timeStamp': time.time()
            }
            self.transport.write(dump(response))

        elif do == '0':
            self.transport.close()
            quit()

    def newTxn(self):
        do = input("Use same account?\t\n[y/n]--> ") if self._1 else 'n'
        if do.lower() in ('no', 'n'):
            self._1 = 1

            if os.listdir('./Accounts'):
                print("Available accounts: ")
                for index, account in enumerate(os.listdir('./Accounts')):
                    print(f'\t*[{index}] {account}.')
                print(f"\t*[{index+1}] Generate new account.")
                
                while True:
                    try:
                        account = int(input(f'\t[0-{index+1}]--> '))
                        assert account > 0, ValueError
                        break
                    except (ValueError, AssertionError):
                        print("Enter a number (>=0).")

                account_path = self.genAccount() if account > index else f'Accounts/{os.listdir("./Accounts")[index]}'


            else:
                print("No Accounts found!")
                do = input("Generate new account??\n\t[y/n]--> ")
                if do.lower() in ('yes', 'y'):
                    account_path = self.genAccount()
                    print(f"Account at: {account_path}")

                else:
                    self._1 = 0
                    return self.options()

            with open(account_path, 'rb') as f:
                account = load(f.read())
        
            try:
                self.txn_manager.account = account
            except AttributeError:
                self.txn_manager = NewTXN(account)

        self._pucket = self.txn_manager.makeTNX()

        with open(account_path, 'wb') as f:
            f.write(dump(self.txn_manager.account))
        
    def genAccount(self):
        acc_manager = AccountMaker()
        account_path = f'Accounts/{acc_manager.genAccount()}'
        print(f"Address of new account: {acc_manager.address}")
        return account_path
    
    def _options(self):
        self.options()
        return self._options()



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(
        lambda: SendTransactionClient(), '127.0.0.1', 8888
        )
    
    
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()