package main

import (
	"encoding/hex"
	"os"

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
	rootCmd.AddCommand(versionCmd, signCmd)

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

func CreateSignCommand() *cobra.Command {
	signCommand := &cobra.Command{
		Use:   "sign",
		Short: "Sign transaction requests",
		Long:  "Contains various commands that help you sign transaction requests",
	}

	var keyfile, password string
	var sensible bool
	signCommand.PersistentFlags().StringVarP(&keyfile, "keystore", "k", "", "Path to keystore file (this should be a JSON file).")
	signCommand.PersistentFlags().StringVarP(&password, "password", "p", "", "Password for keystore file. If not provided, you will be prompted for it when you sign with the key.")
	signCommand.PersistentFlags().BoolVar(&sensible, "sensible", false, "Set this flag if you do not want to shift the final, v, byte of the signature by 27. For reference: https://github.com/ethereum/go-ethereum/issues/2053")

	var rawMessage []byte
	rawSubcommand := &cobra.Command{
		Use:   "hash",
		Short: "Sign a raw message hash",
		Run: func(cmd *cobra.Command, args []string) {
			key, err := KeyFromFile(keyfile, password)
			if err != nil {
				cmd.Println(err.Error())
				os.Exit(1)
			}

			signature, err := SignRawMessage(rawMessage, key, sensible)
			if err != nil {
				cmd.Println(err.Error())
				os.Exit(1)
			}

			cmd.Println(hex.EncodeToString(signature))
		},
	}
	rawSubcommand.Flags().BytesHexVarP(&rawMessage, "message", "m", []byte{}, "Raw message to sign (do not include the 0x prefix).")

	signCommand.AddCommand(rawSubcommand)

	return signCommand
}
