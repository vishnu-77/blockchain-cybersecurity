import can
import time
import threading

def simulate_can_network(channel, node_id, anomaly_delay=None, ddos_interval=None):
    bus = can.interface.Bus(channel=channel, interface='socketcan')
    start_time = time.time()
    ddos_start_time = time.time() if ddos_interval else None

    print(f"Node {node_id} started sending messages on {channel}")

    while True:
        current_time = time.time()
        node_id_int = ord(node_id[0]) if isinstance(node_id, str) else node_id

        if node_id == 'Node1':
            # Node 1 can send both normal and anomalous data and DDoS traffic
            if anomaly_delay and (current_time - start_time) > anomaly_delay:
                data = [node_id_int, 0xFF, 0xFF, 0xFF]  # Anomalous data
                print(f"Node {node_id} switched to anomalous data")
            else:
                data = [node_id_int, 0x00, 0x00, 0x00]  # Normal data

            if ddos_interval and (current_time - start_time) > anomaly_delay:
                for _ in range(10):  # Send a DDoS attack with 10 messages
                    try:
                        msg = can.Message(arbitration_id=0x123, data=data, is_extended_id=False)
                        bus.send(msg)
                        print(f"Node {node_id} sent DDoS message: {msg}")
                    except can.CanError as e:
                        print(f"Node {node_id} failed to send DDoS message: {e}")
                    time.sleep(0.1)  # Short interval between DDoS messages
            else:
                try:
                    msg = can.Message(arbitration_id=0x123, data=data, is_extended_id=False)
                    bus.send(msg)
                    print(f"Node {node_id} successfully sent message: {msg}")
                except can.CanError as e:
                    print(f"Node {node_id} failed to send message: {e}")

            time.sleep(1)  # Normal interval between messages
        else:
            # Node 2, Node 3, and Master Node only send normal traffic
            data = [node_id_int, 0x00, 0x00, 0x00]  # Normal data
            try:
                msg = can.Message(arbitration_id=0x123, data=data, is_extended_id=False)
                bus.send(msg)
                print(f"Node {node_id} successfully sent message: {msg}")
            except can.CanError as e:
                print(f"Node {node_id} failed to send message: {e}")
            time.sleep(1)  # Normal interval between messages

if __name__ == "__main__":
    nodes = [
        ('MasterNode', 'vcan0', None, None),  # Master Node
        ('Node1', 'vcan1', 20, 10),  # Anomaly after 20 seconds, DDoS interval of 10 seconds
        ('Node2', 'vcan2', None, None),
        ('Node3', 'vcan3', None, None)
    ]

    for node_id, channel, anomaly_delay, ddos_interval in nodes:
        threading.Thread(target=simulate_can_network, args=(channel, node_id, anomaly_delay, ddos_interval)).start()
