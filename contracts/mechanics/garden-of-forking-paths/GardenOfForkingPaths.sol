// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/engine
 */

pragma solidity ^0.8.0;

import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import {TerminusPermissions} from "@moonstream/contracts/terminus/TerminusPermissions.sol";
import "../../diamond/libraries/LibDiamond.sol";

struct Session {
    address playerTokenAddress;
    address paymentTokenAddress;
    uint256 paymentAmount;
    bool isActive; // active -> stake if ok,  cannot unstake
    bool isChoosingActive; // if active -> players can choose path in current stage
    string uri;
    uint256[] stages;
}

library LibGOFP {
    bytes32 constant STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.mechanics.GardenOfForkingPaths");

    struct GOFPStorage {
        address AdminTerminusAddress;
        uint256 AdminTerminusPoolID;
        uint256 numSessions;
        mapping(uint256 => Session) sessionById;
        //stage => tokenId => index in stakedTokens
        mapping(uint256 => mapping(uint256 => uint256)) stakedTokenIndex;
        //stage => owner => tokens, Important: indexing starts from 1
        mapping(uint256 => mapping(address => mapping(uint256 => uint256))) stakedTokens;
        mapping(uint256 => mapping(address => uint256)) stakedTokensCountOfOwner;
        // session -> stage -> correct path index
        mapping(uint256 => mapping(uint256 => uint256)) sessionStagePath;
    }

    function gofpStorage() internal pure returns (GOFPStorage storage gs) {
        bytes32 position = STORAGE_POSITION;
        assembly {
            gs.slot := position
        }
    }
}

contract GOFPFacet is ERC1155Holder, TerminusPermissions, ERC721Holder {
    modifier onlyGameMaster() {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            _holdsPoolToken(gs.AdminTerminusAddress, gs.AdminTerminusPoolID, 1),
            "GOFPFacet.onlyGameMaster: The address is not an authorized game master"
        );
        _;
    }

    event SessionCreated(
        uint256 sessionID,
        address indexed playerTokenAddress,
        address indexed paymentTokenAddress,
        uint256 paymentAmount,
        string URI,
        bool active
    );
    event SessionActivated(uint256 indexed sessionID, bool isActive);
    event SessionChoosingActivated(
        uint256 indexed sessionID,
        bool isChoosingActive
    );
    event PathRegistered(
        uint256 indexed sessionID,
        uint256 stage,
        uint256 path
    );

    function init(address adminTerminusAddress, uint256 adminTerminusPoolID)
        external
    {
        LibDiamond.enforceIsContractOwner();
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        gs.AdminTerminusAddress = adminTerminusAddress;
        gs.AdminTerminusPoolID = adminTerminusPoolID;
    }

    function getSession(uint256 sessionID)
        external
        view
        returns (Session memory)
    {
        return LibGOFP.gofpStorage().sessionById[sessionID];
    }

    function adminTerminusInfo() external view returns (address, uint256) {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        return (gs.AdminTerminusAddress, gs.AdminTerminusPoolID);
    }

    function numSessions() external view returns (uint256) {
        return LibGOFP.gofpStorage().numSessions;
    }

    function createSession(
        address playerTokenAddress,
        address paymentTokenAddress,
        uint256 paymentAmount,
        bool isActive,
        string memory uri,
        uint256[] memory stages
    ) external onlyGameMaster {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        gs.numSessions++;

        require(
            gs.sessionById[gs.numSessions].playerTokenAddress == address(0),
            "GOFPFacet.createSession: Session already registered"
        );

        require(
            playerTokenAddress != address(0),
            "GOFPFacet.createSession: playerTokenAddress can't be zero address"
        );

        gs.sessionById[gs.numSessions] = Session({
            playerTokenAddress: playerTokenAddress,
            paymentTokenAddress: paymentTokenAddress,
            paymentAmount: paymentAmount,
            isActive: isActive,
            isChoosingActive: true,
            uri: uri,
            stages: stages
        });
        emit SessionCreated(
            gs.numSessions,
            playerTokenAddress,
            paymentTokenAddress,
            paymentAmount,
            uri,
            isActive
        );
    }

    function setSessionActive(uint256 sessionID, bool isActive)
        external
        onlyGameMaster
    {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.setSessionActive: Invalid session ID"
        );
        gs.sessionById[gs.numSessions].isActive = isActive;
        emit SessionActivated(sessionID, isActive);
    }

    function getCorrectPathForStage(uint256 sessionID, uint256 stage)
        external
        view
        returns (uint256)
    {
        return LibGOFP.gofpStorage().sessionStagePath[sessionID][stage];
    }

    function setCorrectPathForStage(
        uint256 sessionID,
        uint256 stage,
        uint256 path,
        bool setIsChoosingActive
    ) external onlyGameMaster {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.setCorrectPathForStage: Invalid session"
        );
        require(
            stage < gs.sessionById[sessionID].stages.length,
            "GOFPFacet.setCorrectPathForStage: Invalid stage"
        );
        require(
            !gs.sessionById[sessionID].isChoosingActive,
            "GOFPFacet.setCorrectPathForStage: Deactivate isChoosingActive before setting the correct path"
        );
        // Paths are 1-indexed to avoid possible confusion involving default value of 0
        require(
            path >= 1 && path <= gs.sessionById[sessionID].stages[stage],
            "GOFPFacet.setCorrectPathForStage: Invalid path"
        );
        // We use the default value of 0 as a guard to check that path has not already been set for that
        // stage. No changes allowed for a given stage after the path was already chosen.
        require(
            gs.sessionStagePath[sessionID][stage] == 0,
            "GOFPFacet.setCorrectPathForStage: Path has already been chosen for that stage"
        );
        require(
            stage == 0 || gs.sessionStagePath[sessionID][stage - 1] != 0,
            "GOFPFacet.setCorrectPathForStage: Path not set for previous stage"
        );
        gs.sessionStagePath[sessionID][stage] = path;
        gs.sessionById[sessionID].isChoosingActive = setIsChoosingActive;

        emit PathRegistered(sessionID, stage, path);
        emit SessionChoosingActivated(sessionID, setIsChoosingActive);
    }

    function setSessionChoosingActive(uint256 sessionID, bool isChoosingActive)
        external
        onlyGameMaster
    {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.setSessionChoosingActive: Invalid session ID"
        );
        gs.sessionById[gs.numSessions].isChoosingActive = isChoosingActive;
        emit SessionChoosingActivated(sessionID, isChoosingActive);
    }

    function _addTokenToEnumeration(
        uint256 sessionId,
        address owner,
        uint256 tokenId
    ) internal {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();

        require(
            gs.stakedTokenIndex[sessionId][tokenId] == 0,
            "GOFPFacet._addTokenToEnumeration: Token was already added to enumeration"
        );
        uint256 currStaked = gs.stakedTokensCountOfOwner[sessionId][owner];
        gs.stakedTokens[sessionId][owner][currStaked + 1] = tokenId;
        gs.stakedTokenIndex[sessionId][tokenId] = currStaked + 1;
    }

    function _removeTokenFromEnumeration(
        uint256 sessionId,
        address owner,
        uint256 tokenId
    ) internal {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            gs.stakedTokenIndex[sessionId][tokenId] != 0,
            "GOFPFacet._removeTokenFromEnumeration: Token wasn't added to enumeration"
        );
        uint256 currStaked = gs.stakedTokensCountOfOwner[sessionId][owner];
        uint256 currIndex = gs.stakedTokenIndex[sessionId][tokenId];
        uint256 lastToken = gs.stakedTokens[sessionId][owner][currStaked];
        //TODO add another mapping like dark forest for staker
        require(
            currIndex <= currStaked &&
                gs.stakedTokens[sessionId][owner][currIndex] == tokenId,
            "GOFPFacet._removeTokenFromEnumeration: Token wasn't staked by the given owner"
        );
        //swapping last element with element at given index
        gs.stakedTokens[sessionId][owner][currIndex] = lastToken;
        //updating last token's index
        gs.stakedTokenIndex[sessionId][lastToken] = currIndex;
        //deleting old lastToken
        delete gs.stakedTokens[sessionId][owner][currStaked];
        //updating staked count
        gs.stakedTokensCountOfOwner[sessionId][owner]--;
    }

    // ReentrancyGuard needed
    function stakeTokensIntoSession(
        uint256 sessionID,
        uint256[] calldata tokenIDs
    ) external {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.setSessionChoosingActive: Invalid session ID"
        );

        IERC20 paymentToken = IERC20(
            gs.sessionById[sessionID].paymentTokenAddress
        );
        uint256 paymentAmount = gs.sessionById[sessionID].paymentAmount *
            tokenIDs.length;
        paymentToken.transferFrom(msg.sender, address(this), paymentAmount);

        // The first stage path has not been set. (game has not started)
        require(gs.sessionStagePath[sessionID][0] == 0);
        // Session is active
        require(gs.sessionById[gs.numSessions].isActive);

        IERC721 token = IERC721(gs.sessionById[sessionID].playerTokenAddress);
        for (uint256 i = 0; i < tokenIDs.length; i++) {
            token.safeTransferFrom(msg.sender, address(this), tokenIDs[i]);
            //adding to enumeration
        }
    }

    // ReentrancyGuard needed
    function unstakeTokensFromSession(
        uint256 sessionID,
        uint256[] calldata tokenIDs
    ) external {
        //TODO add checks that needed
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        IERC721 token = IERC721(gs.sessionById[sessionID].playerTokenAddress);
        for (uint256 i = 0; i < tokenIDs.length; i++) {
            _removeTokenFromEnumeration(sessionID, msg.sender, tokenIDs[i]);
            token.safeTransferFrom(address(this), msg.sender, tokenIDs[i]);
        }
    }
}
