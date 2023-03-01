package main

import (
	"context"
	"log"
	"math"
	"math/big"
	"sync"
	"time"
)

type RobotInstance struct {
	ValueToClaim int64

	ContractTerminusInstance ContractTerminusInstance
	EntityInstance           EntityInstance
	NetworkInstance          NetworkInstance
	SignerInstance           SignerInstance

	MintCounter int64
}

func Run(configs *[]RobotsConfig) {
	var robots []RobotInstance

	// Configure networks
	networks, err := InitializeNetworks()
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Initialized configuration of network endpoints and chain IDs")

	ctx := context.Background()
	for _, config := range *configs {
		robot := RobotInstance{
			ValueToClaim: config.ValueToClaim,
			MintCounter:  0, // TODO(kompotkot): Fetch minted number from blockchain
		}

		// Configure network client
		network := networks[config.Blockchain]
		client, err := GenDialRpcClient(network.Endpoint)
		if err != nil {
			log.Fatal(err)
		}
		robot.NetworkInstance = NetworkInstance{
			Blockchain: config.Blockchain,
			Endpoint:   network.Endpoint,
			ChainID:    network.ChainID,

			Client: client,
		}
		log.Printf("Initialized configuration of JSON RPC network client for %s blockchain", config.Blockchain)

		// Fetch required opts
		err = robot.NetworkInstance.FetchSuggestedGasPrice(ctx)
		if err != nil {
			log.Fatal(err)
		}

		// Define contract instance
		contractAddress, err := GetTerminusContractAddress(config.Blockchain)
		if err != nil {
			log.Fatal(err)
		}
		contractTerminusInstance, err := InitializeTerminusContractInstance(client, *contractAddress)
		if err != nil {
			log.Fatal(err)
		}
		robot.ContractTerminusInstance = ContractTerminusInstance{
			Address:        *contractAddress,
			Instance:       contractTerminusInstance,
			TerminusPoolId: config.TerminusPoolId,
		}
		log.Printf("Initialized configuration of terminus contract instance for %s blockchain", config.Blockchain)

		// Configure entity client
		entityInstance, err := InitializeEntityInstance(config.CollectionId)
		if err != nil {
			log.Fatal(err)
		}
		robot.EntityInstance = *entityInstance
		log.Printf("Initialized configuration of entity client for '%s' collection", robot.EntityInstance.CollectionId)

		// Configure signer
		signer, err := initializeSigner(config.SignerKeyfileName, config.SignerPasswordFileName)
		if err != nil {
			log.Fatal(err)
		}
		robot.SignerInstance = *signer
		log.Printf("Initialized configuration of signer %s", robot.SignerInstance.Address.String())

		robots = append(robots, robot)
	}

	var wg sync.WaitGroup
	for _, robot := range robots {
		wg.Add(1)
		go robotRun(
			&wg,
			robot,
		)
	}
	wg.Wait()
}

// robotRun represents of each robot instance for specific airdrop
func robotRun(
	wg *sync.WaitGroup,
	robot RobotInstance,
) {
	log.Printf(
		"Spawned robot for blockchain %s, signer %s, entity collection %s, pool %d",
		robot.NetworkInstance.Blockchain,
		robot.SignerInstance.Address.String(),
		robot.EntityInstance.CollectionId,
		robot.ContractTerminusInstance.TerminusPoolId,
	)
	minSleepTime := 5
	maxSleepTime := 60
	timer := minSleepTime
	ticker := time.NewTicker(time.Duration(minSleepTime) * time.Second)

	for {
		select {
		case <-ticker.C:
			empty_addresses_len, err := AirdropRun(&robot)
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

func (ri *RobotInstance) IncreaseMintCounter(num int64) {

}

type Claimant struct {
	EntityId string
	Address  string
}

func AirdropRun(robot *RobotInstance) (int64, error) {
	status_code, search_data, err := robot.EntityInstance.FetchPublicSearchUntouched(JOURNAL_SEARCH_BATCH_SIZE)
	if err != nil {
		return 0, err
	}
	log.Printf("Received response %d from entities API for collection %s with %d results", status_code, robot.EntityInstance.CollectionId, search_data.TotalResults)

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
	balances, err := robot.ContractTerminusInstance.BalanceOfBatch(nil, claimants, robot.ContractTerminusInstance.TerminusPoolId)
	if err != nil {
		return 0, err
	}

	zeroBigInt := big.NewInt(1)
	var emptyClaimantsLen int64
	var emptyClaimants []Claimant
	for i, balance := range balances {
		// If less then 1
		if balance.Cmp(zeroBigInt) == -1 {
			emptyClaimants = append(emptyClaimants, claimants[i])
			emptyClaimantsLen++
		}
	}

	if emptyClaimantsLen > 0 {
		log.Printf("Ready to send tokens for %d addresses", emptyClaimantsLen)

		auth, err := robot.SignerInstance.CreateTransactor(robot.NetworkInstance)
		if err != nil {
			return emptyClaimantsLen, err
		}
		if robot.NetworkInstance.Blockchain == "caldera" {
			auth.GasPrice = big.NewInt(0)
		}

		tx, err := robot.ContractTerminusInstance.PoolMintBatch(auth, emptyClaimants, robot.ValueToClaim)
		if err != nil {
			return emptyClaimantsLen, err
		}
		currentCounter := robot.MintCounter
		robot.MintCounter = currentCounter + emptyClaimantsLen
		log.Printf("Pending tx for PoolMintBatch on blockchain %s at pool ID %d: 0x%x", robot.NetworkInstance.Blockchain, robot.ContractTerminusInstance.TerminusPoolId, tx.Hash())
	}

	var touched_entities int64
	for _, claimant := range claimants {
		_, _, err := robot.EntityInstance.TouchPublicEntity(claimant.EntityId, 10)
		if err != nil {
			log.Printf("Unable to touch entity with ID: %s for claimant: %s, err: %v", claimant.EntityId, claimant.Address, err)
			continue
		}
		touched_entities++
	}
	log.Printf("Marked %d entities from %d claimants total", touched_entities, claimants_len)

	return emptyClaimantsLen, nil
}
