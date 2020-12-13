import sys
from flask import Flask, jsonify, request
from wrking_crypto.blockchain import BlockChain

app = Flask(__name__)
block_chain = BlockChain()

'''
    Module that a user of the network would run to be able to interact
    with other users. All users have the ability to mine, but you don't have
    to. Also how you send transactions to other nodes of the network
    
    BROKEN, Unfortunaley didn't have enough time to fully implement the
    features that would be needed for this to work.
'''

@app.route('/send_tx/', methods=['POST'])
def send_tx():

    #TODO: IMPLEMENT the stuff that will actually get a series of UTXOs
    #of UTXOs to send and sign
    trans = tx.json()
    return jsonify(trans), 201

@app.route('/rec_tx', methods = ['POST'])
def rec_tx():

    #TODO: UNPACK the recieved JSON into a TX object
    json = request.get_json()
    transation_keys = ['inputs', 'outputs', 'amount']


    return jsonify(response), 201

@app.route('/mine_block', methods = ['GET'])
def mine_block():

    previous_block = block_chain.get_prev_block()
    previous_nonce = previous_block['nonce']
    nonce = block_chain.nonce_of_work(previous_nonce)
    previous_hash = block_chain.hash(previous_block)
    block_chain.add_transation(sender=node_address, reciever = 'Isaac', amount = 1)
    block = block_chain.create_block(nonce, previous_hash)
    response = {'message':'You just mined a block!',
                'index':block['index'],
                'timestamp': block['timestamp'],
                'nonce': block['nonce'],
                'previous_hash': block['previous_hash'],
                'transactions':block['transactions']
                }
    return jsonify(response),200

@app.route('/add_transation', methods = ['POST'])
def add_transation():

    json = request.get_json()
    transation_keys = ['sender','receiver','amount']
    if not all (key in json for key in transation_keys):
        return 'Some elements of the transation are missing', 400
    index = block_chain.add_transation(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'Your transation has been added to block {index}'}

    return jsonify(response), 201

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
    app.run( host = '0.0.0.0', port= int(sys.argv[1]) )

    '''
    Code for generating a sample Tx() object
    
    isaac = User()
    lily = User()
    
    isaac_wal_b = isaac.wal.digest()
    utxos = [Output(isaac_wal_b, 10), Output(isaac_wal_b, 20), Output(isaac_wal_b, 5)]
    unlocks = []
    
    for utx in utxos:
        h, sig = isaac.sign(utx.coin_hash)
        unlock = Input(utx.coin_hash, isaac.puk.export_key('DER'), sig)
        unlocks.append(unlock)
    
    to = [(lily.wal.digest(), 30), (isaac.wal.digest(), 2)]
    tx = Tx(unlocks, utxos, to)
    
    '''