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

import "./LibDropper.sol";
import "../interfaces/IERC721Mint.sol";
import "../diamond/security/DiamondReentrancyGuard.sol";
import "../diamond/libraries/LibSignatures.sol";

/**
 * @title Moonstream Dropper
 * @author Moonstream Engineering (engineering@moonstream.to)
 * @notice This contract manages drops for ERC20, ERC1155, and ERC721 tokens.
 */
contract DropperFacet is
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

    function erc20_type() external pure returns (uint256) {
        return ERC20_TYPE;
    }

    function erc721_type() external pure returns (uint256) {
        return ERC721_TYPE;
    }

    function erc1155_type() external pure returns (uint256) {
        return ERC1155_TYPE;
    }

    function terminus_mintable_type() external pure returns (uint256) {
        return TERMINUS_MINTABLE_TYPE;
    }

    function erc721_mintable_type() external pure returns (uint256) {
        return ERC721_MINTABLE_TYPE;
    }

    modifier onlyTerminusAdmin() {
        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();
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

    function init(
        address terminusAdminContractAddress,
        uint256 terminusAdminPoolID
    ) external {
        // Set up server side signing parameters for EIP712
        LibSignatures._setEIP712Parameters("Moonstream Dropper", "0.2.0");

        // Initialize Terminus administration information
        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();

        ds.TerminusAdminContractAddress = terminusAdminContractAddress;
        ds.TerminusAdminPoolID = terminusAdminPoolID;
    }

    function dropperVersion()
        public
        view
        returns (string memory, string memory)
    {
        LibSignatures.SignaturesStorage storage ss = LibSignatures
            .signaturesStorage();
        return (ss.name, ss.version);
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
            "Dropper: createDrop -- Unknown token type"
        );

        require(
            amount != 0,
            "Dropper: createDrop -- Amount must be greater than 0"
        );

        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();

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
        return LibDropper.dropperStorage().NumDrops;
    }

    function getDrop(uint256 dropId)
        external
        view
        returns (DroppableToken memory)
    {
        return LibDropper.dropperStorage().DropToken[dropId];
    }

    function setDropStatus(uint256 dropId, bool status)
        external
        onlyTerminusAdmin
    {
        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();
        ds.IsDropActive[dropId] = status;
        emit DropStatusChanged(dropId, status);
    }

    function dropStatus(uint256 dropId) external view returns (bool) {
        return LibDropper.dropperStorage().IsDropActive[dropId];
    }

    function setSignerForDrop(uint256 dropId, address signer)
        public
        onlyTerminusAdmin
    {
        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();
        ds.DropSigner[dropId] = signer;
        emit DropSignerChanged(dropId, signer);
    }

    function getSignerForDrop(uint256 dropId) external view returns (address) {
        return LibDropper.dropperStorage().DropSigner[dropId];
    }

    function maxClaimable(uint256 dropId) external view returns (uint256) {
        return LibDropper.dropperStorage().MaxClaimable[dropId];
    }

    function getAmountClaimed(address claimant, uint256 dropId)
        external
        view
        returns (uint256)
    {
        return LibDropper.dropperStorage().AmountClaimed[claimant][dropId];
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
            "Dropper: claim -- Block deadline exceeded."
        );

        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();

        require(
            ds.AmountClaimed[msg.sender][dropId] + amount <=
                ds.MaxClaimable[dropId],
            "Dropper: claim -- Claimant would exceed the maximum claimable number of tokens for this drop."
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
            "Dropper: claim -- Invalid signer for claim."
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
        return LibDropper.dropperStorage().DropURI[dropId];
    }

    function setDropUri(uint256 dropId, string memory uri)
        external
        onlyTerminusAdmin
    {
        LibDropper.DropperStorage storage ds = LibDropper.dropperStorage();

        ds.DropURI[dropId] = uri;
    }
}
