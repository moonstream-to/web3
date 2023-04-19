package main

import (
	"encoding/hex"
	"testing"
)

func TestDropperClaimMessageHash(t *testing.T) {
	messageHash, err := DropperClaimMessageHash(80001, "0x4ec36E288E1b5d6914851a141cb041152Cf95328", "2", "5", "0x000000000000000000000000000000000000dEaD", "40000000", "3000000000000000000")
	if err != nil {
		t.Errorf("Unexpected error in DropperClaimMessageHash: %s", err.Error())
	}
	messageHashString := hex.EncodeToString(messageHash)

	// Taken from claimMessageHash method on the Moonstream Dropper v0.2.0 contract deployed at 0x4ec36E288E1b5d6914851a141cb041152Cf95328
	// on Polygon Mumbai testnet (chainId: 80001).
	expectedMessageHashString := "48033e41d47cd4cbfe7cd183e1c30ad6af92ea445475913bf96eed42d599bf20"

	if messageHashString != expectedMessageHashString {
		t.Errorf("Incorrect calculation of message hash for Dropper claim. expected: %s, actual: %s", expectedMessageHashString, messageHashString)
	}
}
