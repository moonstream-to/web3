package main

import (
	"context"
	"log"
	"math"
	"math/big"
	"time"
)

type Claimant struct {
	EntityId string
	Address  string
}

func Run(configs *[]RobotsConfig) {
	// Configure networks
	networks := Networks{}
	err := networks.InitializeNetworks()
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Initialized configuration of network endpoints and chain IDs")

	ctx := context.Background()
	for _, config := range *configs {
		if nc, ok := networks.NetworkContractClients[config.Blockchain]; ok {
			continue
		} else {
			// Configure network client
			network := networks.NetworkContractClients[config.Blockchain]
			client, err := GenDialRpcClient(network.Endpoint)
			if err != nil {
				log.Fatal(err)
			}
			nc.Client = client

			log.Printf("Initialized configuration of JSON RPC network client for %s blockchain", config.Blockchain)

			// Fetch required opts
			err = nc.FetchSuggestedGasPrice(ctx)
			if err != nil {
				log.Fatal(err)
			}

			// Define contract instance
			contractAddress, err := GetTerminusContractAddress(config.Blockchain)
			if err != nil {
				log.Fatal(err)
			}
			contractTerminus, err := InitializeTerminusContractInstance(nc.Client, *contractAddress)
			if err != nil {
				log.Fatal(err)
			}
			nc.ContractAddress = *contractAddress
			nc.ContractInstance = contractTerminus

			log.Printf("Initialized configuration of terminus contract instance for %s blockchain", config.Blockchain)

			networks.NetworkContractClients[config.Blockchain] = nc
		}
	}

	for _, config := range *configs {
		// Configure entity client
		entityClient, err := InitializeEntityClient(config.CollectionId)
		if err != nil {
			log.Fatal(err)
		}
		log.Printf("Initialized configuration of entity client for '%s' collection with ID %s", entityClient.CollectionName, entityClient.CollectionId)

		// Configure signer
		signer, err := initializeSigner(config.SignerKeyfileName, config.SignerPasswordFileName)
		if err != nil {
			log.Fatal(err)
		}

		log.Printf("Configuration of signer %s is complete", signer.Address.String())

		go robot(
			networks.NetworkContractClients[config.Blockchain],
			entityClient,
			signer,
			config.TerminusPoolId,
			config.ValueToClaim,
			config.Blockchain,
		)
	}
}

// robot represents of each robot instance for specific airdrop
func robot(
	networkContractCLient NetworkContractClient,
	entityClient *EntityClient,
	signer *Signer,
	terminusPoolId int64,
	valueToClaim int64,
	blockchain string,
) {
	minSleepTime := 5
	maxSleepTime := 60
	timer := minSleepTime
	ticker := time.NewTicker(time.Duration(minSleepTime) * time.Second)

	for {
		select {
		case <-ticker.C:
			empty_addresses_len, err := AirdropRun(
				networkContractCLient,
				entityClient,
				signer,
				terminusPoolId,
				valueToClaim,
				blockchain,
			)
			if err != nil {
				log.Printf("During AirdropRun an error occurred, err: %v", err)
				timer = timer + 10
				ticker.Reset(time.Duration(timer) * time.Second)
				continue
			}
			if empty_addresses_len == 0 {
				timer = int(math.Min(float64(maxSleepTime), float64(timer+1)))
				ticker.Reset(time.Duration(timer) * time.Second)
				log.Printf("Sleeping for %d seconds because of no new empty addresses", timer)
				continue
			}
			timer = int(math.Max(float64(minSleepTime), float64(timer-10)))
			ticker.Reset(time.Duration(timer) * time.Second)
		}
	}
}

func AirdropRun(
	networkContractCLient NetworkContractClient,
	entityClient *EntityClient,
	signer *Signer,
	terminusPoolId int64,
	valueToClaim int64,
	blockchain string,
) (int64, error) {
	status_code, search_data, err := entityClient.FetchPublicSearchUntouched(JOURNAL_SEARCH_BATCH_SIZE)
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
	balances, err := networkContractCLient.BalanceOfBatch(nil, claimants, terminusPoolId)
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

		auth, err := signer.CreateTransactor(networkContractCLient)
		if err != nil {
			return empty_claimants_len, err
		}
		if blockchain == "caldera" {
			auth.GasPrice = big.NewInt(0)
		}

		tx, err := networkContractCLient.PoolMintBatch(auth, terminusPoolId, empty_claimants, valueToClaim)
		if err != nil {
			return empty_claimants_len, err
		}
		log.Printf("Pending tx for PoolMintBatch: 0x%x", tx.Hash())
	}

	var touched_entities int64
	for _, claimant := range claimants {
		_, _, err := entityClient.TouchPublicEntity(claimant.EntityId, 10)
		if err != nil {
			log.Printf("Unable to touch entity with ID: %s for claimant: %s, err: %v", claimant.EntityId, claimant.Address, err)
			continue
		}
		touched_entities++
	}
	log.Printf("Marked %d entities from %d claimants total", touched_entities, claimants_len)

	return empty_claimants_len, nil
}
