ADMINISTRATOR_DESIGNATED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "address",
            "name": "adminTerminusAddress",
            "type": "address",
        },
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "adminTerminusPoolId",
            "type": "uint256",
        },
    ],
    "name": "AdministratorDesignated",
    "type": "event",
}

NEW_SUBJECT_ADDRESS_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "address",
            "name": "contractAddress",
            "type": "address",
        }
    ],
    "name": "NewSubjectAddress",
    "type": "event",
}

SLOT_CREATED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "address",
            "name": "creator",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "slot",
            "type": "uint256",
        },
    ],
    "name": "SlotCreated",
    "type": "event",
}

ITEM_MARKED_AS_EQUIPPABLE_IN_SLOT_ABI = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "uint256", "name": "slot", "type": "uint256"},
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "itemType",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "itemAddress",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "itemPoolId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "maxAmount",
            "type": "uint256",
        },
    ],
    "name": "ItemMarkedAsEquippableInSlot",
    "type": "event",
}

ITEM_EQUIPPED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "subjectTokenId",
            "type": "uint256",
        },
        {"indexed": True, "internalType": "uint256", "name": "slot", "type": "uint256"},
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "itemType",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "itemAddress",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "itemTokenId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "address",
            "name": "equippedBy",
            "type": "address",
        },
    ],
    "name": "ItemEquipped",
    "type": "event",
}

ITEM_UNEQUIPPED_ABI = {
    "anonymous": False,
    "inputs": [
        {
            "indexed": True,
            "internalType": "uint256",
            "name": "subjectTokenId",
            "type": "uint256",
        },
        {"indexed": True, "internalType": "uint256", "name": "slot", "type": "uint256"},
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "itemType",
            "type": "uint256",
        },
        {
            "indexed": True,
            "internalType": "address",
            "name": "itemAddress",
            "type": "address",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "itemTokenId",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "uint256",
            "name": "amount",
            "type": "uint256",
        },
        {
            "indexed": False,
            "internalType": "address",
            "name": "unequippedBy",
            "type": "address",
        },
    ],
    "name": "ItemUnequipped",
    "type": "event",
}
