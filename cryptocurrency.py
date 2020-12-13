'''
CryptoCurr Currency
Created by: Isaac Harasty
'''

import datetime
import json
import hashlib
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Creating the BlockChain

class BlockChain:

    def __init__(self):
        self.memlist = []
        self.chain = []
        self.create_block(nonce = 1, previous_hash = '0')
        self.nodes = set()

    def add_block(self, block):
        '''
        Adds a block to the chain. Assumed that blocks are of the correct form.

        :param block: a dict object representing a block
        :return: the block that was added/inputted
        '''

        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def mine_new_block(self, previous_hash):

        new_nonce = 1
        check_nonce = False
        new_block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'nonce': new_nonce,
            'previous_hash': previous_hash
        }

        while not check_nonce:
            hash_operation = self.hash(new_block)
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
            new_block['nonce'] = new_nonce

        return new_block

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self,chain):
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

    def add_transation(self, sender, receiver, amount):
        self.memlist.append({
            'sender':sender,
            'receiver': receiver,
            'amount': amount
        })

        return self.get_prev_block()['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain =  response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    # END Module 1 changes

#Part 2 Mining our Block Chain

app = Flask(__name__)
node_address = str(uuid4()).replace('-','')
block_chain = BlockChain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():

    previous_block = block_chain.get_prev_block()
    previous_hash = block_chain.hash(previous_block)
    block = block_chain.find_new_block(previous_hash)
    block_chain.add_block(block)

    return jsonify(block), 200

# Adding a new Transation to the block Chain
@app.route('/add_transation', methods = ['POST'])
def add_transation():

    json = request.get_json()
    transation_keys = ['sender','receiver','amount']
    if not all (key in json for key in transation_keys):
        return 'Some elements of the transation are missing', 400
    index = block_chain.add_transation(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Your transation has been added to block {index}'}

    return jsonify(response), 201

# END Part 2

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = block_chain.is_chain_valid(block_chain.chain)
    if is_valid:
        response = {'message': 'Our Blockchain is valid.'}
    else:
        response = {'message': 'Our Blockchain is NOT valid.'}
    return jsonify(response)

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': block_chain.chain,
                'length': len(block_chain.chain)}
    return jsonify(response), 200

# Part 3 - Decentralizing the Block Chain

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No Node", 400
    for node in nodes:
        block_chain.add_node(node)
    response = {'message': 'Those nodes are now connected: ',
                'total_nodes': list(block_chain.nodes) }
    return jsonify(response), 201

# Replacing our chain with other chains if they're longer
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replace = block_chain.replace_chain(block_chain.chain)
    if is_chain_replace:
        response = {'message': 'Our Blockchain is not the longest. Has been updated.',
                    'new_chain': block_chain.chain}
    else:
        response = {'message': 'Our Blockchain is the longest. It has not been replaced.',
                    'curr_chain': block_chain.chain}
    return jsonify(response)

# Running the app
if __name__ == '__main__':
    app.run( host = '0.0.0.0', port=5000 )



