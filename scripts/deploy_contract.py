import json
from solcx import compile_standard, install_solc, set_solc_version
from web3 import Web3

def deploy_contract():
    # Ensure Solidity compiler is installed
    solc_version = '0.8.0'
    try:
        set_solc_version(solc_version)
    except Exception as e:
        print(f"Error setting Solidity compiler version {solc_version}: {e}")
        print(f"Installing Solidity compiler version {solc_version}...")
        install_solc(solc_version)
        set_solc_version(solc_version)

    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        print("Failed to connect to Ganache")
        exit(1)
    else:
       print("Connected:", w3.is_connected())

    w3.eth.default_account = w3.eth.accounts[0]

    # Compile the smart contract
    try:
        with open('contracts/AnomalyDetection.sol', 'r') as file:
            contract_source_code = file.read()
    except FileNotFoundError:
        print("Smart contract source file not found")
        exit(1)
    except Exception as e:
        print(f"Error reading smart contract source file: {e}")
        exit(1)

    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {"AnomalyDetection.sol": {"content": contract_source_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "evm.bytecode"]
                }
            }
        }
    })

    bytecode = compiled_sol['contracts']['AnomalyDetection.sol']['AnomalyDetection']['evm']['bytecode']['object']
    abi = compiled_sol['contracts']['AnomalyDetection.sol']['AnomalyDetection']['abi']

    # Deploy the smart contract
    initial_nodes = [w3.eth.accounts[1], w3.eth.accounts[2], w3.eth.accounts[3], w3.eth.accounts[4]]
    threshold = 200

    AnomalyDetection = w3.eth.contract(abi=abi, bytecode=bytecode)
    try:
        tx_hash = AnomalyDetection.constructor(initial_nodes, threshold).transact()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"Error deploying contract: {e}")
        exit(1)

    if tx_receipt.status != 1:
        print("Contract deployment failed")
        exit(1)

    # Save the contract address and ABI
    try:
        contract_address = tx_receipt.contractAddress
        with open('contracts/contract_address.txt', 'w') as file:
            file.write(contract_address)
        with open('contracts/abi.json', 'w') as file:
            json.dump(abi, file)
    except Exception as e:
        print(f"Error saving contract address or ABI: {e}")
        exit(1)

    print(f"Contract deployed at address: {contract_address}")
    print(f"Initial nodes: {initial_nodes}")

    return w3, AnomalyDetection

if __name__ == "__main__":
    deploy_contract()
