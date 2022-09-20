// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/engine
 */

pragma solidity ^0.8.0;

import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import {TerminusPermissions} from "@moonstream/contracts/terminus/TerminusPermissions.sol";
import "../../diamond/libraries/LibDiamond.sol";

// Why not to make struct Session and have only one mapping? uint => Session
// Reward as terminus token and use crafting ?
//

struct Session {
    address playerTokenAddress;
    address paymentTokenAddress;
    uint256 paymentAmount;
    bool isActive;
    string URI;
    uint256[] stages;
}

library LibGOFP {
    bytes32 constant STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.mechanics.GardenOfForkingPaths");

    struct GOFPStorage {
        address AdminTerminusAddress;
        uint256 AdminTerminusPoolID;
        uint256 numSessions;
        // session -> stage -> correct path index
        mapping(uint256 => mapping(uint256 => uint256)) path;
    }

    function gofpStorage() internal pure returns (GOFPStorage storage gs) {
        bytes32 position = STORAGE_POSITION;
        assembly {
            gs.slot := position
        }
    }
}

contract GOFPFacet is ERC1155Holder, TerminusPermissions {
    modifier onlyGameMaster() {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            _holdsPoolToken(gs.AdminTerminusAddress, gs.AdminTerminusPoolID, 1),
            "GOFPFacet.onlyGameMaster: The address is not an authorized game master"
        );
        _;
    }

    event SessionCreated(Session);

    // When session is activated, this fires:
    // SessionActivated(<id>, true)
    // When session is deactivated, this fires:
    // SessionActivated(<id>, false)
    event SessionActivated(uint256 indexed sessionID, bool active);

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
        returns (
            address playerTokenAddress,
            address paymentTokenAddress,
            uint256 paymentamount,
            bool isActive,
            string memory uri,
            uint256[] memory stages,
            uint256[] memory correctPath
        )
    {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        playerTokenAddress = gs.SessionPlayerTokenAddress[sessionID];
        paymentTokenAddress = gs.SessionPaymentTokenAddress[sessionID];
        paymentamount = gs.SessionPaymentAmount[sessionID];
        isActive = gs.SessionIsActive[sessionID];
        uri = gs.SessionURI[sessionID];
        stages = gs.SessionStages[sessionID];
        correctPath = new uint256[](stages.length);
        for (uint256 i = 0; i < stages.length; i++) {
            correctPath[i] = gs.SessionPath[sessionID][i];
        }
    }

    function adminTerminusInfo() external view returns (address, uint256) {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        return (gs.AdminTerminusAddress, gs.AdminTerminusPoolID);
    }

    function numSessions() external view returns (uint256) {
        return LibGOFP.gofpStorage().NumSessions;
    }

    function createSession(
        address playerTokenAddress,
        address paymentTokenAddress,
        uint256 paymentAmount,
        string memory uri,
        uint256[] memory stages,
        bool active
    ) external onlyGameMaster {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        gs.NumSessions++;
        require(
            gs.SessionPlayerTokenAddress[gs.NumSessions] == address(0),
            "GOFPFacet.createSession: Session already registered"
        );
        gs.SessionPlayerTokenAddress[gs.NumSessions] = playerTokenAddress;
        gs.SessionPaymentTokenAddress[gs.NumSessions] = paymentTokenAddress;
        gs.SessionPaymentAmount[gs.NumSessions] = paymentAmount;
        gs.SessionURI[gs.NumSessions] = uri;
        gs.SessionStages[gs.NumSessions] = stages;
        gs.SessionIsActive[gs.NumSessions] = active;

        emit SessionCreated(
            gs.NumSessions,
            playerTokenAddress,
            paymentTokenAddress,
            paymentAmount,
            uri
        );
    }

    function setSessionActive(uint256 sessionID, bool active)
        external
        onlyGameMaster
    {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.NumSessions,
            "GOFPFacet.setSessionActive: Invalid session ID"
        );
        gs.SessionIsActive[sessionID] = active;
        emit SessionActivated(sessionID, active);
    }

    function registerPath(
        uint256 sessionID,
        uint256 stage,
        uint256 path
    ) external onlyGameMaster {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.NumSessions,
            "GOFPFacet.registerPath: Invalid session"
        );
        require(
            stage < gs.SessionStages[sessionID].length,
            "GOFPFacet.registerPath: Invalid stage"
        );
        // Paths are 1-indexed to avoid possible confusion involving default value of 0
        require(
            path >= 1 && path <= gs.SessionStages[sessionID][stage],
            "GOFPFacet.registerPath: Invalid path"
        );
        // We use the default value of 0 as a guard to check that path has not already been set for that
        // stage. No changes allowed for a given stage after the path was already chosen.
        require(
            gs.SessionPath[sessionID][stage] == 0,
            "GOFPFacet.registerPath: Path has already been chosen for that stage"
        );
        gs.SessionPath[sessionID][stage] = path;
        emit PathRegistered(sessionID, stage, path);
    }

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata _data
    ) public virtual returns (bytes4) {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();

        // _data is expected to be an encoded uint256 representing the session ID into which the NFT
        // should be staked.
        uint256 sessionID;
        (sessionID) = abi.decode(_data, (uint256));
        require(
            sessionID <= gs.NumSessions,
            "GOFPFacet.onERC721Received: Invalid session"
        );

        // Note: msg.sender is always the ERC721 contract address in onERC721Received:
        // https://eips.ethereum.org/EIPS/eip-721
        require(
            msg.sender == gs.SessionPlayerTokenAddress[sessionID],
            "GOFPFacet.onERC721Received: Invalid ERC721 contract for session"
        );

        return this.onERC721Received.selector;
    }
}
