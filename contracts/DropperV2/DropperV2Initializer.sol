// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 *
 * Initializer for Terminus contract. Used when mounting a new TerminusFacet onto its diamond proxy.
 */

pragma solidity ^0.8.9;

import "./LibDropperV2.sol";
import "../diamond/libraries/LibSignatures.sol";

contract DropperV2Initializer {
    function init(
        address terminusAdminContractAddress,
        uint256 terminusAdminPoolID
    ) external {
        // Set up server side signing parameters for EIP712
        LibSignatures._setEIP712Parameters("Moonstream Dropper", "2.0.0");

        // Initialize Terminus administration information
        LibDropperV2.DropperV2Storage storage ds = LibDropperV2
            .dropperV2Storage();

        ds.TerminusAdminContractAddress = terminusAdminContractAddress;
        ds.TerminusAdminPoolID = terminusAdminPoolID;
    }
}
