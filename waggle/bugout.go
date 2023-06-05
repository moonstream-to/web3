package main

// Much of this code is copied from waggle: https://github.com/bugout-dev/waggle/blob/main/main.go

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"

	bugout "github.com/bugout-dev/bugout-go/pkg"
	spire "github.com/bugout-dev/bugout-go/pkg/spire"
)

func CleanTimestamp(rawTimestamp string) string {
	return strings.ReplaceAll(rawTimestamp, " ", "T")
}

func GetCursorFromJournal(client *bugout.BugoutClient, token, journalID, cursorName string) (string, error) {
	query := fmt.Sprintf("context_type:waggle tag:type:cursor tag:cursor:%s", cursorName)
	parameters := map[string]string{
		"order":   "desc",
		"content": "true", // We may use the content in the future, even though we are simply using context_url right now
	}
	results, err := client.Spire.SearchEntries(token, journalID, query, 1, 0, parameters)
	if err != nil {
		return "", err
	}

	if results.TotalResults == 0 {
		return "", nil
	}

	return results.Results[0].ContextUrl, nil
}

func WriteCursorToJournal(client *bugout.BugoutClient, token, journalID, cursorName, cursor, queryTerms string) error {
	title := fmt.Sprintf("waggle cursor: %s", cursorName)
	entryContext := spire.EntryContext{
		ContextType: "waggle",
		ContextID:   cursor,
		ContextURL:  cursor,
	}
	tags := []string{
		"type:cursor",
		fmt.Sprintf("cursor:%s", cursorName),
		fmt.Sprintf("waggle_version:%s", WAGGLE_VERSION),
	}
	content := fmt.Sprintf("Cursor: %s at %s\nQuery: %s", cursorName, cursor, queryTerms)
	_, err := client.Spire.CreateEntry(token, journalID, title, content, tags, entryContext)
	return err
}

func ReportsIterator(client *bugout.BugoutClient, token, journalID, cursor, queryTerms string, limit, offset int) (spire.EntryResultsPage, error) {
	var query string = fmt.Sprintf("!tag:type:cursor %s", queryTerms)
	if cursor != "" {
		cleanedCursor := CleanTimestamp(cursor)
		query = fmt.Sprintf("%s created_at:>%s", query, cleanedCursor)
		fmt.Fprintln(os.Stderr, "query:", query)
	}
	parameters := map[string]string{
		"order":   "asc",
		"content": "false",
	}
	return client.Spire.SearchEntries(token, journalID, query, limit, offset, parameters)
}

func LoadDropperReports(searchResults spire.EntryResultsPage) ([]DropperClaimMessage, error) {
	reports := make([]DropperClaimMessage, len(searchResults.Results))
	for i, result := range searchResults.Results {
		parseErr := json.Unmarshal([]byte(result.Content), &reports[i])
		if parseErr != nil {
			return reports, parseErr
		}
	}
	return reports, nil
}

func DropperReportsToCSV(reports []DropperClaimMessage, header bool, w io.Writer) error {
	numRecords := len(reports)
	startIndex := 0
	if header {
		numRecords++
		startIndex++
	}

	records := make([][]string, numRecords)
	if header {
		records[0] = []string{
			"dropId", "requestID", "claimant", "blockDeadline", "amount", "signer", "signature",
		}
	}

	for i, report := range reports {
		records[i+startIndex] = []string{
			report.DropId,
			report.RequestID,
			report.Claimant,
			report.BlockDeadline,
			report.Amount,
			report.Signer,
			report.Signature,
		}
	}

	csvWriter := csv.NewWriter(w)
	return csvWriter.WriteAll(records)
}

func ProcessDropperClaims(client *bugout.BugoutClient, bugoutToken, journalID, cursorName, query string, batchSize int, header bool, w io.Writer) error {
	cursor, cursorErr := GetCursorFromJournal(client, bugoutToken, journalID, cursorName)
	if cursorErr != nil {
		return cursorErr
	}

	searchResults, searchErr := ReportsIterator(client, bugoutToken, journalID, cursor, query, batchSize, 0)
	if searchErr != nil {
		return searchErr
	}

	reports, loadErr := LoadDropperReports(searchResults)
	if loadErr != nil {
		return loadErr
	}

	writeErr := DropperReportsToCSV(reports, header, w)
	if writeErr != nil {
		return writeErr
	}

	var processedErr error
	if len(searchResults.Results) > 0 {
		processedErr = WriteCursorToJournal(client, bugoutToken, journalID, cursorName, searchResults.Results[len(searchResults.Results)-1].CreatedAt, query)
	}

	return processedErr
}
