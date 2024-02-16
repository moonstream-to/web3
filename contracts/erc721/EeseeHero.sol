// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/moonstream-to/moonbound
 */

pragma solidity ^0.8.9;

import "@openzeppelin-contracts/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import {ITerminus} from "../interfaces/ITerminus.sol";
import {ReentrancyGuard} from "@openzeppelin-contracts/contracts/security/ReentrancyGuard.sol";

contract EeseeHero is ERC721Enumerable, ReentrancyGuard {
    address public adminTerminusAddress;
    uint256 public adminTerminusPoolID;
    string public metadataBaseURI;

    event MetadataBaseUriUpdated(string uri);

    // Contract must be deployed along with:
    // 1. terminusAddress specifying a Terminus contract which will host the admin badge for the Initiates contract
    // 2. terminusPoolID specifying the pool ID of the admin badge for the Initiates contract
    // 3. metadataBaseURI specifying the base URI for the metadata of the Initiates
    constructor(
        address terminusAddress,
        uint256 terminusPoolID,
        string memory _metadataBaseURI
    ) ERC721("Eesee Hero", "EESH") {
        adminTerminusAddress = terminusAddress;
        adminTerminusPoolID = terminusPoolID;
        metadataBaseURI = _metadataBaseURI;
    }

    function _baseURI() internal view override returns (string memory) {
        return metadataBaseURI;
    }

    function isAdmin(address account) public view returns (bool) {
        ITerminus adminTerminus = ITerminus(adminTerminusAddress);
        return adminTerminus.balanceOf(account, adminTerminusPoolID) > 0;
    }

    function setBaseURI(string memory newURI) public {
        require(
            isAdmin(msg.sender),
            "Eesee Hero.setBaseURI: caller is not admin"
        );
        metadataBaseURI = newURI;

        emit MetadataBaseUriUpdated(newURI);
    }

    function mint(address to, uint256 quantity) external {
        require(isAdmin(msg.sender), "Eesee Hero.mint: caller is not admin");
        _mint(to, quantity);
    }

    function safeMint(
        address to,
        uint256 quantity,
        bytes memory _data
    ) external nonReentrant {
        require(
            isAdmin(msg.sender),
            "Eesee Hero.safeMint: caller is not admin"
        );
        _safeMint(to, quantity, _data);
    }
}
