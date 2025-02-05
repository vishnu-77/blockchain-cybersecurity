import json
import time
import subprocess
from solcx import compile_standard, install_solc, set_solc_version
from web3 import Web3

# Ensure Solidity compiler is installed
solc_version = '0.8.0'
try:
    set_solc_version(solc_version)
except Exception as e:
    print(f"Installing Solidity compiler version {solc_version}...")
    install_solc(solc_version)
    set_solc_version(solc_version)

def load_contract_details():
    with open('contracts/contract_address.txt', 'r') as file:
        contract_address = file.read().strip()
    with open('contracts/abi.json', 'r') as file:
        abi = json.load(file)
    return contract_address, abi

def initialize_contract():
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        raise ConnectionError("Failed to connect to Ganache")

    contract_address, abi = load_contract_details()
    w3.eth.default_account = w3.eth.accounts[0]
    contract = w3.eth.contract(address=contract_address, abi=abi)
    return w3, contract

def detect_anomaly(contract, data, node_id, w3):
    try:
        tx_hash = contract.functions.detectAnomaly(data).transact({'from': w3.eth.default_account}) 
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Anomaly reported from Node {node_id}: Data {data}")
        print(f"Transaction: {receipt.transactionHash.hex()}")
        print(f"Gas used: {receipt.gasUsed}")
        log_anomaly(data, node_id)
    except Exception as e:
        print(f"Error reporting anomaly: {e}")

def isolate_node(contract, node_id, w3):
    try:
        tx_hash = contract.functions.isolateNode(node_id).transact({'from': w3.eth.default_account})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Node {node_id} isolated.")
        print(f"Transaction: {receipt.transactionHash.hex()}")
        print(f"Gas used: {receipt.gasUsed}")
        log_isolated_node(node_id)
    except Exception as e:
        print(f"Error isolating node: {e}")

def notify_other_nodes(node_id, data):
    print(f"Notifying other nodes about anomaly from Node {node_id}: {data}")

def remove_node_from_network(node_id, channel):
    try:
        result = subprocess.run(['ip', 'link', 'show', channel], capture_output=True, text=True)
        if 'does not exist' in result.stderr:
            print(f"Channel {channel} does not exist.")
            return
        subprocess.run(['sudo', 'ip', 'link', 'delete', channel], check=True)
        print(f"Removed Node {node_id} with channel {channel} from the network.")
    except subprocess.CalledProcessError as e:
        print(f"Error removing node {node_id}: {e}")

def reinitialize_contract(w3, nodes):
    # Compile the smart contract
    with open('contracts/AnomalyDetection.sol', 'r') as file:
        contract_source_code = file.read()

    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {"AnomalyDetection.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    })

    bytecode = compiled_sol['contracts']['AnomalyDetection.sol']['AnomalyDetection']['evm']['bytecode']['object']
    abi = compiled_sol['contracts']['AnomalyDetection.sol']['AnomalyDetection']['abi']
    AnomalyDetection = w3.eth.contract(abi=abi, bytecode=bytecode)

    tx_hash = AnomalyDetection.constructor(nodes, 200).transact()
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    new_contract_address = tx_receipt.contractAddress

    with open('contracts/contract_address.txt', 'w') as file:
        file.write(new_contract_address)
    with open('contracts/abi.json', 'w') as file:
        json.dump(abi, file)
    print(f"Contract reinitialized at {new_contract_address}")

def log_anomaly(data, node_id):
    try:
        with open('anomaly_log.txt', 'a') as file:
            file.write(f"Anomaly reported from Node {node_id}: Data {data} at {time.ctime()}\n")
    except Exception as e:
        print(f"Error logging anomaly: {e}")

def log_isolated_node(node_id):
    try:
        with open('isolated_nodes_log.txt', 'a') as file:
            file.write(f"Node {node_id} isolated at {time.ctime()}\n")
    except Exception as e:
        print(f"Error logging isolated node: {e}")

def report_ddos(contract, data):
    try:
        tx_hash = contract.functions.reportDDoS(data).transact({'from': Web3.toChecksumAddress(contract.functions.owner().call())})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"DDoS reported with Data {data}")
        print(f"Transaction: {receipt.transactionHash.hex()}")
        print(f"Gas used: {receipt.gasUsed}")
        log_ddos(data)
    except Exception as e:
        print(f"Error reporting DDoS: {e}")

def log_ddos(data, node_id):
    try:
        with open('ddos_log.txt', 'a') as file:
            file.write(f"DDoS detected from Node {node_id}: Data {data} at {time.ctime()}\n")
    except Exception as e:
        print(f"Error logging DDoS: {e}")
