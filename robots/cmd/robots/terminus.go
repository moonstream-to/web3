package main

import (
	"math/big"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"

	terminus_contract "github.com/bugout-dev/engine/robots/pkg/terminus"
)

type ContractTerminus struct {
	Address  common.Address
	Instance *terminus_contract.Terminus
}

func (ct *ContractTerminus) SetContractAddress(address_str string) {
	ct.Address = common.HexToAddress(address_str)
}

// InitializeContractInstance parse contract to instance
func (ct *ContractTerminus) InitializeContractInstance(client *ethclient.Client) error {
	contract_instance, err := terminus_contract.NewTerminus(ct.Address, client)
	if err != nil {
		return err
	}

	ct.Instance = contract_instance

	return nil
}

func (ct *ContractTerminus) FetchPoolCapacity(pool_id int64) (*big.Int, error) {
	pool_capacity, err := ct.Instance.TerminusPoolCapacity(nil, big.NewInt(pool_id))
	if err != nil {
		return nil, err
	}

	return pool_capacity, nil
}

// PoolMintBatch executes PoolMintBatch for list of address with same value amount
func (ct *ContractTerminus) PoolMintBatch(auth *bind.TransactOpts, pool_id_int int64, claimants []Claimant, value int64) (*types.Transaction, error) {
	to_addresses := []common.Address{}
	values := []*big.Int{}
	for _, claimant := range claimants {
		to_addresses = append(to_addresses, common.HexToAddress(claimant.Address))
		values = append(values, big.NewInt(value))
	}

	tx, err := ct.Instance.PoolMintBatch(auth, big.NewInt(pool_id_int), to_addresses, values)
	if err != nil {
		return nil, err
	}

	return tx, nil
}

func (ct *ContractTerminus) BalanceOfBatch(auth *bind.CallOpts, claimants []Claimant, id_int int64) ([]*big.Int, error) {
	addresses := []common.Address{}
	ids := []*big.Int{}
	for _, claimant := range claimants {
		addresses = append(addresses, common.HexToAddress(claimant.Address))
		ids = append(ids, big.NewInt(id_int))
	}
	balances, err := ct.Instance.BalanceOfBatch(auth, addresses, ids)
	if err != nil {
		return nil, err
	}

	return balances, nil
}
