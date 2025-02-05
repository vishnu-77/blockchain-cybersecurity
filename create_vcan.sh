#!/bin/bash

# Create virtual CAN interfaces
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
sudo ip link add dev vcan1 type vcan
sudo ip link set up vcan1
sudo ip link add dev vcan2 type vcan
sudo ip link set up vcan2
sudo ip link add dev vcan3 type vcan
sudo ip link set up vcan3

# Verify interfaces
ip link show vcan0
ip link show vcan1
ip link show vcan2
ip link show vcan3


echo "Virtual CAN interfaces vcan0, vcan1, vcan2 and vcan3 have been created and set up."
