package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strconv"
	"strings"
)

type Input struct {
	Address string
	Amount  int64
}

type Output struct {
	SignedData map[string]string `json:"signed_data"`
}

func CheckPathExists(path string) (bool, error) {
	_, err := os.Stat(path)
	if err != nil {
		if !os.IsNotExist(err) {
			return false, fmt.Errorf("Error due checking file path exists, err: %v", err)
		}
		return false, fmt.Errorf("File with path %s does not exists", path)
	}
	return true, nil
}

func ParseInput(providedInput string, header bool) ([]Input, error) {
	// TODO(kompotkot): Support other filetypes and Stdin
	inputFilePath := strings.TrimSuffix(providedInput, "/")
	_, err := CheckPathExists(inputFilePath)
	if err != nil {
		return nil, err
	}

	inputBytes, err := ioutil.ReadFile(inputFilePath)
	if err != nil {
		return nil, fmt.Errorf("Unable to read %s file, err: %v", inputFilePath, err)
	}
	csvr := csv.NewReader(bytes.NewReader(inputBytes))
	csv, err := csvr.ReadAll()
	if err != nil {
		return nil, fmt.Errorf("Unable to parse csv file", err)
	}

	// Parse line in csv
	var startLine int
	if header {
		startLine = 1
	}
	var inputs []Input
	for _, line := range csv[startLine:] {
		amount, err := strconv.Atoi(line[1])
		if err != nil {
			log.Printf("Unable to parse amount %s to int, err: %v", line[1], err)
		}
		inputs = append(inputs, Input{Address: line[0], Amount: int64(amount)})
	}

	return inputs, nil
}

func ProcessOutput(output Output, outputPath string) error {
	outputStr, err := json.Marshal(output)
	if err != nil {
		return fmt.Errorf("Unable to marshal output, err: %v", err)
	}
	if outputPath == "" {
		fmt.Printf("%s", outputStr)
	} else {
		err := ioutil.WriteFile(outputPath, outputStr, 0600)
		if err != nil {
			return fmt.Errorf("Unable to write to file, err: %v", err)
		}
	}

	return nil
}
