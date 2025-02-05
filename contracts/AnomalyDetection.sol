// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AnomalyDetection {
    address public owner;
    uint public anomalyThreshold;

    mapping(address => bool) public isolatedNodes;
    mapping(address => bool) public compromisedNodes;
    address[] public normalNodes;

    constructor(address[] memory _normalNodes, uint _threshold) {
        owner = msg.sender;
        normalNodes = _normalNodes;
        anomalyThreshold = _threshold;
    }

    function setAnomalyThreshold(uint _threshold) public {
        require(msg.sender == owner, "Only owner can set the threshold");
        anomalyThreshold = _threshold;
    }

    function detectAnomaly(uint data) public {
        require(data > anomalyThreshold, "Data does not exceed threshold");
        compromisedNodes[msg.sender] = true;
    }

    function isolateNode(address node) public {
        require(msg.sender == owner, "Only owner can isolate nodes");
        isolatedNodes[node] = true;
    }

    function reportDDoS(uint data) public {
        require(data > anomalyThreshold, "Data does not exceed threshold for DDoS");
        compromisedNodes[msg.sender] = true;
    }

    function getNormalNodes() public view returns (address[] memory) {
        return normalNodes;
    }

    function getCompromisedNodes() public view returns (address[] memory) {
        uint length = 0;
        for (uint i = 0; i < normalNodes.length; i++) {
            if (compromisedNodes[normalNodes[i]]) {
                length++;
            }
        }

        address[] memory compromised = new address[](length);
        uint index = 0;
        for (uint i = 0; i < normalNodes.length; i++) {
            if (compromisedNodes[normalNodes[i]]) {
                compromised[index] = normalNodes[i];
                index++;
            }
        }
        return compromised;
    }
}
