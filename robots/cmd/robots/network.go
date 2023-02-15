package main

import (
	"context"
	"errors"
	"fmt"
	"math/big"
	"os"

	"github.com/ethereum/go-ethereum/ethclient"
)

type NetworkClient struct {
	Client *ethclient.Client

	GasPrice *big.Int
}

type Network struct {
	Endpoint string
	ChainID  *big.Int
}

type Networks struct {
	Networks map[string]Network
}

func (n *Networks) InitializeNetworks() error {
	if n.Networks == nil {
		n.Networks = make(map[string]Network)
	}

	NODEBALANCER_ACCESS_ID := os.Getenv("ENGINE_NODEBALANCER_ACCESS_ID")
	if NODEBALANCER_ACCESS_ID == "" {
		return errors.New("Environment variable ENGINE_NODEBALANCER_ACCESS_ID should be specified")
	}

	MUMBAI_WEB3_PROVIDER_URI := os.Getenv("MOONSTREAM_MUMBAI_WEB3_PROVIDER_URI")
	if MUMBAI_WEB3_PROVIDER_URI == "" {
		return errors.New("Environment variable MUMBAI_WEB3_PROVIDER_URI should be specified")
	}
	POLYGON_WEB3_PROVIDER_URI := os.Getenv("MOONSTREAM_POLYGON_WEB3_PROVIDER_URI")
	if POLYGON_WEB3_PROVIDER_URI == "" {
		return errors.New("Environment variable POLYGON_WEB3_PROVIDER_URI should be specified")
	}

	n.Networks["mumbai"] = Network{
		Endpoint: fmt.Sprintf("%s?access_id=%s&data_source=blockchain", MUMBAI_WEB3_PROVIDER_URI, NODEBALANCER_ACCESS_ID),
		ChainID:  big.NewInt(80001),
	}
	n.Networks["polygon"] = Network{
		Endpoint: fmt.Sprintf("%s?access_id=%s&data_source=blockchain", POLYGON_WEB3_PROVIDER_URI, NODEBALANCER_ACCESS_ID),
		ChainID:  big.NewInt(137),
	}

	return nil
}

// SetDialRpcClient parse PRC endpoint to dial client
func (c *NetworkClient) SetDialRpcClient(rpc_endpoint_uri string) error {
	client, err := ethclient.Dial(rpc_endpoint_uri)
	if err != nil {
		return err
	}

	c.Client = client

	return nil
}

// FetchSuggestedGasPrice fetch network for suggested gas price
func (c *NetworkClient) FetchSuggestedGasPrice(ctx context.Context) error {
	gas_price, err := c.Client.SuggestGasPrice(ctx)
	if err != nil {
		return err
	}

	c.GasPrice = gas_price

	return nil
}
