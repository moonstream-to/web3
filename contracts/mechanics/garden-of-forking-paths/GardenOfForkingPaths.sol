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
import "../../diamond/security/DiamondReentrancyGuard.sol";

struct Session {
    address playerTokenAddress;
    address paymentTokenAddress;
    uint256 paymentAmount;
    bool isActive; // active -> stake if ok,  cannot unstake
    bool isChoosingActive; // if active -> players can choose path in current stage
    string URI;
    uint256[] stages;
}

library LibGOFP {
    bytes32 constant STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.mechanics.GardenOfForkingPaths");

    /**
    All implicit arrays (implemented with maps) are 1-indexed. This applies to:
    - sessions
    - stages
    - paths

    This helps us avoid any confusion that stems from 0 being the default value for uint256.
    Applying this condition uniformly to all mappings avoids confusion from having to remember which
    implicit arrays are 0-indexed and which are 1-indexed.
     */
    struct GOFPStorage {
        address AdminTerminusAddress;
        uint256 AdminTerminusPoolID;
        uint256 numSessions;
        mapping(uint256 => Session) sessionById;
        // session => stage => correct path for that stage
        mapping(uint256 => mapping(uint256 => uint256)) sessionStagePath;
        // nftAddress => tokenId => sessionId
        mapping(address => mapping(uint256 => uint256)) stakedTokenSession;
        // nftAddress => tokenId => owner
        mapping(address => mapping(uint256 => address)) stakedTokenOwner;
        // session => owner => numTokensStaked
        mapping(uint256 => mapping(address => uint256)) numTokensStakedByOwnerInSession;
        // sessionId => tokenId => index in tokensStakedByOwnerInSession
        mapping(uint256 => mapping(uint256 => uint256)) stakedTokenIndex;
        // session => owner => index => tokenID
        // The index refers to the tokens that the given owner has staked into the given sessions.
        // The index starts from 1.
        mapping(uint256 => mapping(address => mapping(uint256 => uint256))) tokensStakedByOwnerInSession;
        // session => tokenID => stage => chosenPath
        // This mapping tracks the path chosen by each eligible NFT in a session at each stage
        mapping(uint256 => mapping(uint256 => mapping(uint256 => uint256))) pathChoices;
    }

    function gofpStorage() internal pure returns (GOFPStorage storage gs) {
        bytes32 position = STORAGE_POSITION;
        assembly {
            gs.slot := position
        }
    }
}

/**
The GOFPFacet is a smart contract that can either be used standalone or as part of an EIP2535 Diamond
proxy contract.

It implements the Garden of Forking Paths, a multiplayer choose your own adventure game mechanic.

Garden of Forking Paths is run in sessions. Each session consists of a given number of stages. Each
stage consists of a given number of paths.

Everything on the Garden of Forking Paths is 1-indexed.

There are two kinds of accounts that can interact with the Garden of Forking Paths:
1. Game Masters
2. Players

Game Masters are accounts which hold an admin badge as defined by LibGOFP.AdminTerminusAddress and
LibGOFP.AdminTerminusPoolID. The badge is expected to be a Terminus badge (non-transferable token).

Game Masters can:
- [x] Create sessions
- [x] Mark sessions as active or inactive
- [x] Mark sessions as active or inactive for the purposes of NFTs choosing a path in a the current stage
- [x] Register the correct path for the current stage
- [ ] Update the metadata for a session
- [ ] Set a reward (Terminus token mint) for NFT holders who make a choice with an NFT in each stage
- [ ] Rescue NFTs and send them to a specified address

Players can:
- [x] Stake their NFTs into a sesssion if the correct first stage path has not been chosen
- [x] Pay to stake their NFTs
- [x] Unstake their NFTs from a session if the session is inactive
- [x] Have one of their NFTs choose a path in the current stage PROVIDED THAT the current stage is the first
stage OR that the NFT chose the correct path in the previous stage
- [ ] Collect their reward (Terminus token mint) for making a choice with an NFT in the current stage of a session

Anybody can:
- [ ] View details of a session
- [ ] View whether a session is active
- [ ] View whether a session is open for NFT choices
- [ ] View the correct path for a given stage
- [ ] View how many tokens a given owner has staked into a given session
- [ ] View the token ID of the <n>th token that a given owner has staked into a given session for any valid
    value of n
 */
contract GOFPFacet is
    ERC721Holder,
    ERC1155Holder,
    TerminusPermissions,
    DiamondReentrancyGuard
{
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
    event PathChosen(
        uint256 indexed sessionID,
        uint256 indexed tokenID,
        uint256 indexed stage,
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

    /**
    Creates a Garden of Forking Paths session. The session is configured with:
    - playerTokenAddress - this is the address of ERC721 tokens that can participate in the session
    - paymentTokenAddress - this is the address of the ERC20 token that each NFT must pay to enter the session
    - paymentAmount - this is the amount of the payment token that each NFT must pay to enter the session
    - isActive - this determines if the session is active as soon as it is created or not
    - isChoosingActive - this determines if NFTs can choose a path in the current stage or not, and is true
      by default when the session is created
    - URI - metadata URI describing the session
    - stages - an array describing the number of path choices at each stage of the session
     */
    function createSession(
        address playerTokenAddress,
        address paymentTokenAddress,
        uint256 paymentAmount,
        bool isActive,
        string memory URI,
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

        require(
            paymentTokenAddress != address(0) || paymentAmount == 0,
            "GOFPFacet.createSession: If paymentTokenAddress is the 0 address, paymentAmount should also be 0"
        );

        gs.sessionById[gs.numSessions] = Session({
            playerTokenAddress: playerTokenAddress,
            paymentTokenAddress: paymentTokenAddress,
            paymentAmount: paymentAmount,
            isActive: isActive,
            isChoosingActive: true,
            URI: URI,
            stages: stages
        });
        emit SessionCreated(
            gs.numSessions,
            playerTokenAddress,
            paymentTokenAddress,
            paymentAmount,
            URI,
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
        require(
            stage > 0,
            "GOFPFacet.getCorrectPathForStage: Stages are 1-indexed, 0 is not a valid stage"
        );
        return LibGOFP.gofpStorage().sessionStagePath[sessionID][stage];
    }

    function setCorrectPathForStage(
        uint256 sessionID,
        uint256 stage,
        uint256 path,
        bool setIsChoosingActive
    ) external onlyGameMaster {
        require(
            stage > 0,
            "GOFPFacet.setCorrectPathForStage: Stages are 1-indexed, 0 is not a valid stage"
        );
        uint256 stageIndex = stage - 1;
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.setCorrectPathForStage: Invalid session"
        );
        require(
            stageIndex < gs.sessionById[sessionID].stages.length,
            "GOFPFacet.setCorrectPathForStage: Invalid stage"
        );
        require(
            !gs.sessionById[sessionID].isChoosingActive,
            "GOFPFacet.setCorrectPathForStage: Deactivate isChoosingActive before setting the correct path"
        );
        // Paths are 1-indexed to avoid possible confusion involving default value of 0
        require(
            path >= 1 && path <= gs.sessionById[sessionID].stages[stageIndex],
            "GOFPFacet.setCorrectPathForStage: Invalid path"
        );
        // We use the default value of 0 as a guard to check that path has not already been set for that
        // stage. No changes allowed for a given stage after the path was already chosen.
        require(
            gs.sessionStagePath[sessionID][stage] == 0,
            "GOFPFacet.setCorrectPathForStage: Path has already been chosen for that stage"
        );
        // You cannot set the path for a stage if the path for its previous stage has not been previously
        // set.
        // We use the stageIndex to access the path because stageIndex = stage - 1. This is just a
        // convenience. It would be more correct to access the "stage - 1" key in the mapping.
        require(
            stage <= 1 || gs.sessionStagePath[sessionID][stageIndex] != 0,
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

    /**
    For a given NFT, specified by the `nftAddress` and `tokenID`, this view function returns:
    1. The sessionId of the session into which the NFT is staked
    2. The address of the staker

    If the token is not currently staked in the Garden of Forking Paths contract, this method returns
    0 for the sessionId and the 0 address as the staker.
     */
    function getStakedTokenInfo(address nftAddress, uint256 tokenID)
        external
        view
        returns (uint256, address)
    {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        return (
            gs.stakedTokenSession[nftAddress][tokenID],
            gs.stakedTokenOwner[nftAddress][tokenID]
        );
    }

    function numTokensStakedIntoSession(uint256 sessionID, address staker)
        external
        view
        returns (uint256)
    {
        return
            LibGOFP.gofpStorage().numTokensStakedByOwnerInSession[sessionID][
                staker
            ];
    }

    function tokenOfStakerInSessionByIndex(
        uint256 sessionID,
        address staker,
        uint256 index
    ) external view returns (uint256) {
        return
            LibGOFP.gofpStorage().tokensStakedByOwnerInSession[sessionID][
                staker
            ][index];
    }

    /**
    Returns the path chosen by the given tokenID in the given session and stage.

    Recall: sessions and stages are 1-indexed.
     */
    function getPathChoice(
        uint256 sessionID,
        uint256 tokenID,
        uint256 stage
    ) external view returns (uint256) {
        return LibGOFP.gofpStorage().pathChoices[sessionID][tokenID][stage];
    }

    function _addTokenToEnumeration(
        uint256 sessionId,
        address owner,
        address nftAddress,
        uint256 tokenId
    ) internal {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();

        require(
            gs.stakedTokenSession[nftAddress][tokenId] == 0,
            "GOFPFacet._addTokenToEnumeration: Token is already associated with a session on this contract"
        );
        require(
            gs.stakedTokenOwner[nftAddress][tokenId] == address(0),
            "GOFPFacet._addTokenToEnumeration: Token is already associated with an owner on this contract"
        );
        require(
            gs.stakedTokenIndex[sessionId][tokenId] == 0,
            "GOFPFacet._addTokenToEnumeration: Token was already added to enumeration"
        );

        gs.stakedTokenSession[nftAddress][tokenId] = sessionId;
        gs.stakedTokenOwner[nftAddress][tokenId] = owner;

        uint256 currStaked = gs.numTokensStakedByOwnerInSession[sessionId][
            owner
        ];
        gs.tokensStakedByOwnerInSession[sessionId][owner][
            currStaked + 1
        ] = tokenId;
        gs.stakedTokenIndex[sessionId][tokenId] = currStaked + 1;
        gs.numTokensStakedByOwnerInSession[sessionId][owner]++;
    }

    function _removeTokenFromEnumeration(
        uint256 sessionId,
        address owner,
        address nftAddress,
        uint256 tokenId
    ) internal {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            gs.stakedTokenSession[nftAddress][tokenId] == sessionId,
            "GOFPFacet._removeTokenFromEnumeration: Token is not associated with the given session"
        );
        require(
            gs.stakedTokenOwner[nftAddress][tokenId] == owner,
            "GOFPFacet._removeTokenFromEnumeration: Token is not associated with the given owner"
        );
        require(
            gs.stakedTokenIndex[sessionId][tokenId] != 0,
            "GOFPFacet._removeTokenFromEnumeration: Token wasn't added to enumeration"
        );

        delete gs.stakedTokenSession[nftAddress][tokenId];
        delete gs.stakedTokenOwner[nftAddress][tokenId];

        uint256 currStaked = gs.numTokensStakedByOwnerInSession[sessionId][
            owner
        ];
        uint256 currIndex = gs.stakedTokenIndex[sessionId][tokenId];
        uint256 lastToken = gs.tokensStakedByOwnerInSession[sessionId][owner][
            currStaked
        ];
        require(
            currIndex <= currStaked &&
                gs.tokensStakedByOwnerInSession[sessionId][owner][currIndex] ==
                tokenId,
            "GOFPFacet._removeTokenFromEnumeration: Token wasn't staked by the given owner"
        );
        //swapping last element with element at given index
        gs.tokensStakedByOwnerInSession[sessionId][owner][
            currIndex
        ] = lastToken;
        //updating last token's index
        gs.stakedTokenIndex[sessionId][lastToken] = currIndex;
        //deleting old lastToken
        delete gs.tokensStakedByOwnerInSession[sessionId][owner][currStaked];
        //updating staked count
        gs.numTokensStakedByOwnerInSession[sessionId][owner]--;
    }

    function stakeTokensIntoSession(
        uint256 sessionID,
        uint256[] calldata tokenIDs
    ) external diamondNonReentrant {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.stakeTokensIntoSession: Invalid session ID"
        );

        address paymentTokenAddress = gs
            .sessionById[sessionID]
            .paymentTokenAddress;
        if (paymentTokenAddress != address(0)) {
            IERC20 paymentToken = IERC20(paymentTokenAddress);
            uint256 paymentAmount = gs.sessionById[sessionID].paymentAmount *
                tokenIDs.length;
            bool paymentSuccessful = paymentToken.transferFrom(
                msg.sender,
                address(this),
                paymentAmount
            );
            require(
                paymentSuccessful,
                "GOFPFacet.stakeTokensIntoSession: Session requires payment but payment was unsuccessful"
            );
        }

        require(
            gs.sessionById[gs.numSessions].isActive,
            "GOFPFacet.stakeTokensIntoSession: Cannot stake tokens into inactive session"
        );

        require(
            gs.sessionStagePath[sessionID][1] == 0,
            "GOFPFacet.stakeTokensIntoSession: The first stage for this session has already been resolved"
        );

        address nftAddress = gs.sessionById[sessionID].playerTokenAddress;
        IERC721 token = IERC721(nftAddress);
        for (uint256 i = 0; i < tokenIDs.length; i++) {
            // TODO(zomglings): Currently, Garden of Forking Paths does not allow even someone who is *approved* to transfer
            // NFTs on behalf of their owners to stake those NFTs into a session.
            // We may want to change this in the future. Perhaps the more correct thing would be to check if the msg.sender
            // was approved by the NFT owner on the ERC721 contract.
            // We should check if approvals are intended to compose transitively on ERC721.
            // Just because person A gives person B approval to transfer ERC721 tokens, doesn't mean they want them to
            // have permission to instigate *another* address with transfer approval to make a transfer.
            require(
                token.ownerOf(tokenIDs[i]) == msg.sender,
                "GOFPFacet.stakeTokensIntoSession: Cannot stake a token into session which is not owned by message sender"
            );
            token.safeTransferFrom(msg.sender, address(this), tokenIDs[i]);
            _addTokenToEnumeration(
                sessionID,
                msg.sender,
                nftAddress,
                tokenIDs[i]
            );
        }
    }

    function unstakeTokensFromSession(
        uint256 sessionID,
        uint256[] calldata tokenIDs
    ) external diamondNonReentrant {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.unstakeTokensFromSession: Invalid session ID"
        );

        Session storage session = gs.sessionById[sessionID];
        require(
            !session.isActive,
            "GOFPFacet.unstakeTokensFromSession: Cannot unstake from active session"
        );
        address nftAddress = session.playerTokenAddress;
        IERC721 token = IERC721(nftAddress);
        for (uint256 i = 0; i < tokenIDs.length; i++) {
            _removeTokenFromEnumeration(
                sessionID,
                msg.sender,
                nftAddress,
                tokenIDs[i]
            );
            token.safeTransferFrom(address(this), msg.sender, tokenIDs[i]);
        }
    }

    /**
    Returns the number of the current stage.
     */
    function getCurrentStage(uint256 sessionID)
        external
        view
        returns (uint256)
    {
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();
        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.getCurrentStage: Invalid session ID"
        );

        Session storage session = gs.sessionById[sessionID];

        uint256 lastStage = 0;

        for (uint256 i = 1; i <= session.stages.length; i++) {
            if (gs.sessionStagePath[sessionID][i] > 0) {
                lastStage = i;
            } else {
                break;
            }
        }

        return lastStage + 1;
    }

    /**
    For the current stage of the session with the given sessionID, a player may make a choice of paths
    for each of their tokenIDs.

    The tokenIDs array is expected to be the same length as the paths array.

    A choice may only be made if choosing is currently active for the given session.

    If the current stage is not the first stage, it is expected that each of the tokens specified by
    tokenIDs made the correct choice in the previous stage.
     */
    function chooseCurrentStagePaths(
        uint256 sessionID,
        uint256[] calldata tokenIDs,
        uint256[] calldata paths
    ) external {
        require(
            tokenIDs.length == paths.length,
            "GOFPFacet.chooseCurrentStagePaths: tokenIDs and paths arrays must be of the same length"
        );
        LibGOFP.GOFPStorage storage gs = LibGOFP.gofpStorage();

        require(
            sessionID <= gs.numSessions,
            "GOFPFacet.chooseCurrentStagePaths: Invalid session ID"
        );

        Session storage session = gs.sessionById[sessionID];
        // This prevents players from claiming rewards for path choice in inactive sessions.
        // It is a form of protection for game masters - they can shut down all reward claims from the
        // Garden of Forking Paths session my marking that session as inactive.
        require(
            session.isActive,
            "GOFPFacet.chooseCurrentStagePaths: Cannot choose paths in inactive session"
        );
        require(
            session.isChoosingActive,
            "GOFPFacet.chooseCurrentStagePaths: Cannot choose paths in a session for which choosing is not active"
        );

        uint256 i = 0;

        uint256 lastStage = 0;
        uint256 lastStageCorrectPath = 0;

        for (i = 1; i <= session.stages.length; i++) {
            if (gs.sessionStagePath[sessionID][i] > 0) {
                lastStage = i;
                lastStageCorrectPath = gs.sessionStagePath[sessionID][i];
            } else {
                break;
            }
        }

        require(
            lastStage < session.stages.length,
            "GOFPFacet.chooseCurrentStagePaths: This session has ended"
        );

        uint256 currentStage = lastStage + 1;
        // lastStage has no semantic meaning below. It would be more correct to say currentStage - 1.
        // This is just for convenience, saving one subtraction.
        uint256 numPaths = session.stages[lastStage];

        for (i = 0; i < tokenIDs.length; i++) {
            // BEWARE: Setting tokenID and path variables resuls in a "Stack too deep" error message
            // when compiling this contract. Using calldata array arguments restricts the amount of
            // stack variables available to us inside the function body.
            require(
                gs.stakedTokenIndex[sessionID][tokenIDs[i]] > 0,
                "GOFPFacet.chooseCurrentStagePaths: Token not currently staked into session"
            );
            require(
                gs.stakedTokenOwner[session.playerTokenAddress][tokenIDs[i]] ==
                    msg.sender,
                "GOFPFacet.chooseCurrentStagePaths: Message not sent by token owner"
            );
            require(
                (lastStage == 0) ||
                    (gs.pathChoices[sessionID][tokenIDs[i]][lastStage] ==
                        lastStageCorrectPath),
                "GOFPFacet.chooseCurrentStagePaths: Token did not choose correct path in last stage"
            );
            require(
                (paths[i] >= 1) && (paths[i] <= numPaths),
                "GOFPFacet.chooseCurrentStagePaths: Invalid path"
            );
            gs.pathChoices[sessionID][tokenIDs[i]][currentStage] = paths[i];
            emit PathChosen(sessionID, tokenIDs[i], currentStage, paths[i]);
        }
    }
}
