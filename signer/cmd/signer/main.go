package main

import (
	"flag"
	"fmt"
	"os"
)

var (
	// Storing CLI definitions
	stateCLI StateCLI

	ENGINE_DROPPER_ADDRESS = os.Getenv("ENGINE_DROPPER_ADDRESS")
	RPC_URI                = os.Getenv("RPC_URI")
)

// Command Line Interface state
type StateCLI struct {
	genCmd     *flag.FlagSet
	versionCmd *flag.FlagSet

	// Common flags
	passFileFlag       string
	keyFileFlag        string
	privateKeyFileFlag string
	helpFlag           bool

	// Gen flags
	claimIdFlag    int64
	inputFlag      string
	outputFlag     string
	outputTypeFlag string
	headerFlag     bool
}

func (s *StateCLI) usage() {
	fmt.Printf(`usage: signer [-h] {%[1]s,%[2]s} ...

Generate signed messages.

optional arguments:
    -h, --help         show this help message and exit

subcommands:
    {%[1]s,%[2]s}
`, s.genCmd.Name(), s.versionCmd.Name())
}

// Check if required flags are set
func (s *StateCLI) checkRequirements() {
	if s.helpFlag {
		switch {
		case s.genCmd.Parsed():
			fmt.Printf("Generate signed messages command\n\n")
			s.genCmd.PrintDefaults()
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

	switch {
	case s.genCmd.Parsed():
		if s.claimIdFlag == 0 {
			fmt.Println("Flag claim-id should be specified")
			os.Exit(1)
		}
		if s.inputFlag == "" {
			fmt.Println("Flag input should be specified")
			os.Exit(1)
		}
	}

	if s.outputTypeFlag != "json" && s.outputTypeFlag != "csv" {
		fmt.Printf("Unsupported output file type %s", s.outputTypeFlag)
		os.Exit(1)
	}

	if s.passFileFlag != "" {
		passFileExists, err := CheckPathExists(s.passFileFlag)
		if err != nil || !passFileExists {
			fmt.Printf("File with password at %s not found, err: %v", s.passFileFlag, err)
			os.Exit(1)
		}
	}
	if s.keyFileFlag == "" && s.privateKeyFileFlag == "" {
		fmt.Println("Flag keyfile or privatekey should be specified")
		os.Exit(1)
	}
	if s.keyFileFlag != "" && s.privateKeyFileFlag != "" {
		fmt.Println("One of keyfile or privatekey file should be specified, not both")
		os.Exit(1)
	}
	if s.keyFileFlag != "" {
		keyFileExists, err := CheckPathExists(s.keyFileFlag)
		if err != nil || !keyFileExists {
			fmt.Printf("Keyfile at %s not found, err: %v", s.keyFileFlag, err)
			os.Exit(1)
		}
	}
	if s.privateKeyFileFlag != "" {
		privateKeyFileExists, err := CheckPathExists(s.privateKeyFileFlag)
		if err != nil || !privateKeyFileExists {
			fmt.Printf("Privatekey file at %s not found, err: %v", s.privateKeyFileFlag, err)
			os.Exit(1)
		}
	}
}

func (s *StateCLI) populateCLI() {
	// Subcommands setup
	s.genCmd = flag.NewFlagSet("gen", flag.ExitOnError)
	s.versionCmd = flag.NewFlagSet("version", flag.ExitOnError)

	// Common flag pointers
	for _, fs := range []*flag.FlagSet{s.genCmd, s.versionCmd} {
		fs.BoolVar(&s.helpFlag, "help", false, "Show help message")
		fs.StringVar(&s.passFileFlag, "passfile", "", "Path to file with password")
		fs.StringVar(&s.keyFileFlag, "keyfile", "", "Path to keyfile")
		fs.StringVar(&s.privateKeyFileFlag, "privatekey", "", "Path to file with private key")
	}

	// Gen subcommand flag pointers
	s.genCmd.Int64Var(&s.claimIdFlag, "claim-id", 0, "Dropper claim ID")
	s.genCmd.StringVar(&s.inputFlag, "input", "", "Addresses input to sign, supported types: .csv")
	s.genCmd.StringVar(&s.outputFlag, "output", "output", "Output for generated messages, default: ./output.json")
	s.genCmd.StringVar(&s.outputTypeFlag, "output-type", "json", "Output extension, default: json")
	s.genCmd.BoolVar(&s.headerFlag, "header", true, "Specify this flag if input csv file contains header")
}

func cli() {
	stateCLI.populateCLI()
	if len(os.Args) < 2 {
		stateCLI.usage()
		os.Exit(1)
	}

	// Parse subcommands and appropriate FlagSet
	switch os.Args[1] {
	case "gen":
		stateCLI.genCmd.Parse(os.Args[2:])
		stateCLI.checkRequirements()

		err := initSigner(stateCLI.passFileFlag, stateCLI.keyFileFlag, stateCLI.privateKeyFileFlag)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		err = initDropper()
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		inputs, err := ParseInput(stateCLI.inputFlag, stateCLI.headerFlag)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		var claimants []Claimant
		for _, input := range inputs {
			chm, err := claimMessageHash(stateCLI.claimIdFlag, input.Address, input.ClaimBlockDeadline, input.Amount)
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}
			sig, err := privateContainer.sign(chm)
			if err != nil {
				fmt.Println(err)
				os.Exit(1)
			}
			claimants = append(claimants, Claimant{
				ClaimantAddress:    input.Address,
				Amount:             input.Amount,
				Signature:          sig,
				ClaimBlockDeadline: input.ClaimBlockDeadline,
				ClaimId:            stateCLI.claimIdFlag,
			})
		}
		fullPath, err := ProcessOutput(claimants, stateCLI.outputFlag, stateCLI.outputTypeFlag)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		fmt.Printf("Output saved at: %s\nSigner address: %s\n", fullPath, privateContainer.publicKey.String())

	case "version":
		stateCLI.versionCmd.Parse(os.Args[2:])
		stateCLI.checkRequirements()

		fmt.Printf("v%s\n", SIGNER_VERSION)

	default:
		stateCLI.usage()
		os.Exit(1)
	}
}

func main() {
	cli()
}
