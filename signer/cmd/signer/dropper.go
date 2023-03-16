package main

import (
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"

	dropper_contract "github.com/bugout-dev/engine/signer/pkg/dropper"
)

type DropperContract struct {
	Address  common.Address
	Instance *dropper_contract.Dropper
}

// InitializeDropperContracts set map of dropper contract addresses
// If custom dropper contract required, it could be set with environment
// variable MOONSTREAM_DROPPER_CUSTOM_CONTRACT_ADDRESS.
func InitializeDropperContracts() map[string]DropperContract {
	dropperContracts := make(map[string]DropperContract)

	dropperContracts["polygon"] = DropperContract{
		Address: common.HexToAddress(MOONSTREAM_DROPPER_POLYGON_CONTRACT_ADDRESS),
	}

	if MOONSTREAM_DROPPER_CUSTOM_CONTRACT_ADDRESS != "" {
		dropperContracts["custom"] = DropperContract{
			Address: common.HexToAddress(MOONSTREAM_DROPPER_CUSTOM_CONTRACT_ADDRESS),
		}
	}

	return dropperContracts
}

// InitializeContractInstance parse contract to instance
func (dc *DropperContract) InitializeContractInstance(client *ethclient.Client) error {
	contract_instance, err := dropper_contract.NewDropper(dc.Address, client)
	if err != nil {
		return err
	}

	dc.Instance = contract_instance

	return nil
}

func (dc *DropperContract) claimMessageHash(claimId int64, addr string, blockDeadline int64, amount int64) ([32]byte, error) {
	address := common.HexToAddress(addr)
	cmh, err := dc.Instance.ClaimMessageHash(nil, big.NewInt(claimId), address, big.NewInt(blockDeadline), big.NewInt(amount))
	if err != nil {
		return [32]byte{}, fmt.Errorf("uailed to generate claim message hash, err: %v", err)
	}

	return cmh, nil
}
