package main

import (
	"context"
	"flag"
	"log"
	"math"
	"strings"
	"time"
)

type flagSlice []string

func (i *flagSlice) String() string {
	return strings.Join(*i, ", ")
}

func (i *flagSlice) Set(value string) error {
	*i = append(*i, value)
	return nil
}

func cli() {
	var contract_address_flag string
	var network_flag string
	var secrets_dir_path_flag string

	var collection_flag string
	var pool_id_flag int64
	var to_addresses_flag flagSlice
	var value_flag int64

	flag.StringVar(&contract_address_flag, "address", "", "Contract address")
	flag.StringVar(&network_flag, "network", "polygon", "JSON RPC network")
	flag.StringVar(&secrets_dir_path_flag, "secrets-dir", "", "Path to directory with keyfile and password file")

	flag.StringVar(&collection_flag, "collection", "", "Airdrop collection ID")
	flag.Int64Var(&pool_id_flag, "pool-id", 0, "Pool ID run operations to")
	flag.Var(&to_addresses_flag, "to-addresses", "List of addresses for claim")
	flag.Int64Var(&value_flag, "value", 0, "Value to claim")
	flag.Parse()

	// Configure network with client
	networks := Networks{}
	err := networks.InitializeNetworks()
	if err != nil {
		log.Fatal(err)
	}

	network := networks.Networks[network_flag]

	network_client := NetworkClient{}
	err = network_client.SetDialRpcClient(network.Endpoint)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Configuration of JSON RPC network is complete")

	// Configure signer
	keyfile_path, keyfile_password_path, err := initializeSigner(secrets_dir_path_flag)
	if err != nil {
		log.Fatal(err)
	}

	signer := Signer{}
	err = signer.SetPrivateKey(keyfile_path, keyfile_password_path)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Configuration of signer is complete")

	// Fetch required opts
	ctx := context.Background()

	err = network_client.FetchSuggestedGasPrice(ctx)
	if err != nil {
		log.Fatal(err)
	}

	// Define contract instance
	contract := ContractTerminus{}
	contract.SetContractAddress(contract_address_flag)
	err = contract.InitializeContractInstance(network_client.Client)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Configuration of terminus contract instance is complete")

	// Configure entity client
	entity_client := EntityClient{}
	err = entity_client.InitializeEntityClient(collection_flag)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Configuration of entity client is complete")

	min_sleep_time := 5
	max_sleep_time := 60
	timer := min_sleep_time

	var empty_addresses_len_sum int64
	for true {
		time.Sleep(time.Second * time.Duration(timer))

		empty_addresses_len, err := AirdropRun(entity_client, pool_id_flag, contract, signer, network, value_flag, network_flag)
		if err != nil {
			log.Printf("During AirdropRun an error occurred, err: %v", err)
			timer = timer + 10
			continue
		}
		if empty_addresses_len == 0 && empty_addresses_len_sum >= 3 {
			timer = int(math.Min(float64(max_sleep_time), float64(timer+1)))
			log.Printf("Sleeping for %d seconds because of no new empty addresses", timer)
			empty_addresses_len_sum = 0
			continue
		}
		if empty_addresses_len == 0 {
			empty_addresses_len_sum++
		}
		timer = int(math.Max(float64(min_sleep_time), float64(timer-1)))
	}
}
