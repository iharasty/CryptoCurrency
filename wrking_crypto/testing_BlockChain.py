from wrking_crypto.blockchain import BlockChain
from wrking_crypto.user import User
from wrking_crypto.coin import Input,Output
from wrking_crypto.transaction import Tx
from pprint import pprint

if __name__ == '__main__':
    me = User()
    chain = BlockChain(me.wal)
    chain.create_block()
    print('ayy')

    lily = User()

    isaac_wal_b = me.wal
    target_coin = chain.chain[0].transactions[0].sent_coins[0]
    utxos = [Output(target_coin.lock, target_coin.amount)]
    unlocks = []

    for utx in utxos:
        sig = me.sign(utx.coin_hash)
        unlock = Input(utx.coin_hash, me.puk.export_key('PEM'), sig)
        unlocks.append(unlock)

    to = [(lily.wal, 30), (me.wal, 2)]
    tx = Tx(unlocks, utxos, to)

    chain.add_transation(tx)
    chain.create_block()
    print(chain)
    print(chain.is_chain_valid())
    pprint(chain.json())


