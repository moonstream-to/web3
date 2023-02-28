package main

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/accounts/keystore"
)

type Signer struct {
	PrivateKey *keystore.Key
}

// initializeSigner parse secrets directory with keyfile and passfile
func initializeSigner(keyfileName, passfileName string) (string, string, error) {
	secretsDirPath := os.Getenv("ENGINE_ROBOTS_SECRETS_DIR")
	if secretsDirPath == "" {
		return "", "", errors.New("Directory with secrets not specified")
	}

	keyfilePath := fmt.Sprintf("%s/%s", secretsDirPath, keyfileName)
	keyfilePasswordPath := fmt.Sprintf("%s/%s", secretsDirPath, passfileName)

	return keyfilePath, keyfilePasswordPath, nil
}

// SetPrivateKey opens keyfile with password to privateKey
func (s *Signer) SetPrivateKey(keyfile_path, keyfile_password_path string) error {
	passfile, err := ioutil.ReadFile(keyfile_password_path)
	if err != nil {
		return err
	}
	passfile_lines := strings.Split(string(passfile), "\n")
	password := passfile_lines[0]

	keyfile, err := ioutil.ReadFile(keyfile_path)
	if err != nil {
		return err
	}

	private_key, err := keystore.DecryptKey(keyfile, password)
	if err != nil {
		return err
	}

	s.PrivateKey = private_key

	return nil
}

func (s *Signer) CreateTransactor(network Network) (*bind.TransactOpts, error) {
	auth, err := bind.NewKeyedTransactorWithChainID(s.PrivateKey.PrivateKey, network.ChainID)
	if err != nil {
		return nil, err
	}
	// auth.Nonce = big.NewInt(int64(nonce))
	// auth.Value = big.NewInt(0)
	// auth.GasLimit = uint64(300000)
	// auth.GasPrice = gasPrice

	return auth, nil
}
