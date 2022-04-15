// import { TerminusFacet } from "../../../types/contracts/TerminusFacet";
// import { BaseContract } from "../../../types/contracts/types";
// import { OwnershipFacet } from "../../../types/contracts/OwnershipFacet";

// import Web3 from "web3";

// export const getTerminusFacetState =
//   (contracts: { ownershipFacet: BaseContract; terminusFacet: BaseContract }) =>
//   async () => {
//     console.log("gert terminusFacetState");
//     const terminusFacet = contracts.terminusFacet as TerminusFacet;
//     const ownershipFacet = contracts.ownershipFacet as OwnershipFacet;
//     console.dir(contracts.terminusFacet);
//     const poolBasePrice = await terminusFacet.methods.poolBasePrice().call();
//     const paymentToken = await terminusFacet.methods.paymentToken().call();
//     const contractURI = await terminusFacet.methods.contractURI().call();
//     const totalPools = await terminusFacet.methods.totalPools().call();
//     const owner = await ownershipFacet.methods.owner().call();
//     // const controller = await terminusFacet.methods.terminusController().call();
//     // let numberOfOwnedPools = "0";
//     // let ownedPoolIds = [];
//     // if (account) {
//     //   numberOfOwnedPools = await terminusFacet.methods
//     //     .totalPoolsByOwner(account)
//     //     .call();

//     //   if (numberOfOwnedPools !== "0") {
//     //     const n = new Number(numberOfOwnedPools);
//     //     for (let i = 0; i < n; i++) {
//     //       const poolId = await terminusFacet.methods
//     //         .poolOfOwnerByIndex(account, i)
//     //         .call();
//     //       const poolOwner: any = await terminusFacet.methods
//     //         .terminusPoolController(poolId)
//     //         .call();

//     //       if (poolOwner === account) {
//     //         ownedPoolIds.push(poolId);
//     //       }
//     //     }
//     //   }

//     // }
//     // const web3 = new Web3(
//     //   `https://mainnet.infura.io/v3/6e9a55a6a5664c4a84335d68d9f5a727`
//     // );
//     // const allEvents = await terminusFacet.getPastEvents("allEvents");

//     // const blockNumber = await web3.eth.getBlockNumber();
//     // console.log("block number: ", blockNumber);
//     // const pastPoolControlTransferred = await terminusFacet.getPastEvents(
//     //   "allEvents",
//     //   { fromBlock: 26051378 - 175, toBlock: 26051378 + 175 }
//     // );
//     // console.dir(pastPoolControlTransferred);
//     // console.log("poolBasePrice:", poolBasePrice);
//     // console.log("totalPools", totalPools);

//     // while (0) {}

//     return {
//       poolBasePrice,
//       paymentToken,
//       contractURI,
//       totalPools,
//       // numberOfOwnedPools,
//       // ownedPoolIds,
//       owner,
//       // controller,
//     };
//   };

// export const getTerminusFacetPoolState =
//   (contract: BaseContract, poolId: string) => async () => {
//     const terminusFacet = contract as TerminusFacet;
//     const controller = await terminusFacet.methods
//       .terminusPoolController(poolId)
//       .call();
//     const supply = await terminusFacet.methods
//       .terminusPoolSupply(poolId)
//       .call();
//     const uri = await terminusFacet.methods.uri(poolId).call();
//     const capacity = await terminusFacet.methods
//       .terminusPoolCapacity(poolId)
//       .call();

//     return { controller, supply, uri, capacity };
//   };

// export const createSimplePool =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     capacity,
//     transactionConfig,
//   }: {
//     capacity: string;
//     transactionConfig?: any;
//   }) => {
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     console.debug("txConfig", txConfig);
//     const response = await terminusFacet.methods
//       .createSimplePool(capacity)
//       .send(txConfig);
//     return response;
//   };

// export const mintNewAccessToken =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     to,
//     poolId,
//     amount,
//     transactionConfig,
//   }: {
//     to: string;
//     amount: number;
//     poolId: string;
//     transactionConfig?: any;
//   }) => {
//     const web3 = new Web3();
//     console.debug("mintNewAccessToken", to, amount, poolId);
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     console.debug("address", to);
//     const response = await terminusFacet.methods
//       .mint(web3.utils.toChecksumAddress(to), poolId, amount, "asd")
//       .send(txConfig);
//     return response;
//   };

// export const transferTerminusOwnership =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     newOwner,
//     transactionConfig,
//   }: {
//     newOwner: string;
//     transactionConfig?: any;
//   }) => {
//     const ownershipFacet = contract as OwnershipFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await ownershipFacet.methods
//       .transferOwnership(newOwner)
//       .send(txConfig);
//     return response;
//   };

// export const setController =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     newController,
//     transactionConfig,
//   }: {
//     newController: string;
//     transactionConfig?: any;
//   }) => {
//     const web3 = new Web3();
//     const terminus = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await terminus.methods
//       .setController(web3.utils.toChecksumAddress(newController))
//       .send(txConfig);
//     return response;
//   };

// export const withrawTerminusFunds =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     toAddress,
//     amount,
//     transactionConfig,
//   }: {
//     toAddress: string;
//     amount: string;
//     transactionConfig?: any;
//   }) => {
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await terminusFacet.methods
//       .withdrawPayments(toAddress, amount)
//       .send(txConfig);
//     return response;
//   };

// export const setTerminusPoolBasePrice =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     newPoolBasePrice,
//     transactionConfig,
//   }: {
//     newPoolBasePrice: string;
//     transactionConfig?: any;
//   }) => {
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await terminusFacet.methods
//       .setPoolBasePrice(newPoolBasePrice)
//       .send(txConfig);
//     return response;
//   };

// export const setTerminusURI =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     newURI,
//     transactionConfig,
//   }: {
//     newURI: string;
//     transactionConfig?: any;
//   }) => {
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await terminusFacet.methods
//       .setContractURI(newURI)
//       .send(txConfig);
//     return response;
//   };

// export const setTerminusPoolURI =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async (args: {
//     poolURI: string;
//     poolId: string;
//     transactionConfig?: any;
//   }) => {
//     console.debug("setTerminusPoolURI", args.poolURI);
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...args.transactionConfig };
//     const response = await terminusFacet.methods
//       .setURI(args.poolId, args.poolURI)
//       .send(txConfig);
//     return response;
//   };

// export const setTerminusPaymentToken =
//   (contract: BaseContract, defaultTxConfig: any) =>
//   async ({
//     paymentTokenAddress,
//     transactionConfig,
//   }: {
//     paymentTokenAddress: string;
//     transactionConfig?: any;
//   }) => {
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await terminusFacet.methods
//       .setPaymentToken(paymentTokenAddress)
//       .send(txConfig);
//     return response;
//   };

// export const setTerminusPoolController =
//   (contract: BaseContract, poolId: string, defaultTxConfig: any) =>
//   async ({
//     newController,
//     transactionConfig,
//   }: {
//     newController: string;
//     transactionConfig?: any;
//   }) => {
//     const web3 = new Web3();
//     const terminusFacet = contract as TerminusFacet;
//     const txConfig = { ...defaultTxConfig, ...transactionConfig };
//     const response = await terminusFacet.methods
//       .setPoolController(poolId, web3.utils.toChecksumAddress(newController))
//       .send(txConfig);
//     return response;
//   };
