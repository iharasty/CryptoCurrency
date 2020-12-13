'''
Blockchain, Module 1
Created by: Isaac Harasty

This python module is what is accomplished in the 'Module 1' Section of the slides
that were submitted for this project.

Creates a cryptographically linked chain of blocks with basic data fields, including
Time Stamps, Block Index, the Previous Hash, and Nonce for mining.

Also, uses flasks to create endpoints capable of a few basic operations, namely
getting the chain, and mining a new block.
'''

import datetime
import json
import hashlib
from flask import Flask, jsonify

# Creating the BlockChain
class BlockChain:

    '''
    The block chain object. Capable of functionality outlined above, a cryptographically
    linked list of 'blocks'. In this module, blocks have yet to hold transactions, but
    are rather dict() objects of the following structure.

         {
            'index': int,
            'timestamp': str,
            'nonce': int,
            'previous_hash': str
        }

    Attributes:
    ---------------
    chain: List
        The effectual block chain, a Python list object full of Block dicts
    '''

    def __init__(self):
        self.chain = []
        genesis_block = self.find_new_block('0')
        self.chain.append(genesis_block)

    def add_block(self, block):
        '''
        Adds a block to the chain. Assumed that blocks are of the correct form.

        :param block: a dict object representing a block
        :return: the block that was added/inputted
        '''

        self.chain.append(block)
        return block

    def get_prev_block(self):
        '''
        Returns the last block of the block chain

        :return: dict object representing the most recent (last) block added
        '''
        return self.chain[-1]

    def hash(self, block):
        '''
        A method of the block chain to find the Hash of an inputted block.
        Uses the hashlib's SHA256 method to return the hexdigest()

        :param block: A block dictionary
        :return: a String representation of the block's hash
        '''
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def find_new_block(self, previous_hash):
        '''
        Proof of Work algorithm. Difficulty is currently set to 4 by functionality.
        Creates a prospective new block to be added to the chain with the hash of
        the prev block inputted. Continue to increment the Nonce value until you get
        a hash that satisfies the POW requierment of 4 leading 0's

        :param previous_hash: String representation of the last blocks SHA256 Hash
        :return: the new block Dict() object.
        '''
        new_nonce = 1
        check_nonce = False
        new_block = {
            'index': len(self.chain) + 1,
            'timestamp':str(datetime.datetime.now()),
            'nonce': new_nonce,
            'previous_hash':previous_hash
        }

        while not check_nonce:
            hash_operation = self.hash(new_block)
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
            new_block['nonce'] = new_nonce

        return new_block


    # checking the critical features of the block chain

    def is_chain_valid(self,chain):
        '''
        method to check if a given chain is crytographically valid. This means
        the following 2 conditions are met.

            1) make to make sure each nonce of work is correct
            2) each hash of the previous block is the correct hash

        :param chain: a List object representing the block chain being checked.
        Each item in chain must be a dictionary following the system above.
        :return: True if it is valid, False if not
        '''
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce ** 2 - previous_nonce ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1

        return True


# Creating the Web App

app = Flask(__name__)
block_chain = BlockChain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():

    previous_block = block_chain.get_prev_block()
    previous_hash = block_chain.hash(previous_block)
    block = block_chain.find_new_block(previous_hash)
    block_chain.add_block(block)

    return jsonify(block), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': block_chain.chain,
                'length': len(block_chain.chain)}
    return jsonify(response), 200

# Running the app

if __name__ == '__main__':
    app.run( host = '0.0.0.0', port=5000 )



