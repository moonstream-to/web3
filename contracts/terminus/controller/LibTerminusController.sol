// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 *
 */

pragma solidity ^0.8.9;

struct TerminusPool {
    address terminusAddress;
    uint256 poolId;
}

library LibTerminusController {
    bytes32 constant TERMINUS_CONTROLLER_STORAGE_POSITION =
        keccak256("moonstreamdao.eth.storage.terminus.controller");

    struct TerminusControllerStorage {
        address terminusAddress;
        TerminusPool terminusMainAdminPool;
        mapping(uint256 => TerminusPool) poolController;
    }

    function terminusControllerStorage()
        internal
        pure
        returns (TerminusControllerStorage storage es)
    {
        bytes32 position = TERMINUS_CONTROLLER_STORAGE_POSITION;
        assembly {
            es.slot := position
        }
    }
}
