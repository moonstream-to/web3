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
func initializeSigner(secrets_dir_path string) (string, string, error) {
	secrets_dir := os.Getenv("ENGINE_ROBOTS_SECRETS_DIR")
	if secrets_dir == "" {
		secrets_dir = secrets_dir_path
	}
	if secrets_dir == "" {
		return "", "", errors.New("Directory with secrets not specified")
	}

	keyfile_name := os.Getenv("ENGINE_ROBOTS_KEYFILE_NAME")
	if keyfile_name == "" {
		var keyfiles []string
		files, err := ioutil.ReadDir(secrets_dir)
		if err != nil {
			return "", "", errors.New("Files in secrets dir not found")
		}
		for _, file := range files {
			if strings.HasPrefix(file.Name(), "UTC--") {
				keyfiles = append(keyfiles, file.Name())
			}
		}
		if len(keyfiles) != 1 {
			return "", "", errors.New("Wrong number of keyfiles generated")
		}
		keyfile_name = keyfiles[0]
	}

	passfile_name := os.Getenv("ENGINE_ROBOTS_PASSFILE_NAME")
	if passfile_name == "" {
		passfile_name = "passfile"
	}

	keyfile_path := fmt.Sprintf("%s/%s", secrets_dir, keyfile_name)
	keyfile_password_path := fmt.Sprintf("%s/%s", secrets_dir, passfile_name)

	return keyfile_path, keyfile_password_path, nil
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
