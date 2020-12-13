from wrking_crypto.transaction import Tx
from wrking_crypto.user import User
from wrking_crypto.coin import Input, Output

class ass():

    def __init__(self):
        self.tes = 2

    def __hash__(self):
        return self.tes

    def __dict__(self):
        return {'test':2}

if __name__ == '__main__':
    a = ass()
    print(dict(a))

'''
TO GENERATE A TRANSACTION
isaac = User()
lily = User()

utxos = [Output(isaac.wal, 10), Output(isaac.wal, 20), Output(isaac.wal, 5)]
unlocks = []

for utx in utxos:
    sig = isaac.sign(utx.coin_hash)
    unlock = Input(utx.coin_hash, isaac.puk.export_key('PEM').decode('UTF-8'), sig)
    unlocks.append(unlock)

to = [(lily.wal, 30), (isaac.wal, 2)]
tx = Tx(unlocks, utxos, to)

print(tx.json())'''