import json
import random
import can
from anomaly_reporter import (
    initialize_contract,
    detect_anomaly,
    isolate_node,
    notify_other_nodes,
    remove_node_from_network,
    reinitialize_contract,
    report_ddos,
    log_ddos
)

def read_can_data_from_channel(channel):
    bus = can.interface.Bus(channel=channel, interface='socketcan')
    try:
        message = bus.recv()  # Receive a CAN message
        if message:
            # Extract data from the CAN message
            data = message.data[1]  # Use the second byte of data for processing
            return data
    finally:
        bus.shutdown()  # Ensure proper shutdown
    return None

def process_data(data, anomaly_threshold, ddos_threshold):
    # Detect if data is indicative of an anomaly or a DDoS attack
    is_anomaly = data > anomaly_threshold
    is_ddos = data > ddos_threshold
    
    # Print the results
    print(f"Data: {data}, Anomaly Threshold: {anomaly_threshold}, DDoS Threshold: {ddos_threshold}")
    print(f"is_anomaly: {is_anomaly}, is_ddos: {is_ddos}")
    
    return is_anomaly, is_ddos

def simulate_can_network():
    w3, contract = initialize_contract()
    nodes = contract.functions.getNormalNodes().call()
    anomalies = {}
    ddos_attacks = {}
    node_channels = {node: f'vcan{index}' for index, node in enumerate(nodes)}  # Assume each node has a unique channel

    anomaly_threshold = contract.functions.anomalyThreshold().call()
    ddos_threshold = 200  # Adjust threshold as needed

    for node in nodes:
        # Simulate reading CAN data from node
        channel = node_channels[node]
        data = read_can_data_from_channel(channel)
        if data is not None:
            is_anomaly, is_ddos = process_data(data, anomaly_threshold, ddos_threshold)
            if is_anomaly:
                anomalies[node] = data
            if is_ddos:
                ddos_attacks[node] = data

    return w3, contract, nodes, anomalies, ddos_attacks, node_channels

def notify_other_nodes(node, data, issue_type, contract, tx_hash):
    # Example logic to determine other nodes
    nodes_to_notify = [n for n in contract.functions.getNormalNodes().call() if n != node]
    
    # Format the notification message
    notification_message = {
        "issue_type": issue_type,
        "affected_node": node,
        "data": data,
        "contract_address": contract.address,
        "transaction_hash": tx_hash
    }
    
    # Simulate sending notifications
    for n in nodes_to_notify:
        # Here you might use an actual network call or messaging system
        # For this example, we'll just print the notification
        print(f"Notification to Node {n}: {json.dumps(notification_message, indent=2)}")

def detect_anomalies_and_ddos():
    w3, contract, nodes, anomalies, ddos_attacks, node_channels = simulate_can_network()
    anomaly_threshold = contract.functions.anomalyThreshold().call()
    ddos_threshold = 20  # Adjust threshold as needed

    # List initial nodes and their channels
    print("Initial nodes associated with the smart contract:")
    for node in nodes:
        print(f"Node {node} with channel {node_channels[node]}")

    # Nodes to be removed and their channels
    nodes_to_remove = set()
    normal_nodes = [node for node in nodes if node not in anomalies and node not in ddos_attacks]

    # Handle anomalies
    for node in list(anomalies.keys()):  # Iterate over a copy of the keys
        data = anomalies.get(node)
        if data and data > anomaly_threshold:
            print(f"Anomaly detected from Node {node}: Data {data}")
            try:
                # Report anomaly to smart contract
                tx_hash = contract.functions.detectAnomaly(data).transact({'from': w3.eth.default_account})
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                print(f"Anomaly reported from Node {node}: Data {data}")
                print(f"Transaction: {receipt.transactionHash.hex()}")
                print(f"Gas used: {receipt.gasUsed}")

                # Notify other nodes
                notify_other_nodes(node, data, "Anomaly", contract, receipt.transactionHash.hex())

                # Handle the anomaly
                isolate_node(contract, node, w3)
                nodes_to_remove.add(node)
                print(f"Anomaly isolated and notified for Node {node}")
            except Exception as e:
                print(f"Error handling anomaly for Node {node}: {e}")

    # Handle DDoS attacks
    for node in list(ddos_attacks.keys()):  # Iterate over a copy of the keys
        data = ddos_attacks[node]
        print(f"Potential DDoS detected from Node {node}: Data {data}")
        try:
            # Report DDoS to smart contract
            tx_hash = contract.functions.reportDDoS(data).transact({'from': w3.eth.default_account})
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Potential DDoS reported from Node {node}: Data {data}")
            print(f"Transaction: {receipt.transactionHash.hex()}")
            print(f"Gas used: {receipt.gasUsed}")

            # Notify other nodes
            notify_other_nodes(node, data, "DDoS", contract, receipt.transactionHash.hex())

            # Handle the DDoS
            isolate_node(contract, node, w3)
            nodes_to_remove.add(node)
            print(f"DDoS isolated and notified for Node {node}")
        except Exception as e:
            print(f"Error handling DDoS for Node {node}: {e}")

    # Remove nodes after processing anomalies and DDoS attacks
    for node in nodes_to_remove:
        try:
            remove_node_from_network(node, node_channels[node])
            print(f"Removed Node {node} with channel {node_channels[node]} from the network.")
        except Exception as e:
            print(f"Error removing Node {node} from network: {e}")

    # Update non-compromised nodes
    non_compromised_nodes = [node for node in normal_nodes if node not in nodes_to_remove]

    # Reinitialize contract with remaining normal nodes
    if non_compromised_nodes:
        try:
            reinitialize_contract(w3, non_compromised_nodes)
            print(f"Contract is reinitialized with non-compromised nodes.")
        except Exception as e:
            print(f"Error reinitializing contract: {e}")

    # List non-compromised nodes and their channels
    print("Non-compromised nodes after detection:")
    for node in non_compromised_nodes:
        print(f"Node {node} with channel {node_channels[node]}")

if __name__ == "__main__":
    detect_anomalies_and_ddos()
