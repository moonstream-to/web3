package main

import (
	"fmt"
	"os"

	"github.com/ethereum/go-ethereum/accounts/keystore"
	"github.com/ethereum/go-ethereum/crypto"
	"golang.org/x/term"
)

func KeyFromFile(keystoreFile string, password string) (*keystore.Key, error) {
	var emptyKey *keystore.Key
	keystoreContent, readErr := os.ReadFile(keystoreFile)
	if readErr != nil {
		return emptyKey, readErr
	}

	// If password is "", prompt user for password.
	if password == "" {
		fmt.Printf("Please provide a password for keystore (%s): ", keystoreFile)
		passwordRaw, inputErr := term.ReadPassword(int(os.Stdin.Fd()))
		if inputErr != nil {
			return emptyKey, fmt.Errorf("error reading password: %s", inputErr.Error())
		}
		fmt.Printf("\n")
		password = string(passwordRaw)
	}

	key, err := keystore.DecryptKey(keystoreContent, password)
	return key, err
}

func SignRawMessage(message []byte, key *keystore.Key, sensible bool) ([]byte, error) {
	signature, err := crypto.Sign(message, key.PrivateKey)
	if !sensible {
		// This refers to a bug in an early Ethereum client implementation where the v parameter byte was
		// shifted by 27: https://github.com/ethereum/go-ethereum/issues/2053
		// Default for callers should be NOT sensible.
		// Defensively, we only shift if the 65th byte is 0 or 1.
		if signature[64] < 2 {
			signature[64] += 27
		}
	}
	return signature, err
}
