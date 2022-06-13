// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 */

pragma solidity ^0.8.9;

import "@moonstream/contracts/terminus/TerminusFacet.sol";
import "@moonstream/contracts/terminus/TerminusPermissions.sol";
import "@openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin-contracts/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin-contracts/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin-contracts/contracts/utils/cryptography/SignatureChecker.sol";

import "./LibDropperV2.sol";
import "../interfaces/IERC721Mint.sol";
import "../diamond/security/DiamondReentrancyGuard.sol";
import "../diamond/libraries/LibSignatures.sol";

/**
 * @title Moonstream DropperV2
 * @author Moonstream Engineering (engineering@moonstream.to)
 * @notice This contract manages drops for ERC20, ERC1155, and ERC721 tokens.
 */
contract DropperV2Facet is
    IERC721Receiver,
    ERC1155Holder,
    TerminusPermissions,
    DiamondReentrancyGuard
{
    event Claimed(
        uint256 indexed dropId,
        address indexed claimant,
        uint256 requestID,
        uint256 amount
    );
    event DropCreated(
        uint256 dropId,
        uint256 indexed tokenType,
        address indexed tokenAddress,
        uint256 indexed tokenId,
        uint256 amount
    );
    event DropStatusChanged(uint256 indexed dropId, bool status);
    event DropSignerChanged(uint256 indexed dropId, address signer);
    event Withdrawal(
        address recipient,
        uint256 indexed tokenType,
        address indexed tokenAddress,
        uint256 indexed tokenId,
        uint256 amount
    );

    modifier onlyTerminusAdmin() {
        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();
        require(
            _holdsPoolToken(
                ds.TerminusAdminContractAddress,
                ds.TerminusAdminPoolID,
                1
            ),
            "DropperFacet.onlyTerminusAdmin: Sender does not hold administrator token"
        );

        // Execute modified function
        _;
    }

    function onERC721Received(
        address operator,
        address from,
        uint256 tokenId,
        bytes calldata data
    ) external returns (bytes4) {
        return IERC721Receiver.onERC721Received.selector;
    }

    function createDrop(
        uint256 tokenType,
        address tokenAddress,
        uint256 tokenId,
        uint256 amount,
        uint256 _maxClaimable
    ) external onlyTerminusAdmin returns (uint256) {
        require(
            tokenType == ERC20_TYPE ||
                tokenType == ERC721_TYPE ||
                tokenType == ERC1155_TYPE ||
                tokenType == TERMINUS_MINTABLE_TYPE ||
                tokenType == ERC721_MINTABLE_TYPE,
            "DropperV2: createDrop -- Unknown token type"
        );

        require(
            amount != 0,
            "DropperV2: createDrop -- Amount must be greater than 0"
        );

        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();

        ds.NumDrops++;

        DroppableToken memory tokenMetadata;
        tokenMetadata.tokenType = tokenType;
        tokenMetadata.tokenAddress = tokenAddress;
        tokenMetadata.tokenId = tokenId;
        tokenMetadata.amount = amount;
        ds.DropToken[ds.NumDrops] = tokenMetadata;
        emit DropCreated(ds.NumDrops, tokenType, tokenAddress, tokenId, amount);

        ds.IsDropActive[ds.NumDrops] = true;
        emit DropStatusChanged(ds.NumDrops, true);

        ds.MaxClaimable[ds.NumDrops] = _maxClaimable;

        return ds.NumDrops;
    }

    function numDrops() external view returns (uint256) {
        return LibDropperV2.dropperV2Storage().NumDrops;
    }

    function getDrop(uint256 dropId)
        external
        view
        returns (DroppableToken memory)
    {
        return LibDropperV2.dropperV2Storage().DropToken[dropId];
    }

    function setDropStatus(uint256 dropId, bool status)
        external
        onlyTerminusAdmin
    {
        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();
        ds.IsDropActive[dropId] = status;
        emit DropStatusChanged(dropId, status);
    }

    function dropStatus(uint256 dropId) external view returns (bool) {
        return LibDropperV2.dropperV2Storage().IsDropActive[dropId];
    }

    function setSignerForDrop(uint256 dropId, address signer)
        public
        onlyTerminusAdmin
    {
        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();
        ds.DropSigner[dropId] = signer;
        emit DropSignerChanged(dropId, signer);
    }

    function getSignerForDrop(uint256 dropId) external view returns (address) {
        return LibDropperV2.dropperV2Storage().DropSigner[dropId];
    }

    function maxClaimable(uint256 dropId) external view returns (uint256) {
        return LibDropperV2.dropperV2Storage().MaxClaimable[dropId];
    }

    function getAmountClaimed(address claimant, uint256 dropId)
        external
        view
        returns (uint256)
    {
        return LibDropperV2.dropperV2Storage().AmountClaimed[claimant][dropId];
    }

    function claimMessageHash(
        uint256 requestID,
        uint256 dropId,
        address claimant,
        uint256 blockDeadline,
        uint256 amount
    ) public view returns (bytes32) {
        bytes32 structHash = keccak256(
            abi.encode(
                keccak256(
                    "ClaimPayload(uint256 requestID,uint256 dropId,address claimant,uint256 blockDeadline,uint256 amount)"
                ),
                requestID,
                dropId,
                claimant,
                blockDeadline,
                amount
            )
        );
        bytes32 digest = LibSignatures._hashTypedDataV4(structHash);
        return digest;
    }

    function claim(
        uint256 requestID,
        uint256 dropId,
        uint256 blockDeadline,
        uint256 amount,
        bytes memory signature
    ) external diamondNonReentrant {
        require(
            block.number <= blockDeadline,
            "DropperV2: claim -- Block deadline exceeded."
        );

        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();

        require(
            ds.AmountClaimed[msg.sender][dropId] + amount <=
                ds.MaxClaimable[dropId],
            "DropperV2: claim -- Claimant would exceed the maximum claimable number of tokens for this drop."
        );

        bytes32 hash = claimMessageHash(
            requestID,
            dropId,
            msg.sender,
            blockDeadline,
            amount
        );
        require(
            SignatureChecker.isValidSignatureNow(
                ds.DropSigner[dropId],
                hash,
                signature
            ),
            "DropperV2: claim -- Invalid signer for claim."
        );

        DroppableToken memory claimToken = ds.DropToken[dropId];

        if (amount == 0) {
            amount = claimToken.amount;
        }

        if (claimToken.tokenType == ERC20_TYPE) {
            IERC20 erc20Contract = IERC20(claimToken.tokenAddress);
            erc20Contract.transfer(msg.sender, amount);
        } else if (claimToken.tokenType == ERC721_TYPE) {
            IERC721 erc721Contract = IERC721(claimToken.tokenAddress);
            erc721Contract.safeTransferFrom(
                address(this),
                msg.sender,
                claimToken.tokenId,
                ""
            );
        } else if (claimToken.tokenType == ERC1155_TYPE) {
            IERC1155 erc1155Contract = IERC1155(claimToken.tokenAddress);
            erc1155Contract.safeTransferFrom(
                address(this),
                msg.sender,
                claimToken.tokenId,
                amount,
                ""
            );
        } else if (claimToken.tokenType == TERMINUS_MINTABLE_TYPE) {
            TerminusFacet terminusFacetContract = TerminusFacet(
                claimToken.tokenAddress
            );
            terminusFacetContract.mint(
                msg.sender,
                claimToken.tokenId,
                amount,
                ""
            );
        } else if (claimToken.tokenType == ERC721_MINTABLE_TYPE) {
            IERC721Mint erc721MintableContract = IERC721Mint(
                claimToken.tokenAddress
            );
            uint256 numTokens = erc721MintableContract.totalSupply();
            erc721MintableContract.mint(msg.sender, numTokens + 1);
        } else {
            revert("Dropper -- claim: Unknown token type in claim");
        }

        ds.AmountClaimed[msg.sender][dropId] += amount;

        emit Claimed(dropId, msg.sender, requestID, amount);
    }

    function withdrawERC20(address tokenAddress, uint256 amount)
        public
        onlyTerminusAdmin
    {
        IERC20 erc20Contract = IERC20(tokenAddress);
        erc20Contract.transfer(msg.sender, amount);
        emit Withdrawal(msg.sender, ERC20_TYPE, tokenAddress, 0, amount);
    }

    function withdrawERC721(address tokenAddress, uint256 tokenId)
        public
        onlyTerminusAdmin
    {
        IERC721 erc721Contract = IERC721(tokenAddress);
        erc721Contract.safeTransferFrom(address(this), msg.sender, tokenId, "");
        emit Withdrawal(msg.sender, ERC721_TYPE, tokenAddress, tokenId, 1);
    }

    function withdrawERC1155(
        address tokenAddress,
        uint256 tokenId,
        uint256 amount
    ) public onlyTerminusAdmin {
        IERC1155 erc1155Contract = IERC1155(tokenAddress);
        erc1155Contract.safeTransferFrom(
            address(this),
            msg.sender,
            tokenId,
            amount,
            ""
        );
        emit Withdrawal(
            msg.sender,
            ERC1155_TYPE,
            tokenAddress,
            tokenId,
            amount
        );
    }

    function surrenderPoolControl(
        uint256 poolId,
        address terminusAddress,
        address newPoolController
    ) public onlyTerminusAdmin {
        TerminusFacet terminusFacetContract = TerminusFacet(terminusAddress);
        terminusFacetContract.setPoolController(poolId, newPoolController);
    }

    function dropUri(uint256 dropId) public view returns (string memory) {
        return LibDropperV2.dropperV2Storage().DropURI[dropId];
    }

    function setDropUri(uint256 dropId, string memory uri)
        external
        onlyTerminusAdmin
    {
        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();

        ds.DropURI[dropId] = uri;
    }
}
