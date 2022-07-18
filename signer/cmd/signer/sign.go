package main

import (
	"crypto/ecdsa"
	"fmt"
	"io/ioutil"
	"strings"

	"github.com/ethereum/go-ethereum/accounts/keystore"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/crypto"
)

var (
	privateContainer PrivateContainer
)

type PrivateContainer struct {
	publicKey  string
	privateKey *ecdsa.PrivateKey
}

// Sign message with private key
func (pc *PrivateContainer) sign(dataStr string) (string, error) {
	data, err := hexutil.Decode(dataStr)
	if err != nil {
		return "", fmt.Errorf("Unable to decode message, err: %v", err)
	}
	signature, err := crypto.Sign(data, pc.privateKey)
	if err != nil {
		return "", fmt.Errorf("An error occurred while signing with private key, err: %v", err)
	}

	sig := hexutil.Encode(signature)

	return sig, nil
}

func initSigner(passFile, keyFile, privateKeyFile string) error {
	var publicKey common.Address
	var privateKey *ecdsa.PrivateKey
	if keyFile != "" {
		passFileBytes, err := ioutil.ReadFile(passFile)
		if err != nil {
			return fmt.Errorf("Unable to read passFile, err: %v", err)
		}
		passFileLines := strings.Split(string(passFileBytes), "\n")
		pass := passFileLines[0]

		keyFileBytes, err := ioutil.ReadFile(keyFile)
		if err != nil {
			return fmt.Errorf("Unable to read keyFile, err: %v", err)
		}
		key, err := keystore.DecryptKey(keyFileBytes, pass)
		if err != nil {
			return fmt.Errorf("Unable to decrypt key, err: %v", err)
		}
		privateKey = key.PrivateKey
		publicKey = crypto.PubkeyToAddress(privateKey.PublicKey)
	}
	if privateKeyFile != "" {
		return fmt.Errorf("finish it")

		//privateKeyFileBytes, err := ioutil.ReadFile(privateKeyFile)
		//if err != nil {
		//	return fmt.Errorf("Unable to read privateKeyFile, err %v", err)
		//}
		//privateKey, err = crypto.HexToECDSA(string(privateKeyFileBytes))
		//if err != nil {
		//	return fmt.Errorf("Unable to parse privateKeyFile, err: %v", err)
		//}
		//publicKey = privateKey.PublicKey
	}

	privateContainer = PrivateContainer{
		publicKey:  publicKey.String(),
		privateKey: privateKey,
	}
	return nil
}
