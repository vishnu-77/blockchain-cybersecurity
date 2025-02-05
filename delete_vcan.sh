#!/bin/bash

# Delete virtual CAN interfaces
sudo ip link set down vcan0
sudo ip link delete vcan0
sudo ip link set down vcan1
sudo ip link delete vcan1
sudo ip link set down vcan2
sudo ip link delete vcan2

# Verify removal
ip link show vcan0
ip link show vcan1
ip link show vcan2
