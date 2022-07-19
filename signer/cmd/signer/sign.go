package main

import (
	"crypto/ecdsa"
	"fmt"
	"io/ioutil"
	"math/big"
	"strings"

	"github.com/ethereum/go-ethereum/accounts/keystore"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
)

var (
	privateContainer PrivateContainer

	dropper *Dropper
)

type PrivateContainer struct {
	publicKey  common.Address
	privateKey *ecdsa.PrivateKey
}

func initDropper() error {
	client, err := ethclient.Dial(RPC_URI)
	if err != nil {
		return fmt.Errorf("Unable to initialize client, err: %v", err)
	}

	address := common.HexToAddress(ENGINE_DROPPER_ADDRESS)
	dropper, err = NewDropper(address, client)
	if err != nil {
		return fmt.Errorf("Failed to create instance of contract, err: %v", err)
	}

	return nil
}

func claimMessageHash(claimId int64, addr string, blockDeadline int64, amount int64) ([32]byte, error) {
	address := common.HexToAddress(addr)
	cmh, err := dropper.ClaimMessageHash(nil, big.NewInt(claimId), address, big.NewInt(blockDeadline), big.NewInt(amount))
	if err != nil {
		return [32]byte{}, fmt.Errorf("Failed to generate claim message hash, err: %v", err)
	}
	return cmh, nil
}

// Sign message with private key
func (pc *PrivateContainer) sign(data [32]byte) (string, error) {
	dataSlice := data[:]
	signature, err := crypto.Sign(dataSlice, pc.privateKey)
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
		publicKey:  publicKey,
		privateKey: privateKey,
	}
	return nil
}
