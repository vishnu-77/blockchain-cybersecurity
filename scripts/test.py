import unittest
import time
import json
from web3 import Web3

class BlockchainDDoSDetectionTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load contract ABI and address
        try:
            with open('scripts/abi.json', 'r') as file:
                cls.abi = json.load(file)
            with open('scripts/contract_address.txt', 'r') as file:
                cls.contract_address = file.read().strip()
        except Exception as e:
            print(f"Error loading contract ABI or address: {e}")
            raise
        
        # Connect to Ganache
        cls.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        if not cls.w3.is_connected():
            raise ConnectionError("Failed to connect to Ganache")
        
        cls.w3.eth.default_account = cls.w3.eth.accounts[0]
        cls.contract = cls.w3.eth.contract(address=cls.contract_address, abi=cls.abi)

    def test_latency_of_transaction(self):
        node_address = self.w3.eth.accounts[0]
        data = 110
        
        start_time = time.time()
        try:
            tx_hash = self.contract.functions.reportAnomaly(data, node_address).transact({'from': node_address})
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            self.fail(f"Transaction failed: {e}")
        end_time = time.time()

        latency = end_time - start_time
        print(f"Transaction Latency: {latency} seconds")

        self.assertTrue(latency < 5, "Transaction latency is too high!")

    def test_scalability_under_load(self):
        if len(self.w3.eth.accounts) < 10:
            self.skipTest("Not enough accounts for scalability test.")
        
        load_nodes = [self.w3.eth.accounts[i] for i in range(1, 11)]
        data = 110
        
        start_time = time.time()
        for node in load_nodes:
            try:
                tx_hash = self.contract.functions.reportAnomaly(data, node).transact({'from': node})
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
            except Exception as e:
                self.fail(f"Transaction failed for node {node}: {e}")
        end_time = time.time()

        total_time = end_time - start_time
        print(f"Scalability Test - Total Time for 10 nodes: {total_time} seconds")

        self.assertTrue(total_time < 10, "Scalability test failed!")

    def test_resource_usage(self):
        import psutil

        node_address = self.w3.eth.accounts[0]
        data = 250
        
        process = psutil.Process()
        start_cpu = process.cpu_percent(interval=None)
        start_memory = process.memory_info().rss

        try:
            tx_hash = self.contract.functions.reportDDoS(data).transact({'from': node_address})
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            self.fail(f"Transaction failed: {e}")

        end_cpu = process.cpu_percent(interval=None)
        end_memory = process.memory_info().rss

        cpu_usage = end_cpu - start_cpu
        memory_usage = (end_memory - start_memory) / 1024 / 1024  # in MB

        print(f"CPU Usage: {cpu_usage}%")
        print(f"Memory Usage: {memory_usage} MB")

        self.assertTrue(cpu_usage < 50, "CPU usage is too high!")
        self.assertTrue(memory_usage < 100, "Memory usage is too high!")

    def test_security_of_data_integrity(self):
        node_address = self.w3.eth.accounts[0]
        data = 120
        
        try:
            tx_hash = self.contract.functions.reportAnomaly(data, node_address).transact({'from': node_address})
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            self.fail(f"Transaction failed: {e}")

        events = self.contract.events.AnomalyReported().createFilter(fromBlock='latest').get_all_entries()
        reported_event = events[-1] if events else None

        self.assertIsNotNone(reported_event, "No AnomalyReported event found!")
        self.assertEqual(reported_event.args.node, node_address, "Node address mismatch in the event!")
        self.assertEqual(reported_event.args.data, data, "Data mismatch in the event!")

    def test_effectiveness_of_ddos_mitigation(self):
        node_address = self.w3.eth.accounts[0]
        data = 250
        
        try:
            tx_hash = self.contract.functions.reportDDoS(data).transact({'from': node_address})
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        except Exception as e:
            self.fail(f"Transaction failed: {e}")

        events = self.contract.events.DDoSReported().createFilter(fromBlock='latest').get_all_entries()
        reported_event = events[-1] if events else None

        self.assertIsNotNone(reported_event, "No DDoSReported event found!")
        self.assertEqual(reported_event.args.node, node_address, "Node address mismatch in the event!")
        self.assertEqual(reported_event.args.data, data, "Data mismatch in the event!")

    def test_system_stability(self):
        try:
            for i in range(100):  # Simulate continuous operation
                self.test_latency_of_transaction()
        except Exception as e:
            self.fail(f"System stability test failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
