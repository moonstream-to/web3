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
	Address            string
	Amount             int64
	ClaimBlockDeadline int64
}

type Claimant struct {
	ClaimantAddress    string `json:"claimant_address"`
	Amount             int64  `json:"amount"`
	Signature          string `json:"signature"`
	ClaimBlockDeadline int64  `json:"claim_block_deadline"`
	ClaimId            int64  `json:"claim_id"`
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
			log.Printf("Unable to parse amount %s to int for addr %s, err: %v", line[1], line[0], err)
			continue
		}
		claimBlockDeadline, err := strconv.Atoi(line[2])
		if err != nil {
			log.Printf("Unable to parse claimBlockDeadline %s to int for addr %s, err: %v", line[2], line[0], err)
			continue
		}
		inputs = append(inputs, Input{Address: line[0], Amount: int64(amount), ClaimBlockDeadline: int64(claimBlockDeadline)})
	}

	return inputs, nil
}

func ProcessOutput(claimants []Claimant, outputPath, outputFileType string) (string, error) {
	var err error
	var outputBytes []byte
	if outputFileType == "json" {
		outputBytes, err = json.Marshal(claimants)
		if err != nil {
			return "", fmt.Errorf("Unable to marshal output, err: %v", err)
		}
	}
	if outputFileType == "csv" {
		for _, claimant := range claimants {
			row := fmt.Sprintf(
				"%s,%d,%s,%d,%d\n",
				claimant.ClaimantAddress, claimant.Amount, claimant.Signature, claimant.ClaimBlockDeadline, claimant.ClaimId,
			)
			outputBytes = append(outputBytes, row...)
		}
	}

	err = ioutil.WriteFile(fmt.Sprintf("%s.%s", outputPath, outputFileType), outputBytes, 0600)
	if err != nil {
		return "", fmt.Errorf("Unable to write to file, err: %v", err)
	}

	return fmt.Sprintf("%s.%s", outputPath, outputFileType), nil
}
