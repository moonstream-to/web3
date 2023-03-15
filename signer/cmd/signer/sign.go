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

	dropper_contract "github.com/bugout-dev/engine/signer/pkg/dropper"
)

type ContractDropper struct {
	Address  common.Address
	Instance *dropper_contract.Dropper
}

type PrivateContainer struct {
	publicKey  common.Address
	privateKey *ecdsa.PrivateKey
}

func (cd *ContractDropper) SetContractAddress(addressStr string) {
	cd.Address = common.HexToAddress(addressStr)
}

func InitializeNetworkClient(rpcEndpointURI string) (*ethclient.Client, error) {
	client, err := ethclient.Dial(rpcEndpointURI)
	if err != nil {
		return nil, err
	}

	return client, nil
}

// InitializeContractInstance parse contract to instance
func (cd *ContractDropper) InitializeContractInstance(client *ethclient.Client) error {
	contract_instance, err := dropper_contract.NewDropper(cd.Address, client)
	if err != nil {
		return err
	}

	cd.Instance = contract_instance

	return nil
}

func (cd *ContractDropper) claimMessageHash(claimId int64, addr string, blockDeadline int64, amount int64) ([32]byte, error) {
	address := common.HexToAddress(addr)
	cmh, err := cd.Instance.ClaimMessageHash(nil, big.NewInt(claimId), address, big.NewInt(blockDeadline), big.NewInt(amount))
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

	rawSig := hexutil.Encode(signature)

	var sig string
	rawSigLen := len(rawSig)
	if rawSig[rawSigLen-2:] == "00" {
		sig = fmt.Sprintf("%s%s", rawSig[:rawSigLen-2], "1b")
	} else if rawSig[rawSigLen-2:] == "01" {
		sig = fmt.Sprintf("%s%s", rawSig[:rawSigLen-2], "1c")
	} else {
		sig = rawSig
	}

	return sig, nil
}

func initSigner(passFile, keyFile, privateKeyFile string) (*PrivateContainer, error) {
	var publicKey common.Address
	var privateKey *ecdsa.PrivateKey
	if keyFile != "" {
		passFileBytes, err := ioutil.ReadFile(passFile)
		if err != nil {
			return nil, fmt.Errorf("Unable to read passFile, err: %v", err)
		}
		passFileLines := strings.Split(string(passFileBytes), "\n")
		pass := passFileLines[0]

		keyFileBytes, err := ioutil.ReadFile(keyFile)
		if err != nil {
			return nil, fmt.Errorf("Unable to read keyFile, err: %v", err)
		}
		key, err := keystore.DecryptKey(keyFileBytes, pass)
		if err != nil {
			return nil, fmt.Errorf("Unable to decrypt key, err: %v", err)
		}
		privateKey = key.PrivateKey
		publicKey = crypto.PubkeyToAddress(privateKey.PublicKey)
	}
	if privateKeyFile != "" {
		return nil, fmt.Errorf("finish it")

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

	privateContainer := PrivateContainer{
		publicKey:  publicKey,
		privateKey: privateKey,
	}
	return &privateContainer, nil
}

func initSigner2(password, keyFilePath string) (*PrivateContainer, error) {
	var publicKey common.Address
	var privateKey *ecdsa.PrivateKey
	if keyFilePath != "" {
		keyFileBytes, err := ioutil.ReadFile(keyFilePath)
		if err != nil {
			return nil, fmt.Errorf("Unable to read keyFile, err: %v", err)
		}
		key, err := keystore.DecryptKey(keyFileBytes, password)
		if err != nil {
			return nil, fmt.Errorf("Unable to decrypt key, err: %v", err)
		}
		privateKey = key.PrivateKey
		publicKey = crypto.PubkeyToAddress(privateKey.PublicKey)
	}

	privateContainer := PrivateContainer{
		publicKey:  publicKey,
		privateKey: privateKey,
	}
	return &privateContainer, nil
}
