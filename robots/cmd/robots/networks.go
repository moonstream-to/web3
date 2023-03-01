package main

import (
	"context"
	"errors"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"

	terminus_contract "github.com/bugout-dev/engine/robots/pkg/terminus"
)

type NetworkContractClient struct {
	Endpoint string
	ChainID  *big.Int

	Client *ethclient.Client

	GasPrice *big.Int

	ContractAddress  common.Address
	ContractInstance *terminus_contract.Terminus
}

type Networks struct {
	NetworkContractClients map[string]NetworkContractClient
}

func (n *Networks) InitializeNetworks() error {
	if n.NetworkContractClients == nil {
		n.NetworkContractClients = make(map[string]NetworkContractClient)
	}

	if NODEBALANCER_ACCESS_ID == "" {
		return errors.New("Environment variable ENGINE_NODEBALANCER_ACCESS_ID should be specified")
	}

	if MUMBAI_WEB3_PROVIDER_URI == "" {
		return errors.New("Environment variable MUMBAI_WEB3_PROVIDER_URI should be specified")
	}
	if POLYGON_WEB3_PROVIDER_URI == "" {
		return errors.New("Environment variable POLYGON_WEB3_PROVIDER_URI should be specified")
	}
	if CALDERA_WEB3_PROVIDER_URI == "" {
		return errors.New("Environment variable MOONSTREAM_CALDERA_WEB3_PROVIDER_URI should be specified")
	}

	n.NetworkContractClients["mumbai"] = NetworkContractClient{
		Endpoint: fmt.Sprintf("%s?access_id=%s&data_source=blockchain", MUMBAI_WEB3_PROVIDER_URI, NODEBALANCER_ACCESS_ID),
		ChainID:  big.NewInt(80001),
	}
	n.NetworkContractClients["polygon"] = NetworkContractClient{
		Endpoint: fmt.Sprintf("%s?access_id=%s&data_source=blockchain", POLYGON_WEB3_PROVIDER_URI, NODEBALANCER_ACCESS_ID),
		ChainID:  big.NewInt(137),
	}
	n.NetworkContractClients["caldera"] = NetworkContractClient{
		Endpoint: CALDERA_WEB3_PROVIDER_URI,
		ChainID:  big.NewInt(322),
	}

	return nil
}

// GenDialRpcClient parse PRC endpoint to dial client
func GenDialRpcClient(rpc_endpoint_uri string) (*ethclient.Client, error) {
	client, err := ethclient.Dial(rpc_endpoint_uri)
	if err != nil {
		return nil, err
	}

	return client, nil
}

// FetchSuggestedGasPrice fetch network for suggested gas price
func (c *NetworkContractClient) FetchSuggestedGasPrice(ctx context.Context) error {
	gas_price, err := c.Client.SuggestGasPrice(ctx)
	if err != nil {
		return err
	}

	c.GasPrice = gas_price

	return nil
}

func GetTerminusContractAddress(blockchain string) (*common.Address, error) {
	switch blockchain {
	case "polygon":
		if TERMINUS_CONTRACT_POLYGON_ADDRESS == "" {
			return nil, errors.New("Terminus polygon contract address should be specified")
		}
		address := common.HexToAddress(TERMINUS_CONTRACT_POLYGON_ADDRESS)
		return &address, nil
	case "mumbai":
		if TERMINUS_CONTRACT_MUMBAI_ADDRESS == "" {
			return nil, errors.New("Terminus mumbai contract address should be specified")
		}
		address := common.HexToAddress(TERMINUS_CONTRACT_MUMBAI_ADDRESS)
		return &address, nil
	case "caldera":
		if TERMINUS_CONTRACT_CALDERA_ADDRESS == "" {
			return nil, errors.New("Terminus caldera contract address should be specified")
		}
		address := common.HexToAddress(TERMINUS_CONTRACT_CALDERA_ADDRESS)
		return &address, nil
	}
	return nil, errors.New(fmt.Sprintf("Not supported blockchain by Terminus contract found: %s", blockchain))
}

// InitializeContractInstance parse contract to instance
func InitializeTerminusContractInstance(client *ethclient.Client, address common.Address) (*terminus_contract.Terminus, error) {
	contractInstance, err := terminus_contract.NewTerminus(address, client)
	if err != nil {
		return nil, err
	}

	return contractInstance, nil
}

func (ct *NetworkContractClient) FetchPoolCapacity(pool_id int64) (*big.Int, error) {
	pool_capacity, err := ct.ContractInstance.TerminusPoolCapacity(nil, big.NewInt(pool_id))
	if err != nil {
		return nil, err
	}

	return pool_capacity, nil
}

// PoolMintBatch executes PoolMintBatch for list of address with same value amount
func (ct *NetworkContractClient) PoolMintBatch(auth *bind.TransactOpts, pool_id_int int64, claimants []Claimant, value int64) (*types.Transaction, error) {
	to_addresses := []common.Address{}
	values := []*big.Int{}
	for _, claimant := range claimants {
		to_addresses = append(to_addresses, common.HexToAddress(claimant.Address))
		values = append(values, big.NewInt(value))
	}

	tx, err := ct.ContractInstance.PoolMintBatch(auth, big.NewInt(pool_id_int), to_addresses, values)
	if err != nil {
		return nil, err
	}

	return tx, nil
}

func (ct *NetworkContractClient) BalanceOfBatch(auth *bind.CallOpts, claimants []Claimant, id_int int64) ([]*big.Int, error) {
	addresses := []common.Address{}
	ids := []*big.Int{}
	for _, claimant := range claimants {
		addresses = append(addresses, common.HexToAddress(claimant.Address))
		ids = append(ids, big.NewInt(id_int))
	}
	balances, err := ct.ContractInstance.BalanceOfBatch(auth, addresses, ids)
	if err != nil {
		return nil, err
	}

	return balances, nil
}
