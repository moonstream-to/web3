// SPDX-License-Identifier: UNLICENSED
///@notice This contract is for mock for WETH token.
pragma solidity ^0.8.0;

import "@openzeppelin-contracts/contracts/token/ERC20/ERC20.sol";

contract MockErc20 is ERC20 {
    constructor(string memory name, string memory symbol) ERC20(name, symbol) {}

    function mint(address account, uint256 amount) public {
        _mint(account, amount);
    }

    function decimals() public view virtual override returns (uint8) {
        return 18;
    }
}
