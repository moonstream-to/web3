package signer

import (
	"crypto/ecdsa"
	"fmt"
	"io/ioutil"

	"github.com/ethereum/go-ethereum/accounts/keystore"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/hexutil"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
)

type PrivateContainer struct {
	PublicKey  common.Address
	PrivateKey *ecdsa.PrivateKey
}

func InitializeNetworkClient(rpcEndpointURI string) (*ethclient.Client, error) {
	client, err := ethclient.Dial(rpcEndpointURI)
	if err != nil {
		return nil, err
	}

	return client, nil
}

func InitializeSigner(password, keyFilePath, privateKeyStr string) (PrivateContainer, error) {
	privateContainer := PrivateContainer{}

	var publicKey common.Address
	var privateKey *ecdsa.PrivateKey

	if keyFilePath != "" {
		keyFileBytes, err := ioutil.ReadFile(keyFilePath)
		if err != nil {
			return privateContainer, fmt.Errorf("uable to read keyFilePath, err: %v", err)
		}
		key, err := keystore.DecryptKey(keyFileBytes, password)
		if err != nil {
			return privateContainer, fmt.Errorf("unable to decrypt keyfile with password, err: %v", err)
		}
		privateKey = key.PrivateKey
		publicKey = crypto.PubkeyToAddress(privateKey.PublicKey)
	} else {
		var err error
		privateKey, err = crypto.LoadECDSA(privateKeyStr)
		if err != nil {
			return privateContainer, fmt.Errorf("uable to parse private key, err: %v", err)
		}

	}

	privateContainer = PrivateContainer{
		PublicKey:  publicKey,
		PrivateKey: privateKey,
	}
	return privateContainer, nil
}

// Sign message with private key
func (pc *PrivateContainer) Sign(data [32]byte) (string, error) {
	dataSlice := data[:]
	signature, err := crypto.Sign(dataSlice, pc.PrivateKey)
	if err != nil {
		return "", fmt.Errorf("an error occurred while signing with private key, err: %v", err)
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
