from flask import Flask, render_template, request
from web3 import Web3

app = Flask(__name__)

CONTRACT_ABI = [
    # Add your contract ABI here
]

CONTRACT_BYTECODE = '0x123456789abcdef'

CONTRACT_BYTECODE_RUNTIME = '0x123456789abcdef'

def connect_to_blockchain():
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"))
    return w3

def create_contract():
    w3 = connect_to_blockchain()
    account = w3.eth.account.create()
    contract = w3.eth.contract(
        abi=CONTRACT_ABI,
        bytecode=CONTRACT_BYTECODE,
        bytecode_runtime=CONTRACT_BYTECODE_RUNTIME
    )
    tx_hash = contract.constructor().transact({'from': account.address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    return contract_address, account

def get_contract_instance(contract_address):
    w3 = connect_to_blockchain()
    contract = w3.eth.contract(address=contract_address, abi=CONTRACT_ABI)
    return contract

def create_funding_request(contract_address, account, company_name, amount):
    contract = get_contract_instance(contract_address)
    tx_hash = contract.functions.create_funding_request(company_name, amount).transact({'from': account.address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt

def get_funding_requests(contract_address):
    contract = get_contract_instance(contract_address)
    requests = []
    for i in range(contract.functions.get_request_count().call()):
        request = contract.functions.requests(i).call()
        requests.append({
            'id': i,
            'company_name': request[0],
            'amount': request[1],
            'investors': request[2],
            'completed': request[3],
            'approved': request[4]
        })
    return requests

def approve_funding_request(contract_address, account, request_id):
    contract = get_contract_instance(contract_address)
    tx_hash = contract.functions.approve_request(request_id).transact({'from': account.address})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt

def invest_in_funding_request(contract_address, account, request_id, amount):
    contract = get_contract_instance(contract_address)
    tx_hash = contract.functions.invest(request_id).transact({'from': account.address, 'value': amount})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return tx_receipt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_contract', methods=['POST'])
def create_contract_route():
    contract_address, account = create_contract()
    return contract_address

@app.route('/create_funding_request', methods=['POST'])
def create_funding_request_route():
    contract_address = request.form['contract_address']
    account = request.form['account']
    company_name = request.form['company_name']
    amount = request.form['amount']
    tx_receipt = create_funding_request(contract_address, account, company_name, amount)
    return tx_receipt

@app.route('/get_funding_requests', methods=['POST'])
def get_funding_requests_route():
    contract_address = request.form['contract_address']
    requests = get_funding_requests(contract_address)
    return render_template('funding_requests.html', requests=requests)

if __name__ == '__main__':
    app.run(debug=True)
