// SPDX-License-Identifier: Apache-2.0

/**
 * Authors: Moonstream Engineering (engineering@moonstream.to)
 * GitHub: https://github.com/bugout-dev/dao
 *
 * This contract stands as a proxy for the Terminus contract
 * with a ability to whitelist operators by using Terminus Pools
 */
import "@openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";
import "../TerminusFacet.sol";
import "../TerminusPermissions.sol";
import "./LibTerminusController.sol";
import "../../TokenDrainerFacet.sol";

pragma solidity ^0.8.9;

// Permissions:
// - Contract owner can change _TERMINUS_MAIN_ADMIN_POOL_ID (+ all other operations?)
// - Holder of _TERMINUS_MAIN_ADMIN_POOL_ID can change poolControllerPoolID, create pool (+ pool operations?)
// - PoolController can: mint/burn + setURI

contract TerminusControllerFacet is TerminusPermissions, TokenDrainerFacet {
    /**
     * @dev Checks if the caller holds the Admin Pool token or PoolController of pool with poolID
     * @param poolId The poolID to check
     */
    modifier onlyPoolController(uint256 poolId) {
        TerminusPool memory pool = LibTerminusController
            .terminusControllerStorage()
            .poolController[poolId];

        TerminusPool memory adminPool = LibTerminusController
            .terminusControllerStorage()
            .terminusMainAdminPool;
        require(
            _holdsPoolToken(adminPool.terminusAddress, adminPool.poolId, 1) ||
                _holdsPoolToken(pool.terminusAddress, pool.poolId, 1),
            "TerminusControllerFacet.onlyPoolController: Sender doens't hold pool controller token"
        );
        _;
    }

    /**
     * @dev Checks if the caller holds the Admin Pool token
     */
    modifier onlyMainAdmin() {
        TerminusPool memory adminPool = LibTerminusController
            .terminusControllerStorage()
            .terminusMainAdminPool;
        require(
            _holdsPoolToken(adminPool.terminusAddress, adminPool.poolId, 1),
            "TerminusControllerFacet.onlyPoolController: Sender doens't hold pool controller token"
        );
        _;
    }

    function initTerminusController(
        address terminusAddress,
        address _TERMINUS_MAIN_ADMIN_POOL_TERMINUS_ADDRESS,
        uint256 _TERMINUS_MAIN_ADMIN_POOL_ID
    ) public {
        LibTerminusController.TerminusControllerStorage
            storage ts = LibTerminusController.terminusControllerStorage();

        ts.terminusMainAdminPool = TerminusPool(
            _TERMINUS_MAIN_ADMIN_POOL_TERMINUS_ADDRESS,
            _TERMINUS_MAIN_ADMIN_POOL_ID
        );
        ts.terminusAddress = terminusAddress;
    }

    function terminusContract() internal view returns (TerminusFacet) {
        return
            TerminusFacet(
                LibTerminusController
                    .terminusControllerStorage()
                    .terminusAddress
            );
    }

    function getTerminusPoolControllerPool(
        uint256 poolId
    ) public view returns (TerminusPool memory) {
        return
            LibTerminusController.terminusControllerStorage().poolController[
                poolId
            ];
    }

    function getTerminusAddress() public view returns (address) {
        return
            LibTerminusController.terminusControllerStorage().terminusAddress;
    }

    function getTerminusMainAdminPoolId()
        public
        view
        returns (TerminusPool memory)
    {
        return
            LibTerminusController
                .terminusControllerStorage()
                .terminusMainAdminPool;
    }

    /**
     * @dev Gives permission to the holder of the  (poolControllerPoolId,terminusAddress)
     * to mint/burn/setURI for the pool with poolId
     */
    function setPoolControlPermissions(
        uint256 poolId,
        address terminusAddress,
        uint256 poolControllerPoolId
    ) public onlyMainAdmin {
        LibTerminusController.terminusControllerStorage().poolController[
            poolId
        ] = TerminusPool(terminusAddress, poolControllerPoolId);
    }

    // PROXY FUNCTIONS:

    /**
     * @dev Sets the controller of the terminus contract
     */
    function setController(address newController) external {
        LibDiamond.enforceIsContractOwner();
        terminusContract().setController(newController);
    }

    function poolMintBatch(
        uint256 id,
        address[] memory toAddresses,
        uint256[] memory amounts
    ) public onlyPoolController(id) {
        terminusContract().poolMintBatch(id, toAddresses, amounts);
    }

    function terminusController() external view returns (address) {
        return terminusContract().terminusController();
    }

    function contractURI() public view returns (string memory) {
        return terminusContract().contractURI();
    }

    function setContractURI(string memory _contractURI) external onlyMainAdmin {
        terminusContract().setContractURI(_contractURI);
    }

    function setURI(
        uint256 poolID,
        string memory poolURI
    ) external onlyPoolController(poolID) {
        terminusContract().setURI(poolID, poolURI);
    }

    function totalPools() external view returns (uint256) {
        return terminusContract().totalPools();
    }

    function setPoolController(
        uint256 poolID,
        address newController
    ) external onlyMainAdmin {
        terminusContract().setPoolController(poolID, newController);
    }

    function terminusPoolController(
        uint256 poolID
    ) external view returns (address) {
        return terminusContract().terminusPoolController(poolID);
    }

    function terminusPoolCapacity(
        uint256 poolID
    ) external view returns (uint256) {
        return terminusContract().terminusPoolCapacity(poolID);
    }

    function terminusPoolSupply(
        uint256 poolID
    ) external view returns (uint256) {
        return terminusContract().terminusPoolSupply(poolID);
    }

    function isApprovedForPool(
        uint256 poolID,
        address operator
    ) public view returns (bool) {
        return terminusContract().isApprovedForPool(poolID, operator);
    }

    function approveForPool(
        uint256 poolID,
        address operator
    ) external onlyPoolController(poolID) {
        terminusContract().approveForPool(poolID, operator);
    }

    function unapproveForPool(
        uint256 poolID,
        address operator
    ) external onlyPoolController(poolID) {
        terminusContract().unapproveForPool(poolID, operator);
    }

    function _approvePoolCreationPayments() internal {
        IERC20 paymentToken = IERC20(terminusContract().paymentToken());
        uint256 fee = terminusContract().poolBasePrice();
        uint256 contractBalance = paymentToken.balanceOf(address(this));
        require(
            contractBalance >= fee,
            "TerminusControllerFacet._getPoolCreationPayments: Not enough funds, pls transfet payment tokens to terminusController contract"
        );
        paymentToken.approve(getTerminusAddress(), fee);
    }

    function createSimplePool(
        uint256 _capacity
    ) external onlyMainAdmin returns (uint256) {
        _approvePoolCreationPayments();
        return terminusContract().createSimplePool(_capacity);
    }

    function createPoolV1(
        uint256 _capacity,
        bool _transferable,
        bool _burnable
    ) external onlyMainAdmin returns (uint256) {
        _approvePoolCreationPayments();
        return
            terminusContract().createPoolV1(
                _capacity,
                _transferable,
                _burnable
            );
    }

    function mint(
        address to,
        uint256 poolID,
        uint256 amount,
        bytes memory data
    ) external onlyPoolController(poolID) {
        terminusContract().mint(to, poolID, amount, data);
    }

    function mintBatch(
        address to,
        uint256[] memory poolIDs,
        uint256[] memory amounts,
        bytes memory data
    ) external onlyMainAdmin {
        terminusContract().mintBatch(to, poolIDs, amounts, data);
    }

    function burn(
        address from,
        uint256 poolID,
        uint256 amount
    ) external onlyPoolController(poolID) {
        terminusContract().burn(from, poolID, amount);
    }

    function balanceOf(
        address account,
        uint256 id
    ) public view returns (uint256) {
        return terminusContract().balanceOf(account, id);
    }
}
