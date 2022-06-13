// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

struct DroppableToken {
    uint256 tokenType;
    address tokenAddress; // address of the token
    uint256 tokenId;
    uint256 amount;
}

uint256 constant ERC20_TYPE = 20;
uint256 constant ERC721_TYPE = 721;
uint256 constant ERC1155_TYPE = 1155;
uint256 constant TERMINUS_MINTABLE_TYPE = 1;
uint256 constant ERC721_MINTABLE_TYPE = 2;

library LibDropperV2 {
    bytes32 constant DROPPERV2_STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.DropperV2");

    struct DropperV2Storage {
        address TerminusAdminContractAddress;
        uint256 TerminusAdminPoolID;
        uint256 NumDrops;
        mapping(uint256 => bool) IsDropActive;
        mapping(uint256 => address) DropSigner;
        mapping(uint256 => DroppableToken) DropToken;
        mapping(uint256 => string) DropURI;
        // dropID => maximum number of tokens a user can claim as part of this drop
        mapping(uint256 => uint256) MaxClaimable;
        // address => dropID => total amount claimed for that drop
        mapping(address => mapping(uint256 => uint256)) AmountClaimed;
    }

    function dropperV2Storage()
        internal
        pure
        returns (DropperV2Storage storage ds)
    {
        bytes32 position = DROPPERV2_STORAGE_POSITION;
        assembly {
            ds.slot := position
        }
    }
}
