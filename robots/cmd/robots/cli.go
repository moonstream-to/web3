package main

import (
	"flag"
	"fmt"
	"os"
	"strings"
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

		// Load configuration
		configPlacement, err := PrepareConfigPlacement(stateCLI.configPathFlag)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		configs, err := LoadConfig(configPlacement.ConfigPath)
		if err != nil {
			fmt.Println(err)
			os.Exit(1)
		}

		Run(configs)
	case "version":
		stateCLI.versionCmd.Parse(os.Args[2:])

		fmt.Printf("v%s\n", ROBOTS_VERSION)
	default:
		stateCLI.usage()
		os.Exit(1)
	}
}
