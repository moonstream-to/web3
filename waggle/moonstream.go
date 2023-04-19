package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"time"
)

type RegisteredContract struct {
	Id               string    `json:"id"`
	Blockchain       string    `json:"blockchain"`
	Address          string    `json:"address"`
	ContractType     string    `json:"contract_type"`
	MoonstreamUserId string    `json:"moonstream_user_id"`
	Title            string    `json:"title"`
	Description      string    `json:"description"`
	ImageURI         string    `json:"image_uri"`
	CreatedAt        time.Time `json:"created_at"`
	UpdatedAt        time.Time `json:"updated_at"`
}

type CallRequest struct {
	Id                   string      `json:"id"`
	RegisteredContractId string      `json:"registered_contract_id"`
	MoonstreamUserId     string      `json:"moonstream_user_id"`
	Caller               string      `json:"caller"`
	Method               string      `json:"method"`
	Parameters           interface{} `json:"parameters"`
	ExpiresAt            time.Time   `json:"expires_at"`
	CreatedAt            time.Time   `json:"created_at"`
	UpdateAt             time.Time   `json:"updated_at"`
}

type CallRequestSpecification struct {
	Caller     string      `json:"caller"`
	Method     string      `json:"method"`
	Parameters interface{} `json:"parameters"`
}

type CreateCallRequestsRequest struct {
	TTLDays        int                        `json:"ttl_days"`
	Specifications []CallRequestSpecification `json:"specifications"`
}

type DropperCallRequestParameters struct {
	DropId        string `json:"dropId"`
	RequestID     string `json:"requestID"`
	BlockDeadline string `json:"blockDeadline"`
	Amount        string `json:"amount"`
	Signer        string `json:"signer"`
	Signature     string `json:"signature"`
}

type MoonstreamEngineAPIClient struct {
	AccessToken string
	BaseURL     string
	HTTPClient  *http.Client
}

func ClientFromEnv() (*MoonstreamEngineAPIClient, error) {
	accessToken := os.Getenv("MOONSTREAM_ENGINE_ACCESS_TOKEN")

	if accessToken == "" {
		return nil, fmt.Errorf("set the MOONSTREAM_ENGINE_ACCESS_TOKEN environment variable")
	}
	baseURL := os.Getenv("MOONSTREAM_ENGINE_BASE_URL")
	if baseURL == "" {
		baseURL = "https://engineapi.moonstream.to"
	}
	timeoutSecondsRaw := os.Getenv("MOONSTREAM_ENGINE_TIMEOUT_SECONDS")
	if timeoutSecondsRaw == "" {
		timeoutSecondsRaw = "30"
	}
	timeoutSeconds, conversionErr := strconv.Atoi(timeoutSecondsRaw)
	if conversionErr != nil {
		return nil, conversionErr
	}
	timeout := time.Duration(timeoutSeconds) * time.Second
	httpClient := http.Client{Timeout: timeout}

	return &MoonstreamEngineAPIClient{
		AccessToken: accessToken,
		BaseURL:     baseURL,
		HTTPClient:  &httpClient,
	}, nil
}

func (client *MoonstreamEngineAPIClient) ListRegisteredContracts(blockchain, address, contractType string, limit, offset int) ([]RegisteredContract, error) {
	var contracts []RegisteredContract

	request, requestCreationErr := http.NewRequest("GET", fmt.Sprintf("%s/contracts/", client.BaseURL), nil)
	if requestCreationErr != nil {
		return contracts, requestCreationErr
	}

	request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", client.AccessToken))
	request.Header.Add("Accept", "application/json")

	queryParameters := request.URL.Query()
	if blockchain != "" {
		queryParameters.Add("blockchain", blockchain)
	}
	if address != "" {
		queryParameters.Add("address", address)
	}
	if contractType != "" {
		queryParameters.Add("contract_type", contractType)
	}
	queryParameters.Add("limit", strconv.Itoa(limit))
	queryParameters.Add("offset", strconv.Itoa(offset))

	request.URL.RawQuery = queryParameters.Encode()

	response, responseErr := client.HTTPClient.Do(request)
	if responseErr != nil {
		return contracts, responseErr
	}
	defer response.Body.Close()

	responseBody, responseBodyErr := ioutil.ReadAll(response.Body)

	if response.StatusCode < 200 || response.StatusCode >= 300 {
		if responseBodyErr != nil {
			return contracts, fmt.Errorf("unexpected status code: %d -- could not read response body: %s", response.StatusCode, responseBodyErr.Error())
		}
		responseBodyString := string(responseBody)
		return contracts, fmt.Errorf("unexpected status code: %d -- response body: %s", response.StatusCode, responseBodyString)
	}

	if responseBodyErr != nil {
		return contracts, fmt.Errorf("could not read response body: %s", responseBodyErr.Error())
	}

	unmarshalErr := json.Unmarshal(responseBody, &contracts)
	if unmarshalErr != nil {
		return contracts, fmt.Errorf("could not parse response body: %s", unmarshalErr.Error())
	}

	return contracts, nil
}

func (client *MoonstreamEngineAPIClient) ListCallRequests(contractId, caller string, limit, offset int) ([]CallRequest, error) {
	var callRequests []CallRequest

	request, requestCreationErr := http.NewRequest("GET", fmt.Sprintf("%s/contracts/requests", client.BaseURL), nil)
	if requestCreationErr != nil {
		return callRequests, requestCreationErr
	}

	request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", client.AccessToken))
	request.Header.Add("Accept", "application/json")

	queryParameters := request.URL.Query()
	queryParameters.Add("contract_id", contractId)
	queryParameters.Add("caller", caller)
	queryParameters.Add("limit", strconv.Itoa(limit))
	queryParameters.Add("offset", strconv.Itoa(offset))

	request.URL.RawQuery = queryParameters.Encode()

	response, responseErr := client.HTTPClient.Do(request)
	if responseErr != nil {
		return callRequests, responseErr
	}
	defer response.Body.Close()

	responseBody, responseBodyErr := ioutil.ReadAll(response.Body)

	if response.StatusCode < 200 || response.StatusCode >= 300 {
		if responseBodyErr != nil {
			return callRequests, fmt.Errorf("unexpected status code: %d -- could not read response body: %s", response.StatusCode, responseBodyErr.Error())
		}
		responseBodyString := string(responseBody)
		return callRequests, fmt.Errorf("unexpected status code: %d -- response body: %s", response.StatusCode, responseBodyString)
	}

	if responseBodyErr != nil {
		return callRequests, fmt.Errorf("could not read response body: %s", responseBodyErr.Error())
	}

	unmarshalErr := json.Unmarshal(responseBody, &callRequests)
	if unmarshalErr != nil {
		return callRequests, fmt.Errorf("could not parse response body: %s", unmarshalErr.Error())
	}

	return callRequests, nil
}

func (client *MoonstreamEngineAPIClient) CreateCallRequests(contractId string, ttlDays int, spec []CallRequestSpecification) error {
	requestBody := CreateCallRequestsRequest{
		TTLDays:        ttlDays,
		Specifications: spec,
	}

	requestBodyBytes, requestBodyBytesErr := json.Marshal(requestBody)
	if requestBodyBytesErr != nil {
		return requestBodyBytesErr
	}

	request, requestCreationErr := http.NewRequest("POST", fmt.Sprintf("%s/contracts/%s/requests", client.BaseURL, contractId), bytes.NewBuffer(requestBodyBytes))
	if requestCreationErr != nil {
		return requestCreationErr
	}

	request.Header.Add("Authorization", fmt.Sprintf("Bearer %s", client.AccessToken))
	request.Header.Add("Accept", "application/json")
	request.Header.Add("Content-Type", "application/json")

	response, responseErr := client.HTTPClient.Do(request)
	if responseErr != nil {
		return responseErr
	}
	defer response.Body.Close()

	responseBody, responseBodyErr := ioutil.ReadAll(response.Body)

	if response.StatusCode < 200 || response.StatusCode >= 300 {
		if responseBodyErr != nil {
			return fmt.Errorf("unexpected status code: %d -- could not read response body: %s", response.StatusCode, responseBodyErr.Error())
		}
		responseBodyString := string(responseBody)
		return fmt.Errorf("unexpected status code: %d -- response body: %s", response.StatusCode, responseBodyString)
	}

	return nil
}
