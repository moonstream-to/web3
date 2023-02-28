/*
Configurations for robots server.
*/
package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"
)

var (
	TERMINUS_CONTRACT_POLYGON_ADDRESS = os.Getenv("MOONSTREAM_TERMINUS_DIAMOND_CONTRACT_POLYGON_ADDRESS")
	TERMINUS_CONTRACT_MUMBAI_ADDRESS  = os.Getenv("MOONSTREAM_TERMINUS_DIAMOND_CONTRACT_MUMBAI_ADDRESS")
	TERMINUS_CONTRACT_CALDERA_ADDRESS = os.Getenv("MOONSTREAM_TERMINUS_DIAMOND_CONTRACT_CALDERA_ADDRESS")
)

type RobotsConfig struct {
	CollectionId           string `json:"collection_id"`
	SignerKeyfileName      string `json:"signer_keyfile_name"`
	SignerPasswordFileName string `json:"signer_password_file_name"`
	TerminusPoolId         int    `json:"terminus_pool_id"`
	ValueToClaim           int    `json:"value_to_claim"`
	Blockchain             string `json:"blockchain"`
}

func LoadConfig(configPath string) (*[]RobotsConfig, error) {
	rawBytes, err := ioutil.ReadFile(configPath)
	if err != nil {
		return nil, err
	}
	robotsConfigs := &[]RobotsConfig{}
	err = json.Unmarshal(rawBytes, robotsConfigs)
	if err != nil {
		return nil, err
	}
	return robotsConfigs, nil
}

type ConfigPlacement struct {
	ConfigDirPath   string
	ConfigDirExists bool

	ConfigPath   string
	ConfigExists bool
}

// CheckPathExists checks if path to file exists
func CheckPathExists(path string) (bool, error) {
	var exists = true
	_, err := os.Stat(path)
	if err != nil {
		if os.IsNotExist(err) {
			exists = false
		} else {
			return exists, fmt.Errorf("Error due checking file path exists, err: %v", err)
		}
	}

	return exists, nil
}

func PrepareConfigPlacement(providedPath string) (*ConfigPlacement, error) {
	var configDirPath, configPath string
	if providedPath == "" {
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return nil, fmt.Errorf("Unable to find user home directory, %v", err)
		}
		configDirPath = fmt.Sprintf("%s/.robots", homeDir)
		configPath = fmt.Sprintf("%s/config.json", configDirPath)
	} else {
		configPath = strings.TrimSuffix(providedPath, "/")
		configDirPath = filepath.Dir(configPath)
	}

	configDirPathExists, err := CheckPathExists(configDirPath)
	if err != nil {
		return nil, err
	}
	configPathExists, err := CheckPathExists(configPath)
	if err != nil {
		return nil, err
	}

	config := &ConfigPlacement{
		ConfigDirPath:   configDirPath,
		ConfigDirExists: configDirPathExists,

		ConfigPath:   configPath,
		ConfigExists: configPathExists,
	}

	return config, nil
}

// Generates empty list of robots configuration
func GenerateDefaultConfig(config *ConfigPlacement) error {
	if !config.ConfigDirExists {
		if err := os.MkdirAll(config.ConfigDirPath, os.ModePerm); err != nil {
			return fmt.Errorf("Unable to create directory, %v", err)
		}
		log.Printf("Config directory created at: %s", config.ConfigDirPath)
	}

	if !config.ConfigExists {
		tempConfig := []RobotsConfig{}
		tempConfigJson, err := json.Marshal(tempConfig)
		if err != nil {
			return fmt.Errorf("Unable to marshal configuration data, err: %v", err)
		}
		err = ioutil.WriteFile(config.ConfigPath, tempConfigJson, os.ModePerm)
		if err != nil {
			return fmt.Errorf("Unable to write default config to file %s, err: %v", config.ConfigPath, err)
		}
		log.Printf("Created default configuration at %s", config.ConfigPath)
	}

	return nil
}
