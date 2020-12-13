from flask import Flask, request
from pprint import pprint

app = Flask(__name__)
global_data = None

@app.route('/post',methods = ['POST'])
def post():
    global global_data
    input_data = request.json
    global_data = input_data
    pprint(input_data)
    return 'OK', 200

@app.route('/get', methods=['GET'])
def get():
    return global_data, 200

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)