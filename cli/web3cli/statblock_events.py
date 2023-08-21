STAT_CREATED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "statID",
            "type": "uint256",
        },
    ],
    "name": "StatCreated",
    "type": "event",
}

STAT_DESCRIPTOR_UPDATED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "statID",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "string",
            "name": "descriptor",
            "type": "string",
        },
    ],
    "name": "StatDescriptorUpdated",
    "type": "event",
}

STAT_ASSIGNED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "address",
            "name": "tokenAddress",
            "type": "address",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "tokenID",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "statID",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "value",
            "type": "uint256",
        },
    ],
    "name": "StatAssigned",
    "type": "event",
}
