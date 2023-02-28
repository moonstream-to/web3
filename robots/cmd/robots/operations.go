package main

import (
	"log"
	"math/big"
)

var (
	SEARCH_BATCH_SIZE = 20
)

type Claimant struct {
	EntityId string
	Address  string
}

func AirdropRun(
	entity_client EntityClient,
	pool_id int64,
	contract NetworkContractClient,
	signer Signer,
	network Network,
	value int64,
	network_flag string,
) (int64, error) {
	status_code, search_data, err := entity_client.FetchPublicSearchUntouched(SEARCH_BATCH_SIZE, 15)
	if err != nil {
		return 0, err
	}
	log.Printf("Received response %d from entities API with %d results", status_code, search_data.TotalResults)

	var claimants_len int64
	var claimants []Claimant
	for _, entity := range search_data.Entities {
		claimants = append(claimants, Claimant{
			EntityId: entity.EntityId,
			Address:  entity.Address,
		})
		claimants_len++
	}

	if claimants_len == 0 {
		return claimants_len, nil
	}

	// Fetch balances for addresses and update list
	balances, err := contract.BalanceOfBatch(nil, claimants, pool_id)
	if err != nil {
		return 0, err
	}

	zeroBigInt := big.NewInt(0)
	var empty_claimants_len int64
	var empty_claimants []Claimant
	for i, balance := range balances {
		if balance.Cmp(zeroBigInt) == 0 {
			empty_claimants = append(empty_claimants, claimants[i])
			empty_claimants_len++
		}
	}

	if empty_claimants_len > 0 {
		log.Printf("Ready to send tokens for %d addresses", empty_claimants_len)

		auth, err := signer.CreateTransactor(network)
		if err != nil {
			return empty_claimants_len, err
		}
		if network_flag == "caldera" {
			auth.GasPrice = big.NewInt(0)
		}

		tx, err := contract.PoolMintBatch(auth, pool_id, empty_claimants, value)
		if err != nil {
			return empty_claimants_len, err
		}
		log.Printf("Pending tx for PoolMintBatch: 0x%x", tx.Hash())
	}

	var touched_entities int64
	for _, claimant := range claimants {
		_, _, err := entity_client.TouchPublicEntity(claimant.EntityId, 10)
		if err != nil {
			log.Printf("Unable to touch entity with ID: %s for claimant: %s, err: %v", claimant.EntityId, claimant.Address, err)
			continue
		}
		touched_entities++
	}
	log.Printf("Marked %d entities from %d claimants total", touched_entities, claimants_len)

	return empty_claimants_len, nil
}
