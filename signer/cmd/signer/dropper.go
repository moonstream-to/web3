// Code generated - DO NOT EDIT.
// This file is a generated binding and any manual changes will be lost.
// abigen --abi=abi.json --pkg=dropper --out=dropper.go
package main

import (
	"errors"
	"math/big"
	"strings"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/event"
)

// Reference imports to suppress errors if they are not otherwise used.
var (
	_ = errors.New
	_ = big.NewInt
	_ = strings.NewReader
	_ = ethereum.NotFound
	_ = bind.Bind
	_ = common.Big1
	_ = types.BloomLookup
	_ = event.NewSubscription
)

// DropperMetaData contains all meta data concerning the Dropper contract.
var DropperMetaData = &bind.MetaData{
	ABI: "[{\"inputs\":[{\"internalType\":\"uint256\",\"name\":\"claimId\",\"type\":\"uint256\"},{\"internalType\":\"address\",\"name\":\"claimant\",\"type\":\"address\"},{\"internalType\":\"uint256\",\"name\":\"blockDeadline\",\"type\":\"uint256\"},{\"internalType\":\"uint256\",\"name\":\"amount\",\"type\":\"uint256\"}],\"name\":\"claimMessageHash\",\"outputs\":[{\"internalType\":\"bytes32\",\"name\":\"\",\"type\":\"bytes32\"}],\"stateMutability\":\"view\",\"type\":\"function\"}]",
}

// DropperABI is the input ABI used to generate the binding from.
// Deprecated: Use DropperMetaData.ABI instead.
var DropperABI = DropperMetaData.ABI

// Dropper is an auto generated Go binding around an Ethereum contract.
type Dropper struct {
	DropperCaller     // Read-only binding to the contract
	DropperTransactor // Write-only binding to the contract
	DropperFilterer   // Log filterer for contract events
}

// DropperCaller is an auto generated read-only Go binding around an Ethereum contract.
type DropperCaller struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// DropperTransactor is an auto generated write-only Go binding around an Ethereum contract.
type DropperTransactor struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// DropperFilterer is an auto generated log filtering Go binding around an Ethereum contract events.
type DropperFilterer struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// DropperSession is an auto generated Go binding around an Ethereum contract,
// with pre-set call and transact options.
type DropperSession struct {
	Contract     *Dropper          // Generic contract binding to set the session for
	CallOpts     bind.CallOpts     // Call options to use throughout this session
	TransactOpts bind.TransactOpts // Transaction auth options to use throughout this session
}

// DropperCallerSession is an auto generated read-only Go binding around an Ethereum contract,
// with pre-set call options.
type DropperCallerSession struct {
	Contract *DropperCaller // Generic contract caller binding to set the session for
	CallOpts bind.CallOpts  // Call options to use throughout this session
}

// DropperTransactorSession is an auto generated write-only Go binding around an Ethereum contract,
// with pre-set transact options.
type DropperTransactorSession struct {
	Contract     *DropperTransactor // Generic contract transactor binding to set the session for
	TransactOpts bind.TransactOpts  // Transaction auth options to use throughout this session
}

// DropperRaw is an auto generated low-level Go binding around an Ethereum contract.
type DropperRaw struct {
	Contract *Dropper // Generic contract binding to access the raw methods on
}

// DropperCallerRaw is an auto generated low-level read-only Go binding around an Ethereum contract.
type DropperCallerRaw struct {
	Contract *DropperCaller // Generic read-only contract binding to access the raw methods on
}

// DropperTransactorRaw is an auto generated low-level write-only Go binding around an Ethereum contract.
type DropperTransactorRaw struct {
	Contract *DropperTransactor // Generic write-only contract binding to access the raw methods on
}

// NewDropper creates a new instance of Dropper, bound to a specific deployed contract.
func NewDropper(address common.Address, backend bind.ContractBackend) (*Dropper, error) {
	contract, err := bindDropper(address, backend, backend, backend)
	if err != nil {
		return nil, err
	}
	return &Dropper{DropperCaller: DropperCaller{contract: contract}, DropperTransactor: DropperTransactor{contract: contract}, DropperFilterer: DropperFilterer{contract: contract}}, nil
}

// NewDropperCaller creates a new read-only instance of Dropper, bound to a specific deployed contract.
func NewDropperCaller(address common.Address, caller bind.ContractCaller) (*DropperCaller, error) {
	contract, err := bindDropper(address, caller, nil, nil)
	if err != nil {
		return nil, err
	}
	return &DropperCaller{contract: contract}, nil
}

// NewDropperTransactor creates a new write-only instance of Dropper, bound to a specific deployed contract.
func NewDropperTransactor(address common.Address, transactor bind.ContractTransactor) (*DropperTransactor, error) {
	contract, err := bindDropper(address, nil, transactor, nil)
	if err != nil {
		return nil, err
	}
	return &DropperTransactor{contract: contract}, nil
}

// NewDropperFilterer creates a new log filterer instance of Dropper, bound to a specific deployed contract.
func NewDropperFilterer(address common.Address, filterer bind.ContractFilterer) (*DropperFilterer, error) {
	contract, err := bindDropper(address, nil, nil, filterer)
	if err != nil {
		return nil, err
	}
	return &DropperFilterer{contract: contract}, nil
}

// bindDropper binds a generic wrapper to an already deployed contract.
func bindDropper(address common.Address, caller bind.ContractCaller, transactor bind.ContractTransactor, filterer bind.ContractFilterer) (*bind.BoundContract, error) {
	parsed, err := abi.JSON(strings.NewReader(DropperABI))
	if err != nil {
		return nil, err
	}
	return bind.NewBoundContract(address, parsed, caller, transactor, filterer), nil
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_Dropper *DropperRaw) Call(opts *bind.CallOpts, result *[]interface{}, method string, params ...interface{}) error {
	return _Dropper.Contract.DropperCaller.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_Dropper *DropperRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Dropper.Contract.DropperTransactor.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_Dropper *DropperRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _Dropper.Contract.DropperTransactor.contract.Transact(opts, method, params...)
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_Dropper *DropperCallerRaw) Call(opts *bind.CallOpts, result *[]interface{}, method string, params ...interface{}) error {
	return _Dropper.Contract.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_Dropper *DropperTransactorRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _Dropper.Contract.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_Dropper *DropperTransactorRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _Dropper.Contract.contract.Transact(opts, method, params...)
}

// ClaimMessageHash is a free data retrieval call binding the contract method 0x81b2e31c.
//
// Solidity: function claimMessageHash(uint256 claimId, address claimant, uint256 blockDeadline, uint256 amount) view returns(bytes32)
func (_Dropper *DropperCaller) ClaimMessageHash(opts *bind.CallOpts, claimId *big.Int, claimant common.Address, blockDeadline *big.Int, amount *big.Int) ([32]byte, error) {
	var out []interface{}
	err := _Dropper.contract.Call(opts, &out, "claimMessageHash", claimId, claimant, blockDeadline, amount)

	if err != nil {
		return *new([32]byte), err
	}

	out0 := *abi.ConvertType(out[0], new([32]byte)).(*[32]byte)

	return out0, err

}

// ClaimMessageHash is a free data retrieval call binding the contract method 0x81b2e31c.
//
// Solidity: function claimMessageHash(uint256 claimId, address claimant, uint256 blockDeadline, uint256 amount) view returns(bytes32)
func (_Dropper *DropperSession) ClaimMessageHash(claimId *big.Int, claimant common.Address, blockDeadline *big.Int, amount *big.Int) ([32]byte, error) {
	return _Dropper.Contract.ClaimMessageHash(&_Dropper.CallOpts, claimId, claimant, blockDeadline, amount)
}

// ClaimMessageHash is a free data retrieval call binding the contract method 0x81b2e31c.
//
// Solidity: function claimMessageHash(uint256 claimId, address claimant, uint256 blockDeadline, uint256 amount) view returns(bytes32)
func (_Dropper *DropperCallerSession) ClaimMessageHash(claimId *big.Int, claimant common.Address, blockDeadline *big.Int, amount *big.Int) ([32]byte, error) {
	return _Dropper.Contract.ClaimMessageHash(&_Dropper.CallOpts, claimId, claimant, blockDeadline, amount)
}
