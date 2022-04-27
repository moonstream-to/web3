/* Autogenerated file. Do not edit manually. */
/* tslint:disable */
/* eslint-disable */

import BN from "bn.js";
import { ContractOptions } from "web3-eth-contract";
import { EventLog } from "web3-core";
import { EventEmitter } from "events";
import {
  Callback,
  PayableTransactionObject,
  NonPayableTransactionObject,
  BlockType,
  ContractEventLog,
  BaseContract,
} from "./types";

export interface EventOptions {
  filter?: object;
  fromBlock?: BlockType;
  topics?: string[];
}

export type LootboxCreated = ContractEventLog<{
  lootboxId: string;
  0: string;
}>;
export type LootboxItemAdded = ContractEventLog<{
  lootboxId: string;
  lootboxItem: [string, string, string, string];
  0: string;
  1: [string, string, string, string];
}>;
export type LootboxItemRemoved = ContractEventLog<{
  lootboxId: string;
  lootboxItem: [string, string, string, string];
  0: string;
  1: [string, string, string, string];
}>;
export type LootboxOpened = ContractEventLog<{
  lootboxId: string;
  opener: string;
  lootboxItemCount: string;
  0: string;
  1: string;
  2: string;
}>;
export type OwnershipTransferred = ContractEventLog<{
  previousOwner: string;
  newOwner: string;
  0: string;
  1: string;
}>;
export type Paused = ContractEventLog<{
  account: string;
  0: string;
}>;
export type Unpaused = ContractEventLog<{
  account: string;
  0: string;
}>;

export interface Lootbox extends BaseContract {
  constructor(
    jsonInterface: any[],
    address?: string,
    options?: ContractOptions
  ): Lootbox;
  clone(): Lootbox;
  methods: {
    ERC1155_REWARD_TYPE(): NonPayableTransactionObject<string>;

    ERC20_REWARD_TYPE(): NonPayableTransactionObject<string>;

    addLootboxItem(
      lootboxId: number | string | BN,
      item: [
        number | string | BN,
        string,
        number | string | BN,
        number | string | BN
      ]
    ): NonPayableTransactionObject<void>;

    administratorPoolId(): NonPayableTransactionObject<string>;

    batchMintLootboxes(
      lootboxId: number | string | BN,
      toAddresses: string[],
      amounts: (number | string | BN)[]
    ): NonPayableTransactionObject<void>;

    batchMintLootboxesConstant(
      lootboxId: number | string | BN,
      toAddresses: string[],
      amount: number | string | BN
    ): NonPayableTransactionObject<void>;

    changeAdministratorPoolId(
      _administratorPoolId: number | string | BN
    ): NonPayableTransactionObject<void>;

    createLootbox(
      items: [
        number | string | BN,
        string,
        number | string | BN,
        number | string | BN
      ][]
    ): NonPayableTransactionObject<void>;

    createLootboxWithTerminusPool(
      items: [
        number | string | BN,
        string,
        number | string | BN,
        number | string | BN
      ][],
      terminusPoolId: number | string | BN
    ): NonPayableTransactionObject<void>;

    getLootboxBalance(
      lootboxId: number | string | BN,
      owner: string
    ): NonPayableTransactionObject<string>;

    getLootboxItemByIndex(
      lootboxId: number | string | BN,
      itemIndex: number | string | BN
    ): NonPayableTransactionObject<[string, string, string, string]>;

    getLootboxURI(
      lootboxId: number | string | BN
    ): NonPayableTransactionObject<string>;

    grantAdminRole(to: string): NonPayableTransactionObject<void>;

    lootboxIdbyTerminusPoolId(
      arg0: number | string | BN
    ): NonPayableTransactionObject<string>;

    lootboxItemCount(
      lootboxId: number | string | BN
    ): NonPayableTransactionObject<string>;

    mintLootbox(
      lootboxId: number | string | BN,
      recipient: string,
      amount: number | string | BN,
      data: string | number[]
    ): NonPayableTransactionObject<void>;

    onERC1155BatchReceived(
      arg0: string,
      arg1: string,
      arg2: (number | string | BN)[],
      arg3: (number | string | BN)[],
      arg4: string | number[]
    ): NonPayableTransactionObject<string>;

    onERC1155Received(
      arg0: string,
      arg1: string,
      arg2: number | string | BN,
      arg3: number | string | BN,
      arg4: string | number[]
    ): NonPayableTransactionObject<string>;

    openLootbox(
      lootboxId: number | string | BN,
      count: number | string | BN
    ): NonPayableTransactionObject<void>;

    owner(): NonPayableTransactionObject<string>;

    pause(): NonPayableTransactionObject<void>;

    paused(): NonPayableTransactionObject<boolean>;

    removeLootboxItem(
      lootboxId: number | string | BN,
      itemIndex: number | string | BN
    ): NonPayableTransactionObject<void>;

    renounceOwnership(): NonPayableTransactionObject<void>;

    revokeAdminRole(from: string): NonPayableTransactionObject<void>;

    setLootboxURI(
      lootboxId: number | string | BN,
      uri: string
    ): NonPayableTransactionObject<void>;

    supportsInterface(
      interfaceId: string | number[]
    ): NonPayableTransactionObject<boolean>;

    surrenderTerminusControl(): NonPayableTransactionObject<void>;

    surrenderTerminusPools(
      poolIds: (number | string | BN)[]
    ): NonPayableTransactionObject<void>;

    terminusAddress(): NonPayableTransactionObject<string>;

    terminusPoolIdbyLootboxId(
      arg0: number | string | BN
    ): NonPayableTransactionObject<string>;

    totalLootboxCount(): NonPayableTransactionObject<string>;

    transferOwnership(newOwner: string): NonPayableTransactionObject<void>;

    unpause(): NonPayableTransactionObject<void>;

    withdrawERC1155(
      tokenAddress: string,
      tokenId: number | string | BN,
      amount: number | string | BN
    ): NonPayableTransactionObject<void>;

    withdrawERC20(
      tokenAddress: string,
      amount: number | string | BN
    ): NonPayableTransactionObject<void>;
  };
  events: {
    LootboxCreated(cb?: Callback<LootboxCreated>): EventEmitter;
    LootboxCreated(
      options?: EventOptions,
      cb?: Callback<LootboxCreated>
    ): EventEmitter;

    LootboxItemAdded(cb?: Callback<LootboxItemAdded>): EventEmitter;
    LootboxItemAdded(
      options?: EventOptions,
      cb?: Callback<LootboxItemAdded>
    ): EventEmitter;

    LootboxItemRemoved(cb?: Callback<LootboxItemRemoved>): EventEmitter;
    LootboxItemRemoved(
      options?: EventOptions,
      cb?: Callback<LootboxItemRemoved>
    ): EventEmitter;

    LootboxOpened(cb?: Callback<LootboxOpened>): EventEmitter;
    LootboxOpened(
      options?: EventOptions,
      cb?: Callback<LootboxOpened>
    ): EventEmitter;

    OwnershipTransferred(cb?: Callback<OwnershipTransferred>): EventEmitter;
    OwnershipTransferred(
      options?: EventOptions,
      cb?: Callback<OwnershipTransferred>
    ): EventEmitter;

    Paused(cb?: Callback<Paused>): EventEmitter;
    Paused(options?: EventOptions, cb?: Callback<Paused>): EventEmitter;

    Unpaused(cb?: Callback<Unpaused>): EventEmitter;
    Unpaused(options?: EventOptions, cb?: Callback<Unpaused>): EventEmitter;

    allEvents(options?: EventOptions, cb?: Callback<EventLog>): EventEmitter;
  };

  once(event: "LootboxCreated", cb: Callback<LootboxCreated>): void;
  once(
    event: "LootboxCreated",
    options: EventOptions,
    cb: Callback<LootboxCreated>
  ): void;

  once(event: "LootboxItemAdded", cb: Callback<LootboxItemAdded>): void;
  once(
    event: "LootboxItemAdded",
    options: EventOptions,
    cb: Callback<LootboxItemAdded>
  ): void;

  once(event: "LootboxItemRemoved", cb: Callback<LootboxItemRemoved>): void;
  once(
    event: "LootboxItemRemoved",
    options: EventOptions,
    cb: Callback<LootboxItemRemoved>
  ): void;

  once(event: "LootboxOpened", cb: Callback<LootboxOpened>): void;
  once(
    event: "LootboxOpened",
    options: EventOptions,
    cb: Callback<LootboxOpened>
  ): void;

  once(event: "OwnershipTransferred", cb: Callback<OwnershipTransferred>): void;
  once(
    event: "OwnershipTransferred",
    options: EventOptions,
    cb: Callback<OwnershipTransferred>
  ): void;

  once(event: "Paused", cb: Callback<Paused>): void;
  once(event: "Paused", options: EventOptions, cb: Callback<Paused>): void;

  once(event: "Unpaused", cb: Callback<Unpaused>): void;
  once(event: "Unpaused", options: EventOptions, cb: Callback<Unpaused>): void;
}