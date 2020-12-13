'''
Created by: Isaac Harasty

Primary Purpose: Contains the BLOCK and BLOCKCHAIN
classes for keep a list of all blocks

As of 12/12/20, This block chain is working fairly well on its own.
It is capable of generating transactions, only adding them if they're
valid and point to a UTXO currently in the block chain.
'''

import datetime
from Crypto.Hash import SHA256
import requests
from urllib.parse import urlparse
from wrking_crypto.transaction import Tx

'''
GLOBAL VARIABLES NEEDED IN THE CLASS:

glob_chain: List of Blocks
    This is actually the block chain
    
DIFFICULTY: int
    represents the current difficulty, aka amount of leading zeros
    in a sucsesfully hashed block
    
our_wallet: String (Wallet)
    Represents the string value of the wallet of this node. Needed
    for knowing who to award the new coins/fees to.
'''
glob_chain = []
our_wallet = None
DIFFICULTY = 1

class BlockChain:
    '''
    Represents a List of Blocks cryptographically Linked together

    Attributes:
    ---------------
    memlist: Memlist Object
        A list representing the unmined/pending transactions. Become
        a part of the block chain once create_block() is called.

    chain: List
        A local representation of the global varible, the block chain

    nodes: Set
        A set containing all other node's IP's / Ports to communicate with
    '''

    def __init__(self, wallet):

        global glob_chain
        global our_wallet

        our_wallet = wallet
        self.memlist = MemList()
        self.chain = glob_chain
        self.nodes = set()

    def create_block(self):
        '''
        Primary function of the BlockChain class, mines a new block
        based on the top paying transactions in the MemList.

        Also calls the Block.find_nonce() function to get a correct Nonce

        If the block chain is empty, create the genesis block

        :return: the block that will be added onto the chain after calling.
        '''

        if len(self.chain) == 0:

            init_trans = self.memlist.get_tx_to_mine()
            block = Block(0, '0', init_trans)
            block.find_nonce()

        else:

            init_trans = self.memlist.get_tx_to_mine()
            block = Block(len(self.chain) + 1,
                          self.get_prev_block().hash(),
                          init_trans)
            block.find_nonce()


        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def is_chain_valid(self):
        '''
        Checks to make sure this Block Chain is cryptographically valid,

            1) Each blocks previous hash correlates to that previous blocks hash
            2) Each block is hashed correctly, and has the correct amount of leading 0's

        :return True if passes
        :return False if doesn't
        '''
        previous_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block.previous_hash != previous_block.hash():
                return False

            if block.hash()[:DIFFICULTY] !=  ( '0' * DIFFICULTY ):
                return False

            previous_block = block
            block_index += 1
        return True

    def add_transation(self, tx):
        '''
        Passes the new transaction object to the memlist class.

        :return the value returned by memlist.add_tx()
        '''
        return self.memlist.add_tx(tx)

    def add_node(self, address):
        '''
        Inputs the passed address into this block chains list
        of other nodes of the network

        :param address: A full address (i.e. http://127.0.0.0:8000 )
        '''

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):

        #TODO CHECK IF THIS STILL WORKS
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def __str__(self):

        str_chain = []
        for b in self.chain:
            str_chain.append(str(b))
        return 'Nodes %s\nChain: %s\n' % (self.nodes, str_chain)

    def json(self):

        chain_in_dicts = []

        for block in self.chain:
            chain_in_dicts.append(block.json())

        return {
            'length': len(self.chain),
            'chain': chain_in_dicts
        }

class Block():
    '''
    Represents a single block in the chain. Each block is timestamped
    based on when it started mining, Is hashed with the previous block
    as well.

    Attributes
    -------------
    index: int
        This blocks current position in the Block Chain

    nonce: int
        Number Used only once, the number that is incremented to
        get a hash that solves the cryptographic puzzle

    previous_hash: String
        String representation of the hash of the previous block

    time_stamp: String
        String representation of the time that this block was intialized

    transactions: List of Tx Objects
        Represents the list of Transactions in this block.
    '''

    def __init__(self, index, previous_hash, transactions=None):
        self.index = index
        self.nonce = None
        self.previous_hash = previous_hash
        self.time_stamp = str(datetime.datetime.now())
        self.transactions = transactions


    def hash(self):
        '''
        Hashing algorithm for a block, encode the String representation
        then find the SHA256 Hash.

        :return: String representation of the SHA256 Hash
        '''
        encoded_block = str(self).encode()
        return SHA256.new(encoded_block).hexdigest()

    def find_nonce(self):
        '''
        PROOF OF WORK ALGORITHM. Starting at a nonce of 1, continue to
        increment until you get a SHA256 Hash with the correct amount of
        leading 0's
        '''
        self.nonce = 1
        check_nonce = False
        while not check_nonce:
            hash_operation = self.hash()
            if hash_operation[:DIFFICULTY] == ( '0' * DIFFICULTY ) :
                check_nonce = True
            else:
                print(self.nonce)
                self.nonce += 1

    def __str__(self):
        trans_list = []
        if self.transactions:
            for tx in self.transactions:
                trans_list.append(tx.json())

        return 'Index: %s\nNonce:  %s\nPrevious Hash; %s\nTime: %s\nTransactions: %s\n' % (
            self.index, self.nonce, self.previous_hash, self.time_stamp, trans_list
        )

    def json(self):
        trans_list = []
        if self.transactions:
            for tx in self.transactions:
                trans_list.append(tx.json())

        return {
            'index': self.index,
            'previous_hash':self.previous_hash,
            'time_stamp':self.time_stamp,
            'nonce': self.nonce,
            'transactions': trans_list
        }


class MemList():
    '''
    Class to represent the list of Transactions to be mined. A object
    must be 1) A Tx object 2) A valid Tx object with all fields valid/
    correct unlocking scripts and 3) Pointing to a previously unspent Tx

    Attributes:
    ------------
    tx_list: List
        List of the Tx objects waiting to become in the list.
    '''

    #TODO Make sure that MEMLIST stays consistent across time/blocks changing
    MAX_NUM_TX = 3
    MINING_REWARD = 1000

    def __init__(self):
        self.tx_list = []

    def add_tx(self, tx):
        '''
        Function to add a Tx to this memlist. Must satisfy the following:

            1) A Tx object
            2) A valid Tx object with all fields valid/correct unlocking scripts and
            3) Pointing to a previously unspent Tx

        :return True if added to tx_list
        '''

        if not (isinstance(tx, Tx) and tx.check_is_valid()):
            return False

        for inp_curr in tx.owned_coins:
            for block in glob_chain:
                for tr in block.transactions:
                    if tr.owned_coins:
                        for inp in tr.owned_coins:
                            if inp_curr.coin_hash == inp.coin_hash:
                                return False

        self.tx_list.append(tx)
        return True

    def get_tx_to_mine(self):
        '''
        A function that returns a list of transactions for us to mine
        from the tx_list. Will always put the transaction that pays
        us on top in case we are the node that mines this block.

        If there are more than MAX_NUM_TX - 1 (the tx that we
        get paid in) in the tx_list, return the list of transactions
        with the highest paying fees for us.

        :return: List of Tx objects for us to mine.
        '''

        if len(self.tx_list) <= self.MAX_NUM_TX - 1:
            to_be_returned = []
            total_fee = 0
            for tx in self.tx_list:
                tx.create_new_coins()
                to_be_returned.append(tx)
                total_fee += tx.fee

            our_transaction = Tx(None, None, [(our_wallet, self.MINING_REWARD + total_fee)], True)
            our_transaction.create_new_coins()
            to_be_returned.insert(0, our_transaction)
            self.tx_list = []
            return to_be_returned

        else:
            to_be_returned = []
            total_fee = 0

            for i in range(0,self.MAX_NUM_TX - 1):
                target = None
                curr_max_fee = 0
                for trans in self.tx_list:
                    if trans.fee > curr_max_fee:
                        target = trans
                        curr_max_fee = trans.fee
                total_fee += curr_max_fee
                target.create_new_coins()
                to_be_returned.append(target)
                self.tx_list.remove(target)

                for tx in to_be_returned:
                    tx.create_new_coins()

            our_transaction = Tx(None, None, [(our_wallet, self.MINING_REWARD + total_fee)], True)
            our_transaction.create_new_coins()
            to_be_returned.insert(0, our_transaction)

            return to_be_returned



