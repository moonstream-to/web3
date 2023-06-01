package main

import (
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"os"

	bugout "github.com/bugout-dev/bugout-go/pkg"
	"github.com/spf13/cobra"
)

func CreateRootCommand() *cobra.Command {
	// rootCmd represents the base command when called without any subcommands
	rootCmd := &cobra.Command{
		Use:   "waggle",
		Short: "Sign Moonstream transaction requests",
		Long: `waggle is a CLI that allows you to sign requests for transactions on Moonstream contracts.

	waggle currently supports signatures for the following types of contracts:
	- Dropper (dropper-v0.2.0)

	waggle makes it easy to sign large numbers of requests in a very short amount of time. It also allows
	you to automatically send transaction requests to the Moonstream API.
	`,
		Run: func(cmd *cobra.Command, args []string) {},
	}

	versionCmd := CreateVersionCommand()
	signCmd := CreateSignCommand()
	accountsCmd := CreateAccountsCommand()
	moonstreamCommand := CreateMoonstreamCommand()
	rootCmd.AddCommand(versionCmd, signCmd, accountsCmd, moonstreamCommand)

	completionCmd := CreateCompletionCommand(rootCmd)
	rootCmd.AddCommand(completionCmd)

	return rootCmd
}

func CreateCompletionCommand(rootCmd *cobra.Command) *cobra.Command {
	completionCmd := &cobra.Command{
		Use:   "completion",
		Short: "Generate shell completion scripts for waggle",
		Long: `Generate shell completion scripts for waggle.

The command for each shell will print a completion script to stdout. You can source this script to get
completions in your current shell session. You can add this script to the completion directory for your
shell to get completions for all future sessions.

For example, to activate bash completions in your current shell:
		$ . <(wagggle completion bash)

To add waggle completions for all bash sessions:
		$ waggle completion bash > /etc/bash_completion.d/waggle_completions`,
	}

	bashCompletionCmd := &cobra.Command{
		Use:   "bash",
		Short: "bash completions for waggle",
		Run: func(cmd *cobra.Command, args []string) {
			rootCmd.GenBashCompletion(cmd.OutOrStdout())
		},
	}

	zshCompletionCmd := &cobra.Command{
		Use:   "zsh",
		Short: "zsh completions for waggle",
		Run: func(cmd *cobra.Command, args []string) {
			rootCmd.GenZshCompletion(cmd.OutOrStdout())
		},
	}

	fishCompletionCmd := &cobra.Command{
		Use:   "fish",
		Short: "fish completions for waggle",
		Run: func(cmd *cobra.Command, args []string) {
			rootCmd.GenFishCompletion(cmd.OutOrStdout(), true)
		},
	}

	powershellCompletionCmd := &cobra.Command{
		Use:   "powershell",
		Short: "powershell completions for waggle",
		Run: func(cmd *cobra.Command, args []string) {
			rootCmd.GenPowerShellCompletion(cmd.OutOrStdout())
		},
	}

	completionCmd.AddCommand(bashCompletionCmd, zshCompletionCmd, fishCompletionCmd, powershellCompletionCmd)

	return completionCmd
}

func CreateVersionCommand() *cobra.Command {
	versionCmd := &cobra.Command{
		Use:   "version",
		Short: "Print the version number of waggle",
		Long:  `All software has versions. This is waggle's`,
		Run: func(cmd *cobra.Command, args []string) {
			cmd.Println(WAGGLE_VERSION)
		},
	}
	return versionCmd
}

func CreateAccountsCommand() *cobra.Command {
	accountsCommand := &cobra.Command{
		Use:   "accounts",
		Short: "Set up signing accounts",
	}

	var keyfile string

	accountsCommand.PersistentFlags().StringVarP(&keyfile, "keystore", "k", "", "Path to keystore file.")

	importCommand := &cobra.Command{
		Use:   "import",
		Short: "Import a signing account from a private key.",
		Long:  "Import a signing account from a private key. This will be stored at the given keystore path.",
		RunE: func(cmd *cobra.Command, args []string) error {
			return KeyfileFromPrivateKey(keyfile)
		},
	}

	accountsCommand.AddCommand(importCommand)

	return accountsCommand
}

func CreateSignCommand() *cobra.Command {
	signCommand := &cobra.Command{
		Use:   "sign",
		Short: "Sign transaction requests",
		Long:  "Contains various commands that help you sign transaction requests",
	}

	// All variables to be used for arguments.
	var chainId int64
	var batchSize int
	var bugoutToken, cursorName, journalID, keyfile, password, claimant, dropperAddress, dropId, requestId, blockDeadline, amount, infile, outfile, query string
	var sensible, header, isCSV bool

	signCommand.PersistentFlags().StringVarP(&keyfile, "keystore", "k", "", "Path to keystore file (this should be a JSON file).")
	signCommand.PersistentFlags().StringVarP(&password, "password", "p", "", "Password for keystore file. If not provided, you will be prompted for it when you sign with the key.")
	signCommand.PersistentFlags().BoolVar(&sensible, "sensible", false, "Set this flag if you do not want to shift the final, v, byte of all signatures by 27. For reference: https://github.com/ethereum/go-ethereum/issues/2053")

	var rawMessage []byte
	rawSubcommand := &cobra.Command{
		Use:   "hash",
		Short: "Sign a raw message hash",
		RunE: func(cmd *cobra.Command, args []string) error {
			key, err := KeyFromFile(keyfile, password)
			if err != nil {
				return err
			}

			signature, err := SignRawMessage(rawMessage, key, sensible)
			if err != nil {
				return err
			}

			cmd.Println(hex.EncodeToString(signature))
			return nil
		},
	}
	rawSubcommand.Flags().BytesHexVarP(&rawMessage, "message", "m", []byte{}, "Raw message to sign (do not include the 0x prefix).")

	dropperSubcommand := &cobra.Command{
		Use:   "dropper",
		Short: "Dropper-related signing functionality",
	}

	dropperHashSubcommand := &cobra.Command{
		Use:   "hash",
		Short: "Generate a message hash for a claim method call",
		RunE: func(cmd *cobra.Command, args []string) error {
			messageHash, err := DropperClaimMessageHash(chainId, dropperAddress, dropId, requestId, claimant, blockDeadline, amount)
			if err != nil {
				return err
			}
			cmd.Println(hex.EncodeToString(messageHash))
			return nil
		},
	}
	dropperHashSubcommand.Flags().Int64Var(&chainId, "chain-id", 1, "Chain ID of the network you are signing for.")
	dropperHashSubcommand.Flags().StringVar(&dropperAddress, "dropper", "0x0000000000000000000000000000000000000000", "Address of Dropper contract")
	dropperHashSubcommand.Flags().StringVar(&dropId, "drop-id", "0", "ID of the drop.")
	dropperHashSubcommand.Flags().StringVar(&requestId, "request-id", "0", "ID of the request.")
	dropperHashSubcommand.Flags().StringVar(&claimant, "claimant", "", "Address of the intended claimant.")
	dropperHashSubcommand.Flags().StringVar(&blockDeadline, "block-deadline", "0", "Block number by which the claim must be made.")
	dropperHashSubcommand.Flags().StringVar(&amount, "amount", "0", "Amount of tokens to distribute.")

	dropperSingleSubcommand := &cobra.Command{
		Use:   "single",
		Short: "Sign a single claim method call",
		RunE: func(cmd *cobra.Command, args []string) error {
			messageHash, hashErr := DropperClaimMessageHash(chainId, dropperAddress, dropId, requestId, claimant, blockDeadline, amount)
			if hashErr != nil {
				return hashErr
			}

			if header {
				cmd.Println(hex.EncodeToString(messageHash))
				return nil
			}

			key, keyErr := KeyFromFile(keyfile, password)
			if keyErr != nil {
				return keyErr
			}

			signedMessage, err := SignRawMessage(messageHash, key, sensible)
			if err != nil {
				return err
			}

			result := DropperClaimMessage{
				DropId:        dropId,
				RequestID:     requestId,
				Claimant:      claimant,
				BlockDeadline: blockDeadline,
				Amount:        amount,
				Signature:     hex.EncodeToString(signedMessage),
				Signer:        key.Address.Hex(),
			}
			resultJSON, encodeErr := json.Marshal(result)
			if encodeErr != nil {
				return encodeErr
			}
			os.Stdout.Write(resultJSON)
			return nil
		},
	}
	dropperSingleSubcommand.Flags().Int64Var(&chainId, "chain-id", 1, "Chain ID of the network you are signing for.")
	dropperSingleSubcommand.Flags().StringVar(&dropperAddress, "dropper", "0x0000000000000000000000000000000000000000", "Address of Dropper contract")
	dropperSingleSubcommand.Flags().StringVar(&dropId, "drop-id", "0", "ID of the drop.")
	dropperSingleSubcommand.Flags().StringVar(&requestId, "request-id", "0", "ID of the request.")
	dropperSingleSubcommand.Flags().StringVar(&claimant, "claimant", "", "Address of the intended claimant.")
	dropperSingleSubcommand.Flags().StringVar(&blockDeadline, "block-deadline", "0", "Block number by which the claim must be made.")
	dropperSingleSubcommand.Flags().StringVar(&amount, "amount", "0", "Amount of tokens to distribute.")
	dropperSingleSubcommand.Flags().BoolVar(&header, "hash", false, "Output the message hash instead of the signature.")

	dropperBatchSubcommand := &cobra.Command{
		Use:   "batch",
		Short: "Sign a batch of claim method calls",
		RunE: func(cmd *cobra.Command, args []string) error {
			key, keyErr := KeyFromFile(keyfile, password)
			if keyErr != nil {
				return keyErr
			}

			var batchRaw []byte
			var readErr error

			var batch []*DropperClaimMessage

			if !isCSV {
				if infile != "" {
					batchRaw, readErr = os.ReadFile(infile)
				} else {
					batchRaw, readErr = io.ReadAll(os.Stdin)
				}
				if readErr != nil {
					return readErr
				}

				parseErr := json.Unmarshal(batchRaw, &batch)
				if parseErr != nil {
					return parseErr
				}
			} else {
				var csvReader *csv.Reader
				if infile == "" {
					csvReader = csv.NewReader(os.Stdin)
				} else {
					r, csvOpenErr := os.Open(infile)
					if csvOpenErr != nil {
						return csvOpenErr
					}
					defer r.Close()

					csvReader = csv.NewReader(r)
				}

				csvData, csvReadErr := csvReader.ReadAll()
				if csvReadErr != nil {
					return csvReadErr
				}

				csvHeaders := csvData[0]
				csvData = csvData[1:]
				batch = make([]*DropperClaimMessage, len(csvData))

				for i, row := range csvData {
					jsonData := make(map[string]string)

					for j, value := range row {
						jsonData[csvHeaders[j]] = value
					}

					jsonString, rowMarshalErr := json.Marshal(jsonData)
					if rowMarshalErr != nil {
						return rowMarshalErr
					}

					rowParseErr := json.Unmarshal(jsonString, &batch[i])
					if rowParseErr != nil {
						return rowParseErr
					}
				}
			}

			for _, message := range batch {
				messageHash, hashErr := DropperClaimMessageHash(chainId, dropperAddress, message.DropId, message.RequestID, message.Claimant, message.BlockDeadline, message.Amount)
				if hashErr != nil {
					return hashErr
				}

				signedMessage, signatureErr := SignRawMessage(messageHash, key, sensible)
				if signatureErr != nil {
					return signatureErr
				}

				message.Signature = hex.EncodeToString(signedMessage)
				message.Signer = key.Address.Hex()
			}

			resultJSON, encodeErr := json.Marshal(batch)
			if encodeErr != nil {
				return encodeErr
			}

			if outfile != "" {
				os.WriteFile(outfile, resultJSON, 0644)
			} else {
				os.Stdout.Write(resultJSON)
			}

			return nil
		},
	}
	dropperBatchSubcommand.Flags().Int64Var(&chainId, "chain-id", 1, "Chain ID of the network you are signing for.")
	dropperBatchSubcommand.Flags().StringVar(&dropperAddress, "dropper", "0x0000000000000000000000000000000000000000", "Address of Dropper contract")
	dropperBatchSubcommand.Flags().StringVar(&infile, "infile", "", "Input file. If not specified, input will be expected from stdin.")
	dropperBatchSubcommand.Flags().StringVar(&outfile, "outfile", "", "Output file. If not specified, output will be written to stdout.")
	dropperBatchSubcommand.Flags().BoolVar(&isCSV, "csv", false, "Set this flag if the --infile is a CSV file.")

	dropperPullSubcommand := &cobra.Command{
		Use:   "pull",
		Short: "Pull unprocessed claim requests from the Bugout API",
		Long:  "Pull unprocessed claim requests from the Bugout API and write them to a CSV file.",
		RunE: func(cmd *cobra.Command, args []string) error {
			bugoutClient, bugoutErr := bugout.ClientFromEnv()
			if bugoutErr != nil {
				return bugoutErr
			}

			if bugoutToken == "" {
				bugoutToken = os.Getenv("BUGOUT_ACCESS_TOKEN")
			}
			if bugoutToken == "" {
				return errors.New("please specify a Bugout API access token, either by passing it as the --token/-t argument or by setting the BUGOUT_ACCESS_TOKEN environment variable")
			}

			if journalID == "" {
				return errors.New("please specify a Bugout journal ID, by passing it as the --journal/-j argument")
			}

			return ProcessDropperClaims(&bugoutClient, bugoutToken, journalID, cursorName, query, batchSize, header, os.Stdout)
		},
	}
	dropperPullSubcommand.Flags().StringVarP(&bugoutToken, "token", "t", "", "Bugout API access token. If you don't have one, you can generate one at https://bugout.dev/account/tokens.")
	dropperPullSubcommand.Flags().StringVarP(&journalID, "journal", "j", "", "ID of Bugout journal from which to pull claim requests.")
	dropperPullSubcommand.Flags().StringVarP(&cursorName, "cursor", "c", "", "Name of cursor which defines which requests are processed and which ones are not.")
	dropperPullSubcommand.Flags().StringVarP(&query, "query", "q", "", "Additional Bugout search query to apply in Bugout.")
	dropperPullSubcommand.Flags().IntVarP(&batchSize, "batch-size", "N", 500, "Maximum number of messages to process.")
	dropperPullSubcommand.Flags().BoolVarP(&header, "header", "H", true, "Set this flag to include header row in output CSV.")

	dropperSubcommand.AddCommand(dropperHashSubcommand, dropperSingleSubcommand, dropperBatchSubcommand, dropperPullSubcommand)

	signCommand.AddCommand(rawSubcommand, dropperSubcommand)

	return signCommand
}

func CreateMoonstreamCommand() *cobra.Command {
	moonstreamCommand := &cobra.Command{
		Use:   "moonstream",
		Short: "Interact with the Moonstream Engine API",
		Long:  "Commands that help you interact with the Moonstream Engine API from your command-line.",
	}

	var blockchain, address, contractType, contractId, contractAddress, infile string
	var limit, offset int

	contractsSubcommand := &cobra.Command{
		Use:   "contracts",
		Short: "List all your registered contracts.",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, clientErr := ClientFromEnv()
			if clientErr != nil {
				return clientErr
			}

			contracts, err := client.ListRegisteredContracts(blockchain, address, contractType, limit, offset)
			if err != nil {
				return err
			}

			encodeErr := json.NewEncoder(cmd.OutOrStdout()).Encode(contracts)
			return encodeErr
		},
	}
	contractsSubcommand.Flags().StringVar(&blockchain, "blockchain", "", "Blockchain")
	contractsSubcommand.Flags().StringVar(&address, "address", "", "Contract address")
	contractsSubcommand.Flags().StringVar(&contractType, "contract-type", "", "Contract type (valid types: \"raw\", \"dropper-v0.2.0\")")
	contractsSubcommand.Flags().IntVar(&limit, "limit", 100, "Limit")
	contractsSubcommand.Flags().IntVar(&offset, "offset", 0, "Offset")

	callRequestsSubcommand := &cobra.Command{
		Use:   "call-requests",
		Short: "List call requests for a given caller.",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, clientErr := ClientFromEnv()
			if clientErr != nil {
				return clientErr
			}

			callRequests, err := client.ListCallRequests(contractId, contractAddress, address, limit, offset)
			if err != nil {
				return err
			}

			encodeErr := json.NewEncoder(cmd.OutOrStdout()).Encode(callRequests)
			return encodeErr
		},
	}
	callRequestsSubcommand.Flags().StringVar(&contractId, "contract-id", "", "Moonstream Engine ID of the registered contract")
	callRequestsSubcommand.Flags().StringVar(&contractAddress, "contract-address", "", "Address of the contract (at least one of --contract-id or --contract-address must be specified)")
	callRequestsSubcommand.Flags().StringVar(&address, "caller", "", "Address of caller")
	callRequestsSubcommand.Flags().IntVar(&limit, "limit", 100, "Limit")
	callRequestsSubcommand.Flags().IntVar(&offset, "offset", 0, "Offset")

	createCallRequestsSubcommand := &cobra.Command{
		Use:   "drop",
		Short: "Submit Dropper call requests to the Moonstream Engine API.",
		RunE: func(cmd *cobra.Command, args []string) error {
			client, clientErr := ClientFromEnv()
			if clientErr != nil {
				return clientErr
			}

			var messagesRaw []byte
			var readErr error
			if infile != "" {
				messagesRaw, readErr = os.ReadFile(infile)
			} else {
				messagesRaw, readErr = io.ReadAll(os.Stdin)
			}
			if readErr != nil {
				return readErr
			}

			var messages []*DropperClaimMessage
			parseErr := json.Unmarshal(messagesRaw, &messages)
			if parseErr != nil {
				return parseErr
			}

			callRequests := make([]CallRequestSpecification, len(messages))
			for i, message := range messages {
				callRequests[i] = CallRequestSpecification{
					Caller: message.Claimant,
					Method: "claim",
					Parameters: DropperCallRequestParameters{
						DropId:        message.DropId,
						RequestID:     message.RequestID,
						BlockDeadline: message.BlockDeadline,
						Amount:        message.Amount,
						Signer:        message.Signer,
						Signature:     message.Signature,
					},
				}
			}

			err := client.CreateCallRequests(contractId, contractAddress, limit, callRequests)
			return err
		},
	}
	createCallRequestsSubcommand.Flags().StringVar(&contractId, "contract-id", "", "Moonstream Engine ID of the registered contract")
	createCallRequestsSubcommand.Flags().StringVar(&contractAddress, "contract-address", "", "Address of the contract (at least one of --contract-id or --contract-address must be specified)")
	createCallRequestsSubcommand.Flags().IntVar(&limit, "ttl-days", 30, "Number of days for which request will remain active")
	createCallRequestsSubcommand.Flags().StringVar(&infile, "infile", "", "Input file. If not specified, input will be expected from stdin.")

	moonstreamCommand.AddCommand(contractsSubcommand, callRequestsSubcommand, createCallRequestsSubcommand)

	return moonstreamCommand
}
