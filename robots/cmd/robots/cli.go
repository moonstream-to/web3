package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"math"
	"os"
	"strings"
	"time"
)

var (
	// Storing CLI definitions at server startup
	stateCLI StateCLI
)

// Command Line Interface state
type StateCLI struct {
	generateConfigCmd *flag.FlagSet
	runCmd            *flag.FlagSet
	versionCmd        *flag.FlagSet

	// Common flags
	configPathFlag string
	helpFlag       bool

	// Run flags
	reportMapDuration    int
	reportMapHumbugToken string
}

type flagSlice []string

func (i *flagSlice) String() string {
	return strings.Join(*i, ", ")
}

func (i *flagSlice) Set(value string) error {
	*i = append(*i, value)
	return nil
}

func (s *StateCLI) usage() {
	fmt.Printf(`usage: robots [-h] {%[1]s,%[2]s,%[3]s} ...

Moonstream robots CLI
optional arguments:
    -h, --help         show this help message and exit

subcommands:
    {%[1]s,%[2]s,%[3]s}
`, s.generateConfigCmd.Name(), s.runCmd.Name(), s.versionCmd.Name())
}

// Check if required flags are set
func (s *StateCLI) checkRequirements() {
	if s.helpFlag {
		switch {
		case s.generateConfigCmd.Parsed():
			fmt.Printf("Generate new configuration\n\n")
			s.generateConfigCmd.PrintDefaults()
			os.Exit(0)
		case s.runCmd.Parsed():
			fmt.Printf("Run robots operations\n\n")
			s.runCmd.PrintDefaults()
			os.Exit(0)
		case s.versionCmd.Parsed():
			fmt.Printf("Show version\n\n")
			s.versionCmd.PrintDefaults()
			os.Exit(0)
		default:
			s.usage()
			os.Exit(0)
		}
	}
}

func (s *StateCLI) populateCLI() {
	// Subcommands setup
	s.generateConfigCmd = flag.NewFlagSet("generate-config", flag.ExitOnError)
	s.runCmd = flag.NewFlagSet("run", flag.ExitOnError)
	s.versionCmd = flag.NewFlagSet("version", flag.ExitOnError)

	// Common flag pointers
	for _, fs := range []*flag.FlagSet{s.generateConfigCmd, s.runCmd, s.versionCmd} {
		fs.BoolVar(&s.helpFlag, "help", false, "Show help message")
		fs.StringVar(&s.configPathFlag, "config", "", "Path to configuration file (default: ~/.robots/config.json)")
	}

	// Run list subcommand flag pointers
	s.runCmd.IntVar(&s.reportMapDuration, "report-map-duration", 60, "How often to push report map in Humbug journal in seconds, default: 60")
	s.runCmd.StringVar(&s.reportMapHumbugToken, "report-map-humbug-token", "", "Humbug report token to push report map")
}

func cli() {
	stateCLI.populateCLI()
	if len(os.Args) < 2 {
		stateCLI.usage()
		os.Exit(1)
	}

	// Parse subcommands and appropriate FlagSet
	switch os.Args[1] {
	case "generate-config":
		stateCLI.generateConfigCmd.Parse(os.Args[2:])
		stateCLI.checkRequirements()

		configPlacement, err := PrepareConfigPlacement(stateCLI.configPathFlag)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		if err := GenerateDefaultConfig(configPlacement); err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
	case "run":
		stateCLI.runCmd.Parse(os.Args[2:])
		stateCLI.checkRequirements()

		run()
	case "version":
		stateCLI.versionCmd.Parse(os.Args[2:])

		fmt.Printf("v%s\n", ROBOTS_VERSION)
	default:
		stateCLI.usage()
		os.Exit(1)
	}
}

func run() {
	// Load configuration
	configs, err := LoadConfig(stateCLI.configPathFlag)
	if err != nil {
		log.Fatal(err)
	}

	// Configure networks
	networks := Networks{}
	err = networks.InitializeNetworks()
	if err != nil {
		log.Fatal(err)
	}

	ctx := context.Background()
	networkContractClient := make(map[string]NetworkContractClient)
	for _, config := range *configs {
		if nc, ok := networkContractClient[config.Blockchain]; ok {
			continue
		} else {
			// Configure network client
			network := networks.Networks[config.Blockchain]
			client, err := GenDialRpcClient(network.Endpoint)
			if err != nil {
				log.Fatal(err)
			}
			nc.Client = client

			// Fetch required opts
			err = nc.FetchSuggestedGasPrice(ctx)
			if err != nil {
				log.Fatal(err)
			}

			log.Printf("Configuration of JSON RPC network for %s blockchain is complete", config.Blockchain)

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

			log.Println("Configuration of terminus contract instance is complete")

			networkContractClient[config.Blockchain] = nc
		}
	}

	for _, config := range *configs {
		// Configure entity client
		entityClient := EntityClient{}
		err = entityClient.InitializeEntityClient(config.CollectionId)
		if err != nil {
			log.Fatal(err)
		}
		log.Println("Configuration of entity client is complete")

		// Configure signer
		keyfilePath, keyfilePasswordPath, err := initializeSigner(config.SignerKeyfileName, config.SignerPasswordFileName)
		if err != nil {
			log.Fatal(err)
		}

		signer := Signer{}
		err = signer.SetPrivateKey(keyfilePath, keyfilePasswordPath)
		if err != nil {
			log.Fatal(err)
		}

		log.Printf("Configuration of signer %s is complete", signer.PrivateKey.Address.String())

		go worker(networkContractClient[config.Blockchain], &config, entityClient, signer, networks.Networks[config.Blockchain])
	}

}

func worker(networkCLient NetworkContractClient, config *RobotsConfig, entityClient EntityClient, signer Signer, network Network) {
	min_sleep_time := 5
	max_sleep_time := 60
	timer := min_sleep_time

	for true {
		time.Sleep(time.Second * time.Duration(timer))

		empty_addresses_len, err := AirdropRun(
			entityClient,
			int64(config.TerminusPoolId),
			networkCLient,
			signer, network, int64(config.ValueToClaim), config.Blockchain)
		if err != nil {
			log.Printf("During AirdropRun an error occurred, err: %v", err)
			timer = timer + 10
			continue
		}
		if empty_addresses_len == 0 {
			timer = int(math.Min(float64(max_sleep_time), float64(timer+1)))
			log.Printf("Sleeping for %d seconds because of no new empty addresses", timer)
			continue
		}
		timer = int(math.Max(float64(min_sleep_time), float64(timer-10)))
	}
}
