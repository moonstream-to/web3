import React, { useContext, useEffect } from "react";
import { getLayout } from "moonstream-components/src/layoutsForPlay/EngineLayout";
import {
  Flex,
  Center,
  Badge,
  Spacer,
  Image,
  Spinner,
  Box,
  Text,
  Stack,
  Input,
  InputGroup,
  InputRightElement,
  FormLabel,
  FormControl,
  FormErrorMessage,
  Button,
  HStack,
} from "@chakra-ui/react";

import { useRouter } from "../../../../../packages/moonstream-components/src/core/hooks";
const StashABI = require("../../../games/cu/StashABI.json");
import { StashABI as StashABIType } from "../../../games/cu/StashABI";
const GameBankABI = require("../../../games/cu/GameBankABI.json");
import { GameBankABI as GameBankABIType } from "../../../games/cu/GameBankABI";
const ERC721MetadataABI = require("../../../../../abi/MockERC721.json");
import { MockERC721 } from "../../../../../types/contracts/MockERC721";

import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { supportedChains } from "../../../../../types/Moonstream";
import { useERC20, useToast } from "moonstream-components/src/core/hooks";
import { useMutation, useQuery } from "react-query";
import { DEFAULT_METATAGS } from "../../../src/constants";
import {
  MAX_INT,
  chainByChainId,
} from "moonstream-components/src/core/providers/Web3Provider";
import LootboxCard from "../../../../../packages/moonstream-components/src/components/CryptoUnicorns/LootboxCardPlay";
import { MockTerminus as TerminusFacet } from "../../../../../types/contracts/MockTerminus";
import { hookCommon } from "moonstream-components/src/core/hooks";

const terminusAbi = require("../../../../../abi/MockTerminus.json");

const GameBankAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x762aF8cbE298bbFE568BBB6709f854A01c07333D",
  polygon: "0x94f557dDdb245b11d031F57BA7F2C4f28C4A203e",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const TerminusAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x19e812EdB24B68A8F3AbF5e4C82d10AfEf1641Db",
  polygon: "0x99A558BDBdE247C2B2716f0D4cFb0E246DFB697D",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const UNIMAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x47d0f0BD94188e3f8c6fF2C0B1Bf7D6D8BED7534",
  polygon: "0x64060aB139Feaae7f06Ca4E63189D86aDEb51691",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const RBWAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x4Df452487E6c9d0C3Dc5EB4936244F8572b3F0b6",
  polygon: "0x431CD3C9AC9Fc73644BF68bF5691f4B83F9E104f",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

// const MulticallAddresses: { [key in supportedChains]: string } = {
//   mumbai: "0xe9939e7Ea7D7fb619Ac57f648Da7B1D425832631",
//   polygon: "0xc8E51042792d7405184DfCa245F2d27B94D013b6",
//   ethereum: "0x0000000000000000000000000000000000000000",
//   localhost: "0x0000000000000000000000000000000000000000",
// };

const UnicornsAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x39858b1A4e48CfFB1019F0A15ff54899213B3f8b",
  polygon: "0xdC0479CC5BbA033B3e7De9F178607150B3AbCe1f",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const LandsAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x230E4e85d4549343A460F5dE0a7035130F62d74C",
  polygon: "0xA2a13cE1824F3916fC84C65e559391fc6674e6e8",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

const ShadowcornsAddresses: { [key in supportedChains]: string } = {
  mumbai: "0x8819CFdb4Fd6Ba0464Ef2283F5F621443B7eC2F4",
  polygon: "0xa7D50EE3D7485288107664cf758E877a0D351725",
  ethereum: "0x0000000000000000000000000000000000000000",
  localhost: "0x0000000000000000000000000000000000000000",
};

//keystonePoolIdByLandType
// Land type: 1, 62       // mythic
// Land type: 2, 59       // light
// Land type: 3, 66       // wonder
// Land type: 4, 61       // mystery
// Land type: 5, 58       // heart
// Land type: 6, 55       // cloud
// Land type: 7, 57       // flower
// Land type: 8, 54       // candy
// Land type: 9, 56       // crystal
// Land type: 10, 60      // moon
// Land type: 11, 64      // rainbow
// Land type: 12, 63      // omnom
// Land type: 13, 65      // star

type terminusType =
  | "commonLootbox"
  | "rareLootbox"
  | "mythicLootbox"
  | "landLootbox"
  | "mysteryLootbox"
  | "RMPLootbox"
  | "goldenTicket"
  | "mythicKeystone"
  | "lightKeystone"
  | "wonderKeystone"
  | "mysteryKeystone"
  | "heartKeystone"
  | "cloudKeystone"
  | "flowerKeystone"
  | "candyKeystone"
  | "crystalKeystone"
  | "moonKeystone"
  | "rainbowKeystone"
  | "omnomKeystone"
  | "starKeystone"
  | "commonShadowcornEgg"
  | "rareShadowcornEgg"
  | "mythicShadowcornEgg"
  | "shadowcornTierOne"
  | "shadowcornTierTwo"
  | "shadowcornTierThree"
  | "nurseryTierOne"
  | "nurseryTierTwo"
  | "nurseryTierThree"
  | "iSurvivedLaunch"
  | "founders"
  | "communityCouncil"
  | "summerOfLoveTier1"
  | "summerOfLoveTier2"
  | "summerOfLoveTier3"
  | "fireShadowcornLootbox"
  | "slimeShadowcornLootbox"
  | "soulShadowcornLootbox"
  | "voltShadowcornLootbox"
  | "nebulaShadowcornLootbox";

interface LootboxInfo {
  poolIdByChain: {
    [key in supportedChains]: number;
  };
}

// TODO: Using an Enum here would make this less clumsy. The Enum defines a type *and* a value.
const terminusTypes: terminusType[] = [
  "commonLootbox",
  "rareLootbox",
  "mythicLootbox",
  "landLootbox",
  "mysteryLootbox",
  "RMPLootbox",
  "goldenTicket",
  "mythicKeystone",
  "lightKeystone",
  "wonderKeystone",
  "mysteryKeystone",
  "heartKeystone",
  "cloudKeystone",
  "flowerKeystone",
  "candyKeystone",
  "crystalKeystone",
  "moonKeystone",
  "rainbowKeystone",
  "omnomKeystone",
  "starKeystone",
  "commonShadowcornEgg",
  "rareShadowcornEgg",
  "mythicShadowcornEgg",
  "shadowcornTierOne",
  "shadowcornTierTwo",
  "shadowcornTierThree",
  "nurseryTierOne",
  "nurseryTierTwo",
  "nurseryTierThree",
  "iSurvivedLaunch",
  "founders",
  "communityCouncil",
  "summerOfLoveTier1",
  "summerOfLoveTier2",
  "summerOfLoveTier3",
  "fireShadowcornLootbox",
  "slimeShadowcornLootbox",
  "soulShadowcornLootbox",
  "voltShadowcornLootbox",
  "nebulaShadowcornLootbox",
];

const terminusInfo: { [key in terminusType]: LootboxInfo } = {
  commonLootbox: {
    poolIdByChain: {
      mumbai: 6,
      polygon: 4,
      ethereum: -1,
      localhost: -1,
    },
  },
  rareLootbox: {
    poolIdByChain: {
      mumbai: 7,
      polygon: 5,
      ethereum: -1,
      localhost: -1,
    },
  },
  mythicLootbox: {
    poolIdByChain: {
      mumbai: 8,
      polygon: 6,
      ethereum: -1,
      localhost: -1,
    },
  },
  mysteryLootbox: {
    poolIdByChain: {
      mumbai: 11,
      polygon: 51,
      ethereum: -1,
      localhost: -1,
    },
  },
  RMPLootbox: {
    poolIdByChain: {
      mumbai: 12,
      polygon: 52,
      ethereum: -1,
      localhost: -1,
    },
  },
  landLootbox: {
    poolIdByChain: {
      mumbai: 26,
      polygon: 46,
      ethereum: -1,
      localhost: -1,
    },
  },
  goldenTicket: {
    poolIdByChain: {
      mumbai: 10,
      polygon: 42,
      ethereum: -1,
      localhost: -1,
    },
  },
  mythicKeystone: {
    poolIdByChain: {
      mumbai: 21,
      polygon: 62,
      ethereum: -1,
      localhost: -1,
    },
  },
  lightKeystone: {
    poolIdByChain: {
      mumbai: 18,
      polygon: 59,
      ethereum: -1,
      localhost: -1,
    },
  },
  wonderKeystone: {
    poolIdByChain: {
      mumbai: 25,
      polygon: 66,
      ethereum: -1,
      localhost: -1,
    },
  },
  mysteryKeystone: {
    poolIdByChain: {
      mumbai: 20,
      polygon: 61,
      ethereum: -1,
      localhost: -1,
    },
  },
  heartKeystone: {
    poolIdByChain: {
      mumbai: 17,
      polygon: 58,
      ethereum: -1,
      localhost: -1,
    },
  },
  cloudKeystone: {
    poolIdByChain: {
      mumbai: 14,
      polygon: 55,
      ethereum: -1,
      localhost: -1,
    },
  },
  flowerKeystone: {
    poolIdByChain: {
      mumbai: 16,
      polygon: 57,
      ethereum: -1,
      localhost: -1,
    },
  },
  candyKeystone: {
    poolIdByChain: {
      mumbai: 13,
      polygon: 54,
      ethereum: -1,
      localhost: -1,
    },
  },
  crystalKeystone: {
    poolIdByChain: {
      mumbai: 15,
      polygon: 56,
      ethereum: -1,
      localhost: -1,
    },
  },
  moonKeystone: {
    poolIdByChain: {
      mumbai: 19,
      polygon: 60,
      ethereum: -1,
      localhost: -1,
    },
  },
  rainbowKeystone: {
    poolIdByChain: {
      mumbai: 23,
      polygon: 64,
      ethereum: -1,
      localhost: -1,
    },
  },
  omnomKeystone: {
    poolIdByChain: {
      mumbai: 22,
      polygon: 63,
      ethereum: -1,
      localhost: -1,
    },
  },
  starKeystone: {
    poolIdByChain: {
      mumbai: 24,
      polygon: 65,
      ethereum: -1,
      localhost: -1,
    },
  },
  commonShadowcornEgg: {
    poolIdByChain: {
      mumbai: 5,
      polygon: 1,
      ethereum: -1,
      localhost: -1,
    },
  },
  rareShadowcornEgg: {
    poolIdByChain: {
      mumbai: 4,
      polygon: 2,
      ethereum: -1,
      localhost: -1,
    },
  },
  mythicShadowcornEgg: {
    poolIdByChain: {
      mumbai: 3,
      polygon: 3,
      ethereum: -1,
      localhost: -1,
    },
  },
  shadowcornTierOne: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 43,
      ethereum: -1,
      localhost: -1,
    },
  },
  shadowcornTierTwo: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 44,
      ethereum: -1,
      localhost: -1,
    },
  },
  shadowcornTierThree: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 45,
      ethereum: -1,
      localhost: -1,
    },
  },
  nurseryTierOne: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 47,
      ethereum: -1,
      localhost: -1,
    },
  },
  nurseryTierTwo: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 48,
      ethereum: -1,
      localhost: -1,
    },
  },
  nurseryTierThree: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 49,
      ethereum: -1,
      localhost: -1,
    },
  },
  iSurvivedLaunch: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 50,
      ethereum: -1,
      localhost: -1,
    },
  },
  founders: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 41,
      ethereum: -1,
      localhost: -1,
    },
  },
  communityCouncil: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 53,
      ethereum: -1,
      localhost: -1,
    },
  },
  summerOfLoveTier1: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 67,
      ethereum: -1,
      localhost: -1,
    },
  },
  summerOfLoveTier2: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 68,
      ethereum: -1,
      localhost: -1,
    },
  },
  summerOfLoveTier3: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 69,
      ethereum: -1,
      localhost: -1,
    },
  },
  fireShadowcornLootbox: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 75,
      ethereum: -1,
      localhost: -1,
    },
  },
  slimeShadowcornLootbox: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 77,
      ethereum: -1,
      localhost: -1,
    },
  },
  soulShadowcornLootbox: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 78,
      ethereum: -1,
      localhost: -1,
    },
  },
  voltShadowcornLootbox: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 79,
      ethereum: -1,
      localhost: -1,
    },
  },
  nebulaShadowcornLootbox: {
    poolIdByChain: {
      mumbai: -1,
      polygon: 76,
      ethereum: -1,
      localhost: -1,
    },
  },
};

const defaultLootboxBalances: { [key in terminusType]: number } = {
  commonLootbox: 0,
  rareLootbox: 0,
  mythicLootbox: 0,
  landLootbox: 0,
  mysteryLootbox: 0,
  RMPLootbox: 0,
  goldenTicket: 0,
  mythicKeystone: 0,
  lightKeystone: 0,
  wonderKeystone: 0,
  mysteryKeystone: 0,
  heartKeystone: 0,
  cloudKeystone: 0,
  flowerKeystone: 0,
  candyKeystone: 0,
  crystalKeystone: 0,
  moonKeystone: 0,
  rainbowKeystone: 0,
  omnomKeystone: 0,
  starKeystone: 0,
  commonShadowcornEgg: 0,
  rareShadowcornEgg: 0,
  mythicShadowcornEgg: 0,
  shadowcornTierOne: 0,
  shadowcornTierTwo: 0,
  shadowcornTierThree: 0,
  nurseryTierOne: 0,
  nurseryTierTwo: 0,
  nurseryTierThree: 0,
  iSurvivedLaunch: 0,
  founders: 0,
  communityCouncil: 0,
  summerOfLoveTier1: 0,
  summerOfLoveTier2: 0,
  summerOfLoveTier3: 0,
  fireShadowcornLootbox: 0,
  slimeShadowcornLootbox: 0,
  soulShadowcornLootbox: 0,
  voltShadowcornLootbox: 0,
  nebulaShadowcornLootbox: 0,
};

interface NFTMetadata {
  image: string;
}

// TODO(kellan): Add "locked" key. Reading this data will require us to extend the ERC721Metadata ABI to include:
// 1. getUnicornMetadata for the Unicorns contract
// 2. getLandMetadata for the Lands contract
// 3. We need to check if Shadowcorns support game lock in their metadata
interface NFTInfo {
  tokenID: string;
  tokenURI: string;
  imageURI: string;
  metadata: NFTMetadata;
}

const CryptoUnicorns = () => {
  const router = useRouter();

  const [currentAccount, setCurrentAccount] = React.useState(
    "0x0000000000000000000000000000000000000000"
  );
  const [notEnoughRBW, setNotEnoughRBW] = React.useState(false);
  const [notEnoughUNIM, setNotEnoughUNIM] = React.useState(false);
  const [needAllowanceRBW, setNeedAllowanceRBW] = React.useState(false);
  const [needAllowanceUNIM, setNeedAllowanceUNIM] = React.useState(false);
  const [rbwToStash, setRBWToStash] = React.useState("");
  const [unimToStash, setUNIMToStash] = React.useState("");
  const [terminusAddress, setTerminusAddress] = React.useState("");
  const [UNIMAddress, setUNIMAddress] = React.useState("");
  const [RBWAddress, setRBWAddress] = React.useState("");
  const [unicornsAddress, setUnicornsAddress] = React.useState("");
  const [landsAddress, setLandsAddress] = React.useState("");
  const [shadowcornsAddress, setShadowcornsAddress] = React.useState("");

  // const [lootboxBalances, setLootboxBalances] = React.useState({
  //   ...defaultLootboxBalances,
  // });

  // const [unicorns, setUnicorns] = React.useState<NFTInfo[]>([]);
  // const [lands, setLands] = React.useState<NFTInfo[]>([]);
  // const [shadowcorns, setShadowcorns] = React.useState<NFTInfo[]>([]);

  const spyAddressInput = React.useRef<HTMLInputElement | null>(null);

  const [spyMode, setSpyMode] = React.useState(false);
  const [displayType, setDisplayType] = React.useState(0);

  // const router = useRouter();
  const web3ctx = useContext(Web3Context);

  useEffect(() => {
    if (!spyMode) {
      setCurrentAccount(web3ctx.account);
    }
  }, [web3ctx.account, spyMode]);

  // Set contract addresses
  useEffect(() => {
    const chain: string | undefined = chainByChainId[web3ctx.chainId];
    if (!chain) {
      setTerminusAddress("");
      setUNIMAddress("");
      setRBWAddress("");
      setUnicornsAddress("");
      setLandsAddress("");
      setShadowcornsAddress("");
    } else {
      setTerminusAddress(TerminusAddresses[chain as supportedChains]);
      setUNIMAddress(UNIMAddresses[chain as supportedChains]);
      setRBWAddress(RBWAddresses[chain as supportedChains]);
      setUnicornsAddress(UnicornsAddresses[chain as supportedChains]);
      setLandsAddress(LandsAddresses[chain as supportedChains]);
      setShadowcornsAddress(ShadowcornsAddresses[chain as supportedChains]);
    }
  }, [web3ctx.chainId]);

  useQuery(
    [],
    async () => {
      if (!web3ctx.web3.currentProvider) {
        return {
          rbwAddress: "0x0000000000000000000000000000000000000000",
          unimAddress: "0x0000000000000000000000000000000000000000",
          gameServer: "0x0000000000000000000000000000000000000000",
          terminusAddress: "0x0000000000000000000000000000000000000000",
        };
      }
      const contract = new web3ctx.web3.eth.Contract(
        StashABI
      ) as any as StashABIType;

      const gameBankContract = new web3ctx.web3.eth.Contract(
        GameBankABI
      ) as unknown as GameBankABIType;

      contract.options.address =
        GameBankAddresses[
          web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
        ];
      const rbwAddress = await contract.methods.getRBWAddress().call();
      const unimAddress = await contract.methods.getUNIMAddress().call();
      const gameServer = await contract.methods.getGameServer().call();
      const terminusAddress = await gameBankContract.methods
        .getTerminusTokenAddress()
        .call();
      setRBWAddress(rbwAddress);
      setUNIMAddress(unimAddress);
      return { rbwAddress, unimAddress, gameServer, terminusAddress };
    },
    {
      ...hookCommon,
    }
  );

  // Fetch terminus balances.
  const lootboxBalances = useQuery(
    ["cuTerminus", terminusAddress, currentAccount],
    async ({ queryKey }) => {
      const currentChain = chainByChainId[web3ctx.chainId as number];
      const currentUserAddress = queryKey[2];

      if (!currentChain) {
        return;
      }
      if (currentUserAddress == "0x0000000000000000000000000000000000000000") {
        return;
      }

      const terminusFacet = new web3ctx.web3.eth.Contract(
        terminusAbi
      ) as any as TerminusFacet;
      terminusFacet.options.address = terminusAddress;

      let accounts: string[] = [];
      let poolIds: number[] = [];

      terminusTypes.forEach((lootboxType) => {
        const pool =
          terminusInfo[lootboxType].poolIdByChain[
            currentChain as supportedChains
          ];
        if (pool > 0) {
          accounts.push(`${currentUserAddress}`);
          poolIds.push(pool);
        }
      });

      let currentBalances = { ...defaultLootboxBalances };

      try {
        const balances = await terminusFacet.methods
          .balanceOfBatch(accounts, poolIds)
          .call();
        balances.forEach((balance, lootboxIndex) => {
          currentBalances[terminusTypes[lootboxIndex]] = parseInt(balance, 10);
        });
      } catch (e) {
        console.error(
          `Crypto Unicorns player portal: Could not retrieve lootbox balances for the given user: ${currentUserAddress}. Lootbox pool IDs: ${poolIds}. Terminus contract address: ${terminusAddress}.`
        );
      }
      return currentBalances;
    },
    {
      ...hookCommon,
    }
  );

  // Fetch unicorns.
  const unicorns = useQuery(
    ["cuUnicorns", unicornsAddress, currentAccount],
    async ({ queryKey }) => {
      const currentChain = chainByChainId[web3ctx.chainId as number];
      const currentUserAddress = String(queryKey[2]);

      if (!currentChain) {
        return;
      }
      if (currentUserAddress == "0x0000000000000000000000000000000000000000") {
        return;
      }

      const unicornsContract = new web3ctx.web3.eth.Contract(
        ERC721MetadataABI
      ) as unknown as MockERC721;
      unicornsContract.options.address = String(queryKey[1]);

      let unicornsInventory: NFTInfo[] = [];

      try {
        const numUnicornsRaw: string = await unicornsContract.methods
          .balanceOf(currentUserAddress)
          .call();

        let numUnicorns: number = 0;
        try {
          numUnicorns = parseInt(numUnicornsRaw, 10);
        } catch (e) {
          console.error(
            `Error: Could not parse number of owned unicorns as an integer: ${numUnicornsRaw}`
          );
        }

        let tokenIDPromises = [];
        for (let i = 0; i < numUnicorns; i++) {
          tokenIDPromises.push(
            unicornsContract.methods
              .tokenOfOwnerByIndex(currentUserAddress, i)
              .call()
          );
        }
        const tokenIDs = await Promise.all(tokenIDPromises);

        const tokenURIPromises = tokenIDs.map((tokenID) =>
          unicornsContract.methods.tokenURI(tokenID).call()
        );
        const tokenURIs = await Promise.all(tokenURIPromises);

        const tokenMetadataPromises = tokenURIs.map((tokenURI) =>
          fetch(tokenURI).then((response) => response.json())
        );
        const tokenMetadata = await Promise.all(tokenMetadataPromises);

        const imageURIs = tokenMetadata.map((metadata) => metadata.image);

        tokenIDs.forEach((tokenID, index) => {
          unicornsInventory.push({
            tokenID,
            tokenURI: tokenURIs[index],
            imageURI: imageURIs[index],
            metadata: tokenMetadata[index],
          });
        });
      } catch (e) {
        console.error(
          "Error: There was an issue retrieving information about user's unicorns:"
        );
        console.error(e);
      }

      return unicornsInventory;
    },
    {
      ...hookCommon,
    }
  );

  // Fetch lands.
  const lands = useQuery(
    ["cuLands", landsAddress, currentAccount],
    async ({ queryKey }) => {
      const currentChain = chainByChainId[web3ctx.chainId as number];
      const currentUserAddress = String(queryKey[2]);

      if (!currentChain) {
        return;
      }
      if (currentUserAddress == "0x0000000000000000000000000000000000000000") {
        return;
      }

      const landsContract = new web3ctx.web3.eth.Contract(
        ERC721MetadataABI
      ) as unknown as MockERC721;
      landsContract.options.address = String(queryKey[1]);

      let landsInventory: NFTInfo[] = [];

      try {
        const numLandsRaw: string = await landsContract.methods
          .balanceOf(currentUserAddress)
          .call();

        let numLands: number = 0;
        try {
          numLands = parseInt(numLandsRaw, 10);
        } catch (e) {
          console.error(
            `Error: Could not parse number of owned lands as an integer: ${numLandsRaw}`
          );
        }

        let tokenIDPromises = [];
        for (let i = 0; i < numLands; i++) {
          tokenIDPromises.push(
            landsContract.methods
              .tokenOfOwnerByIndex(currentUserAddress, i)
              .call()
          );
        }
        const tokenIDs = await Promise.all(tokenIDPromises);

        const tokenURIPromises = tokenIDs.map((tokenID) =>
          landsContract.methods.tokenURI(tokenID).call()
        );
        const tokenURIs = await Promise.all(tokenURIPromises);

        const tokenMetadataPromises = tokenURIs.map((tokenURI) =>
          fetch(tokenURI).then((response) => response.json())
        );
        const tokenMetadata = await Promise.all(tokenMetadataPromises);

        const imageURIs = tokenMetadata.map((metadata) => metadata.image);

        tokenIDs.forEach((tokenID, index) => {
          landsInventory.push({
            tokenID,
            tokenURI: tokenURIs[index],
            imageURI: imageURIs[index],
            metadata: tokenMetadata[index],
          });
        });
      } catch (e) {
        console.error(
          "Error: There was an issue retrieving information about user's lands:"
        );
        console.error(e);
      }

      return landsInventory;
    },
    {
      ...hookCommon,
    }
  );

  // Fetch shadowcorns.
  const shadowcorns = useQuery(
    ["cuShadowcorns", shadowcornsAddress, currentAccount],
    async ({ queryKey }) => {
      const currentChain = chainByChainId[web3ctx.chainId as number];
      const currentUserAddress = String(queryKey[2]);

      if (!currentChain) {
        return;
      }
      if (currentUserAddress == "0x0000000000000000000000000000000000000000") {
        return;
      }

      const shadowcornsContract = new web3ctx.web3.eth.Contract(
        ERC721MetadataABI
      ) as unknown as MockERC721;
      shadowcornsContract.options.address = String(queryKey[1]);

      let shadowcornsInventory: NFTInfo[] = [];

      try {
        const numShadowcornsRaw: string = await shadowcornsContract.methods
          .balanceOf(currentUserAddress)
          .call();

        let numShadowcorns: number = 0;
        try {
          numShadowcorns = parseInt(numShadowcornsRaw, 10);
        } catch (e) {
          console.error(
            `Error: Could not parse number of owned shadowcorns as an integer: ${numShadowcornsRaw}`
          );
        }

        let tokenIDPromises = [];
        for (let i = 0; i < numShadowcorns; i++) {
          tokenIDPromises.push(
            shadowcornsContract.methods
              .tokenOfOwnerByIndex(currentUserAddress, i)
              .call()
          );
        }
        const tokenIDs = await Promise.all(tokenIDPromises);

        const tokenURIPromises = tokenIDs.map((tokenID) =>
          shadowcornsContract.methods.tokenURI(tokenID).call()
        );
        const tokenURIs = await Promise.all(tokenURIPromises);

        const tokenMetadataPromises = tokenURIs.map((tokenURI) =>
          fetch(tokenURI).then((response) => response.json())
        );
        const tokenMetadata = await Promise.all(tokenMetadataPromises);

        const imageURIs = tokenMetadata.map((metadata) => metadata.image);

        tokenIDs.forEach((tokenID, index) => {
          shadowcornsInventory.push({
            tokenID,
            tokenURI: tokenURIs[index],
            imageURI: imageURIs[index],
            metadata: tokenMetadata[index],
          });
        });
      } catch (e) {
        console.error(
          "Error: There was an issue retrieving information about user's lands:"
        );
        console.error(e);
      }

      return shadowcornsInventory;
    },
    {
      ...hookCommon,
    }
  );

  const rbw = useERC20({
    contractAddress: RBWAddress,
    ctx: web3ctx,
    spender:
      GameBankAddresses[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    account: currentAccount,
  });
  const unim = useERC20({
    contractAddress: UNIMAddress,
    spender:
      GameBankAddresses[
        web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
      ],
    ctx: web3ctx,
    account: currentAccount,
  });
  const contract = new web3ctx.web3.eth.Contract(
    StashABI
  ) as any as StashABIType;

  contract.options.address =
    GameBankAddresses[
      web3ctx.targetChain?.name ? web3ctx.targetChain.name : "localhost"
    ];

  const playAssetPath = "https://s3.amazonaws.com/static.simiotics.com/play";
  const assets = {
    unimLogo: `${playAssetPath}/cu/unim-logo.png`,
    rbwLogo: `${playAssetPath}/cu/rbw-logo.png`,
  };

  const toast = useToast();
  const stashUnim = useMutation(
    (amount: string) =>
      contract.methods.stashUNIM(web3ctx.web3.utils.toWei(amount)).send({
        from: web3ctx.account,
        gasPrice:
          process.env.NODE_ENV !== "production" ? "100000000000" : undefined,
      }),
    {
      onSuccess: () => {
        toast("Transaction went to the moon!", "success");
      },
      onError: () => {
        toast("Transaction failed >.<", "error");
      },
    }
  );

  const stashRBW = useMutation(
    (amount: string) =>
      contract.methods.stashRBW(web3ctx.web3.utils.toWei(amount)).send({
        from: web3ctx.account,
        gasPrice:
          process.env.NODE_ENV !== "production" ? "100000000000" : undefined,
      }),
    {
      onSuccess: () => {
        toast("Transaction went to the moon!", "success");
      },
      onError: () => {
        toast("Transaction failed >.<", "error");
      },
    }
  );

  React.useLayoutEffect(() => {
    if (unim.spenderState.data?.allowance && unimToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(unim.spenderState.data.allowance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(unimToStash, "ether")
            )
          ) == -1
      ) {
        setNeedAllowanceUNIM(true);
      } else {
        setNeedAllowanceUNIM(false);
      }
    } else {
      setNeedAllowanceUNIM(false);
    }
    if (unim.spenderState.data?.balance && unimToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(unim.spenderState.data.balance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(unimToStash, "ether")
            )
          ) == -1
      ) {
        setNotEnoughUNIM(true);
      } else {
        setNotEnoughUNIM(false);
      }
    } else {
      setNotEnoughUNIM(false);
    }
  }, [unimToStash, unim.spenderState.data, web3ctx.web3.utils, currentAccount]);

  React.useLayoutEffect(() => {
    if (rbw.spenderState.data?.allowance && rbwToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(rbw.spenderState.data.allowance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(rbwToStash, "ether")
            )
          ) == -1
      ) {
        setNeedAllowanceRBW(true);
      } else {
        setNeedAllowanceRBW(false);
      }
    } else {
      setNeedAllowanceRBW(false);
    }
    if (rbw.spenderState.data?.balance && rbwToStash.length !== 0) {
      if (
        web3ctx.web3.utils
          .toBN(rbw.spenderState.data.balance)
          .cmp(
            web3ctx.web3.utils.toBN(
              web3ctx.web3.utils.toWei(rbwToStash, "ether")
            )
          ) == -1
      ) {
        setNotEnoughRBW(true);
      } else {
        setNotEnoughRBW(false);
      }
    } else {
      setNotEnoughRBW(false);
    }
  }, [rbwToStash, rbw.spenderState.data, web3ctx.web3.utils, currentAccount]);

  const lootboxes = [
    {
      imageUrl:
        "https://lh3.googleusercontent.com/0H9500IgQKZqKstSo-nruV9RMV9aw7oPtgLARWtbIBU6brTaaK2F0Lk3t7xLygvk80r6OlsBOjnqIhr3EFzEMdwUZlIXTuuEa-O3uQ=w600",
      displayName: "Common Lootbox",
      balanceKey: "commonLootbox",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/1RFVPV0nYzXG0FYea6BQacjsJlbutQSib258tWnovbsIiNhUyOo_BO_AfANN6aSppzvS7ZLpgNcppXuhLOHT2wQAxqAx-Da5bVLnsw=w600",
      displayName: "Rare Lootbox",
      balanceKey: "rareLootbox",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/2bv26HfU7CgDJhVocABtxbdMLQ8qH2kuU5mQJWVehuNzX-4GiOBm2iIxsTtdriHYpsmr94R7xfRhgELCmnJKQpcMA4wMoPlM_V4zaQ=w600",
      displayName: "Mythic Lootbox",
      balanceKey: "mythicLootbox",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/2AVqj_GOKf358s0Fkw66MHxEcivOWfvRjAMdmqhHgh3RwyWyJNbnn_amPUJt4KDeO6H7IdWKSV1tli5ijkgHHAemxYGuTof5WZo3wA=w600",
      displayName: "Land Lootbox",
      balanceKey: "landLootbox",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/30YXRt8oPvD0J9KuRiUTLrRxrigwvbs8P5uFIkJt65hmlVAerYAsxZgPHjvA-byTXseTKJQsnpbuD7giChaO4TyoFm7pcqza8NrZ=w600",
      displayName: "Mystery Lootbox",
      balanceKey: "mysteryLootbox",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/u_BYIeFDCF4dC4n_Col8e1W_dNTK84uMfR6mhjLhQj7GuObvBeENqSu7L8nzDFJ9JDdpiezHpRP0PJ8ioPxOakvU3iz5lbhJy1abRWM=w600",
      displayName: "RMP Lootbox",
      balanceKey: "RMPLootbox",
    },
    {
      imageUrl:
        "https://i.seadn.io/gae/NY1AJidjM4HnDbOrBw_474MUhbp4tL8EZBRmCXFtPDcEYO_B_pF2D1fua6ggpajhJm5_4xstKg94SySs2QY4mit_XNNd4Rm8LS06?auto=format&w=1000",
      displayName: "Fire Shadowcorn Lootbox",
      balanceKey: "fireShadowcornLootbox",
    },
    {
      imageUrl:
        "https://i.seadn.io/gae/0RBQ7zZ0YJsoh4Ffd38olTDRZKCqlK_3FNpqYF30baO77djp_gedIiD5IRJrUArfmGmQs0VBupzaJyzKaiAHRHolWxrCDm_JvQ_4rQ?auto=format&w=1000",
      displayName: "Slime Shadowcorn Lootbox",
      balanceKey: "slimeShadowcornLootbox",
    },
    {
      imageUrl:
        "https://i.seadn.io/gae/J9KyCj2jbkZ93hB_ilcXBBkyhfTgObG8CjFFmFIT8_d2b6nnmpyikbGGO7_7MH45KcH1VSaqFXFeLjbWsLLj0yJxvULxbzB-1PGTETw?auto=format&w=1000",
      displayName: "Soul Shadowcorn Lootbox",
      balanceKey: "soulShadowcornLootbox",
    },
    {
      imageUrl:
        "https://i.seadn.io/gae/XroR84IEp89RHeEkI2ozw6h9t-hMXY8HDi1uB2nsmjpv_5-fKZrmyX8T2kF7yFRl8SArBhZOCCf6GmOBTDRLngmkdoj0moBQYt5L6sU?auto=format&w=1000",
      displayName: "Volt Shadowcorn Lootbox",
      balanceKey: "voltShadowcornLootbox",
    },
    {
      imageUrl:
        "https://i.seadn.io/gae/U3EE-yhtgc44g3bxUX7FWLiTmNA_q_qdCch-4jxbcd7va_LzDmMm_Mm-RL3RYszPOOu0e8DukUdyBaYo_cSyGM8Dq0l6PYbpreuwrZY?auto=format&w=1000",
      displayName: "Nebula Shadowcorn Lootbox",
      balanceKey: "nebulaShadowcornLootbox",
    },
  ];

  const keystones = [
    {
      imageUrl:
        "https://lh3.googleusercontent.com/cMpMnm8YhUGyOuB-CoBaUV3zwk7d0lXzqjNyNM-Z0z8tmWo1sl_3tUm5LP4sSfgiJ6zF78mLOWthkt17aoXEA9WNe-Mtp_vwQ_w8Gg=w375",
      displayName: "Mythic Keystone",
      balanceKey: "mythicKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/HZOYH5v__1eq3Nb8kRXGkGSPKtefHkjL5cknEdM7UJU7ArAYMboBmVgLNNuAxu3U_IhWulnSP1zmNvqkSQ4Om3mGLhGr_JWY2OvJ9Q=w375",
      displayName: "Light Keystone",
      balanceKey: "lightKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/lzbxrtoYIxAMt61f-uZC0gGu7Vzrq0M0M4YUWUeBYVoD6C2A6YJ5Ecu-9dMPasRiMn65Ol7pHUH83tdFwU3hF61NHyBZryBbRBpp9Lc=w375",
      displayName: "Wonder Keystone",
      balanceKey: "wonderKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/oHKgbOZxlu0DV8wGleezJQbls2sa1UJndTpTf4MQofyWL04Z-GP_KCnai9uXH_kXwWYNkkw0bqw_YsJZgfJ0tqk4b63rHnXaHLCbtg=w375",
      displayName: "Mystery Keystone",
      balanceKey: "mysteryKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/iIoGLFIbt7UOS5Nyzd0eBN2JzhAhUBH706HL7DGlRHlkTqQ-jpH40OTSZQVuQuPplz7yU3iRLXzOXHZ9nvYQ7ePCW5hpoyWcq9uUZ5g=w375",
      displayName: "Heart Keystone",
      balanceKey: "heartKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/GEIIy7aZsqJJq1dXOmbsZ7Q9Xvn0VmoYsSPiHhD6DNwcgbt-3zgdM3p6-0c2VsSxBRT0BsjpWRn4MgIruTP9GG8JC-8NYs9sJ0G58g=w600",
      displayName: "Cloud Keystone",
      balanceKey: "cloudKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/RvTiHpdv_vdyoXEF2rqoAuvA0sGLtfPWd2H9P86bFQ_rC6JkX3iV6MGUfwSRwyVSITyBjgljexUIymGD6fPe2K3clYQu2P70DfqB=w375",
      displayName: "Flower Keystone",
      balanceKey: "flowerKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/UhObo6BU2ytFvmJXex2oxsVyHkpQ1UaV4Us9VGnj3sbZ5rAnjO2e6n_QhYe5kHcDnFVAuj18LNFsavIqJTcEdvDqOXL-rJB2Mj-TCwc=w375",
      displayName: "Candy Keystone",
      balanceKey: "candyKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/Q44aOBZzBUqrcTa6M1Raa9LeuJXOGIKWbgB9MF-6rxSkjOWqqlZSKzwfg8htmpoxs_no_lzYhmGyzvErRKwjq-es3THEh3Gc1Creky4=w375",
      displayName: "Crystal Keystone",
      balanceKey: "crystalKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/9jtNiahHNKloIcn5aRBFv4Q1qPtHauUkKwkMsVvFMq0XIEru1C8xbwdRPbuxSNTmtKcMi0fSLYEacxAqW53p6gq-VCGJPjwYz_6v=w375",
      displayName: "Moon Keystone",
      balanceKey: "moonKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/17Eb4guXQa2i0EmAT16GveeVOGTL2LkG_13-ijW2_6BQFDUx831JCbhhOvG4qqLNQ4r45V9oQvh0hCZb5lAeh1V6f8XD3K-5z1HpzA=w600",
      displayName: "Rainbow Keystone",
      balanceKey: "rainbowKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/uHpjLswSIBh9XjD9hCv0Q3awIj1UeBgkxUk9qrsbXgYI8Etqtyb1R64vERF1Z72PdexC_3wcYcdZkwIldOY-Blp-DhJw7CQn5kkBRg=w375",
      displayName: "Omnom Keystone",
      balanceKey: "omnomKeystone",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/yk3SiRkQVWUH9qYH_opVbgyHJMYcyCYAkEk6ua4VUWIIJqsjp3_hlDVGJdE4W4yUFkOMtfQPAnAzO2bbX1--v0H-d6qSA--USWivDw=w600",
      displayName: "Star Keystone",
      balanceKey: "starKeystone",
    },
  ];

  const badges = [
    {
      imageUrl:
        "https://lh3.googleusercontent.com/pfMV2nrG3KedIn6r5YP1ftLSLGYUP8ErlqX02Xgk3ixT6Ulz9Z6H2iDW2Yv3LK5N2d9IgXryYIlFboGx-ZhiahFivLPg4WrbBMa--So=w600",
      displayName: "Shadowcorn Act 1 - Tier 1",
      balanceKey: "shadowcornTierOne",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/GvSQBvbOHd5lQsTTujmTCdyxOQLCGpVPrJDehIn4HeedDEGdlH6LUZFSKd3qdIwMP1vOXizG7nsPp9yn_FZWHCCzor2o-6j-5OkiuQ=w375",
      displayName: "Shadowcorn Act 1 - Tier 2",
      balanceKey: "shadowcornTierTwo",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/Pch-UckkLH_E-VaU09FnLfRUuZW_c-16UJSCHM3p2NolvUAluXOgNjBV6PUSsIwFah92DFdxeeJr3gsRuzBlVCqoQ3ujwelG8bIGLyM=w600",
      displayName: "Shadowcorn Act 1 - Tier 3",
      balanceKey: "shadowcornTierThree",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/Xm2M-ZtW7Jp9C9kt07s3C-a6mORmKCMgnIAoz7t1Xtw2uFZ6H26wWFKd6tPR0Y_DZmoOYxTcsukXcjA3YBQiulVZBFPRM0IijDc7=w375",
      displayName: "Nursery Under Construction - Tier 1",
      balanceKey: "nurseryTierOne",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/nk1mbOkCnZVY42cSd6hAJWJYiW5yVEkMbIw0ByWe6XBnblzXbkWHDKg0U13RRgInxoykN0ix4T6BEc2WrPdtB2E2l0gsXzwFJuNcRR0=w375",
      displayName: "Nursery Under Construction - Tier 2",
      balanceKey: "nurseryTierTwo",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/KWxFz8b_RlbVtaev3n6sipKulDuJYbfLWNOw8wV5X_Y3I5zZNmBlRoLsF9dl-ccIWwU2r74b_qZ23mNlxN6B_43uPApYwhaSKmTb=w375",
      displayName: "Nursery Under Construction - Tier 3",
      balanceKey: "nurseryTierThree",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/-Cjwhfs4-vE9jHIrv5AVgG0SMorO9MIc6Z5fx-tKQyqRVv8QwK77C-el1KWYh3kQj99QtUjKskpR8Jhot7WVTqWEkBYplQF9u0iqxg=w600",
      displayName: "'I Survived Launch!' Badge",
      balanceKey: "iSurvivedLaunch",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/WrcfIghbGrProNTcyDWVxWR5zxsll4RkKC59L92oDQbCCQAFI53p3FAv8mIWfeI_EfysP3AbH5AfpsC8cVwraKgGTZpFjO71Ixua=w600",
      displayName: "Founders Badge",
      balanceKey: "founders",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/quOMOAl721b5HX22B9pKedNlHDEOnLSt1NxmRu_Ci1rP11o2HV4pfV8d5CjgWmuxpnoMsA4uSrJDJu3Ou84kEniGWtpII37MLoyE=w600",
      displayName: "Community Council",
      balanceKey: "communityCouncil",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/0fOpwZbJiOxwvnUOrNS6ciJMyFntzKQEO1kkIP4dffRCfeK5YL43lhkVsWw0oWuqHmj5sIEh7G1gasr1mqojKHXk7nBiyy5Xkoc2cw=w375",
      displayName: "Summer of Love - Tier 1",
      balanceKey: "summerOfLoveTier1",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/PLpBtNs66mUiOwJZ4KApyVEEGl_Txjy5Ouh4tCo9oqOi_1lq9UOfIkgqO2cRl6uSmaYEtMNee_tP8Ul4PXl_lIKEIlobZmPcXkKG=w600",
      displayName: "Summer of Love - Tier 2",
      balanceKey: "summerOfLoveTier2",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/2rTZEJzrLDY38MVgmSShmYeia1I4EqD2-EyHcyzHwkkT-EwMntAjxA44w93N3CL4lzXlckWLM4m6TfpwlIISsPdBWyJRuJSrT5Pwgg=w600",
      displayName: "Summer of Love - Tier 3",
      balanceKey: "summerOfLoveTier3",
    },
  ];

  const miscItems = [
    {
      imageUrl:
        "https://lh3.googleusercontent.com/39jijzFGBIgkcJU4R6VQGR9b4dC4kQ0keiiBDzgqc10EVg7ajJvXdui0CN4BRHKG33r9NxB_yw9G2VWCg61OS7ESjtKQviY7qT-1Cg=w375",
      displayName: "Golden Ticket",
      balanceKey: "goldenTicket",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/nbELHPCpbpdYS1SfcACqWXnr6_7xaRrdvkYfOeDyzECfW9tBHSUCgR-BC1bYbBj7SsL8AQHhb0QUWl99lXAhco9pj12w_rGKDRZJHA=w375",
      displayName: "Common Shadowcorn Egg",
      balanceKey: "commonShadowcornEgg",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/qjThimKLJZy6cpRa4gZ61jDK06L7G25Ln-BYDYoucz7QZ9xXNjNtjVxAolnD8p878RLcsHrUPwMHoCLAsNr8kq4grAiecw3lr9Il=w600",
      displayName: "Rare Shadowcorn Egg",
      balanceKey: "rareShadowcornEgg",
    },
    {
      imageUrl:
        "https://lh3.googleusercontent.com/GRPpWNUybBn_7CiE2knI2OdBwQUvwQe_jq-MUE-KFBksglI01MqbOpwKoj2m_rS7gD3ywEN3yE21H8e5-av-jX-5gXtzxSufWIdSMw=w375",
      displayName: "Mythic Shadowcorn Egg",
      balanceKey: "mythicShadowcornEgg",
    },
  ];

  const handleSubmit = () => {};

  const handleKeypress = (e: any) => {
    //it triggers by pressing the enter key
    if (e.charCode === 13) {
      handleSubmit();
    }
  };

  const displayCardList = (
    list: any,
    displayId: number,
    showQuantity: boolean = true
  ) => {
    const html = (
      <Box display={displayType == displayId ? undefined : "none"}>
        {spyMode && (
          <HStack alignSelf="start" pb={4}>
            <Image ml={2} alt={"bottle"} h="24px" src={assets["unimLogo"]} />
            <Text pr={4}>UNIM: {getUnimBalance()}</Text>
            <Image ml={2} alt={"bottle"} h="24px" src={assets["rbwLogo"]} />
            <Text>RBW: {getRBWBalance()}</Text>
          </HStack>
        )}
        <Flex wrap="wrap" justifyContent="center" gap="20px" mt="20px">
          {list.map((item: any, idx: any) => {
            if (!lootboxBalances?.data) {
              return;
            }
            const quantity =
              lootboxBalances.data[item["balanceKey"] as terminusType];
            if (quantity == 0 && !showQuantity) {
              return;
            } else {
              return (
                <LootboxCard
                  maxW={["140px", "170px", "220px"]}
                  key={idx}
                  imageUrl={item["imageUrl"]}
                  displayName={item["displayName"]}
                  lootboxBalance={quantity}
                  showQuantity={showQuantity}
                />
              );
            }
          })}
        </Flex>
      </Box>
    );
    return html;
  };

  const displayERC721List = (
    list: any,
    displayId: number,
    showQuantity: boolean = true,
    isVideo = false
  ) => {
    return (
      <Box display={displayType == displayId ? undefined : "none"}>
        {spyMode && (
          <HStack alignSelf="start" pb={4}>
            <Image ml={2} alt={"bottle"} h="24px" src={assets["unimLogo"]} />
            <Text pr={4}>UNIM: {getUnimBalance()}</Text>
            <Image ml={2} alt={"bottle"} h="24px" src={assets["rbwLogo"]} />
            <Text>RBW: {getRBWBalance()}</Text>
            <Spacer />
            <Text>{`${list.length} Item${list.length === 1 ? "" : "s"}`}</Text>
          </HStack>
        )}
        {!spyMode && (
          <HStack alignSelf="start" pb={4}>
            <Text>{`${list.length} Item${list.length === 1 ? "" : "s"}`}</Text>
          </HStack>
        )}

        <Flex wrap="wrap" justifyContent="center" gap="20px" mt="20px">
          {list.map((item: any, idx: any) => {
            return (
              <LootboxCard
                maxW={["140px", "170px", "220px"]}
                key={idx}
                imageUrl={item["metadata"]["image"]}
                displayName={item["metadata"]["name"]}
                lootboxBalance={1}
                showQuantity={showQuantity}
                isVideo={isVideo}
              />
            );
          })}
        </Flex>
      </Box>
    );
  };

  const getUnimBalance = () => {
    return unim.spenderState.data?.balance
      ? Math.floor(
          web3ctx.web3.utils.fromWei(
            unim.spenderState.data?.balance,
            "ether"
          ) as unknown as number
        )
      : "0";
  };

  const getRBWBalance = () => {
    return rbw.spenderState.data?.balance
      ? Math.floor(
          web3ctx.web3.utils.fromWei(
            rbw.spenderState.data?.balance,
            "ether"
          ) as unknown as number
        )
      : "0";
  };

  if (
    contract.options.address === "0x0000000000000000000000000000000000000000"
  ) {
    return (
      <Flex
        w="300px"
        h="220px"
        placeSelf={"center"}
        alignSelf="center"
        fontSize={"20px"}
      >
        There is contract on this chain
      </Flex>
    );
  }

  return (
    <Flex
      className="Games"
      borderRadius={"xl"}
      bgColor={spyMode ? "#1A1D22" : "#1A1D22"}
    >
      <Flex
        w="100%"
        minH="100vh"
        direction={"column"}
        px={[0, 0, "7%"]}
        my={["20px", "40px", "60px"]}
      >
        <Box display={spyMode ? "none" : ""}>
          <Flex
            w="100%"
            direction={"row"}
            flexWrap="wrap"
            mb={[3, 6, 12]}
            bgColor="pink.500"
            borderRadius={"xl"}
            boxShadow="xl"
            placeItems={"center"}
          >
            <Flex direction={"column"}>
              <Badge
                colorScheme={"pink"}
                variant={"solid"}
                borderRadius={"md"}
                mr={2}
                p={1}
              >
                <HStack>
                  <Image
                    ml={2}
                    alt={"bottle"}
                    h="48px"
                    src={assets["unimLogo"]}
                  />
                  <Flex direction={"column"} wrap="nowrap" w="100%">
                    <code>
                      <Flex mx={2} display={"inline-block"} fontSize="xl">
                        {unim.spenderState.isLoading ? (
                          <Spinner m={0} size={"lg"} />
                        ) : (
                          <Flex fontSize={["sm", "md", "lg"]}>
                            {`balance: `} <Spacer />
                            {getUnimBalance()}
                          </Flex>
                        )}
                      </Flex>
                    </code>
                  </Flex>
                </HStack>
              </Badge>
            </Flex>
            <Spacer />
            <Flex direction={"column"}>
              <Badge
                colorScheme={"pink"}
                variant={"solid"}
                fontSize={"md"}
                borderRadius={"md"}
                mr={2}
                p={1}
              >
                <HStack>
                  <Image ml={2} alt={"rbw"} h="48px" src={assets["rbwLogo"]} />
                  <Flex direction={"column"} wrap="nowrap" w="100%">
                    <code>
                      <Flex mx={2} display={"inline-block"} fontSize="xl">
                        {rbw.spenderState.isLoading ? (
                          <Spinner m={0} size={"lg"} />
                        ) : (
                          <Flex fontSize={["sm", "md", "lg"]}>
                            {`balance: `} <Spacer />
                            {getRBWBalance()}
                          </Flex>
                        )}
                      </Flex>
                    </code>
                  </Flex>
                </HStack>
              </Badge>
            </Flex>
          </Flex>
          <Text
            fontSize={["sm", "md", "lg"]}
            textColor={"gray.600"}
            maxW="1337px"
          >
            Use this form to stash any amount of UNIM and RBW into Crypto
            Unicorns.
          </Text>
          <Text mb={4} fontSize={["sm", "md", "lg"]}>
            WARNING: Only use an account with which you have already logged into
            the game. Otherwise, the game server will not respect your stash
            operation.
          </Text>
          <Center>
            <code>
              <Stack bgColor={"#1A1D22"} spacing={2} mx="10px">
                <Box w="100%">
                  <FormLabel
                    fontSize={["sm", "md", "lg"]}
                    mb={["2px", "4px", "8px"]}
                    wordBreak={"break-all"}
                    w="fit-content"
                  >
                    {"UNIM to stash"}
                  </FormLabel>

                  <InputGroup
                    textColor={"blue.900"}
                    size={"lg"}
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                  >
                    <Flex
                      direction={"row"}
                      w="100%"
                      minW={["100%", "480px", "580px"]}
                    >
                      <FormControl isInvalid={notEnoughUNIM}>
                        <Input
                          w={["100%", "200px", "300px"]}
                          mt="4px"
                          variant={"outline"}
                          type="search"
                          value={unimToStash}
                          isDisabled={
                            unim.setSpenderAllowance.isLoading ||
                            stashUnim.isLoading
                          }
                          onKeyPress={handleKeypress}
                          onChange={(event) => {
                            if (
                              event.target.value.match(/^[0-9]+$/) != null ||
                              event.target.value.length == 0
                            ) {
                              setUNIMToStash(event.target.value);
                            }
                          }}
                        />
                        <FormErrorMessage color="red.400" pl="1">
                          Not enough UNIM
                        </FormErrorMessage>
                      </FormControl>
                      <Spacer />
                      <Button
                        isDisabled={
                          (!needAllowanceUNIM || unimToStash === "") &&
                          (notEnoughUNIM || unimToStash == "")
                        }
                        size="md"
                        variant="cuButton"
                        textColor="#D43F8C"
                        borderColor="#FFFFFF"
                        bgColor="white"
                        fontSize={["sm", "md", "lg"]}
                        isLoading={
                          unim.setSpenderAllowance.isLoading ||
                          stashUnim.isLoading
                        }
                        onClick={() => {
                          if (needAllowanceUNIM) {
                            unim.setSpenderAllowance.mutate(MAX_INT, {
                              onSettled: () => {
                                unim.spenderState.refetch();
                              },
                            });
                          } else {
                            stashUnim.mutate(unimToStash, {
                              onSettled: () => {
                                unim.spenderState.refetch();
                                setUNIMToStash("");
                              },
                            });
                          }
                        }}
                      >
                        {needAllowanceUNIM ? "Set allowance" : "Stash!"}
                      </Button>
                    </Flex>
                  </InputGroup>
                </Box>
                <Box w="100%">
                  <FormLabel
                    mb={["2px", "4px", "8px"]}
                    fontSize={["sm", "md", "lg"]}
                    wordBreak={"break-all"}
                    w="fit-content"
                  >
                    {"RBW to stash"}
                  </FormLabel>

                  <InputGroup
                    textColor={"blue.900"}
                    size={"lg"}
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                  >
                    <Flex
                      direction={"row"}
                      w="100%"
                      minW={["95%", "480px", "580px"]}
                    >
                      <FormControl isInvalid={notEnoughRBW}>
                        <Input
                          w={["100%", "200px", "300px"]}
                          mt="4px"
                          variant={"outline"}
                          isDisabled={
                            rbw.setSpenderAllowance.isLoading ||
                            stashRBW.isLoading
                          }
                          type="search"
                          value={rbwToStash}
                          onKeyPress={handleKeypress}
                          onChange={(event) => {
                            if (
                              event.target.value.match(/^[0-9]+$/) != null ||
                              event.target.value.length == 0
                            ) {
                              setRBWToStash(event.target.value);
                            }
                          }}
                        />
                        <FormErrorMessage color="red.400" pl="1">
                          Not enough RBW
                        </FormErrorMessage>
                      </FormControl>
                      <Spacer />
                      <Button
                        variant="cuButton"
                        textColor="#D43F8C"
                        borderColor="#FFFFFF"
                        bgColor="white"
                        fontSize={["sm", "md", "lg"]}
                        isDisabled={
                          (!needAllowanceRBW || rbwToStash === "") &&
                          (notEnoughRBW || rbwToStash == "")
                        }
                        size="md"
                        isLoading={
                          rbw.setSpenderAllowance.isLoading ||
                          stashRBW.isLoading
                        }
                        onClick={() => {
                          if (needAllowanceRBW) {
                            rbw.setSpenderAllowance.mutate(MAX_INT, {
                              onSettled: () => {
                                rbw.spenderState.refetch();
                              },
                            });
                          } else {
                            stashRBW.mutate(rbwToStash, {
                              onSettled: () => {
                                rbw.spenderState.refetch();
                                setRBWToStash("");
                              },
                            });
                          }
                        }}
                      >
                        {needAllowanceRBW ? "Set allowance" : "Stash!"}
                      </Button>
                    </Flex>
                  </InputGroup>
                </Box>
              </Stack>
            </code>
          </Center>
        </Box>
        <Flex
          w="100%"
          direction={"row"}
          h="55px"
          mt={10}
          mb={12}
          pl={6}
          bgColor={spyMode ? "#4A4A4A" : "pink.500"}
          borderRadius={"xl"}
          boxShadow="xl"
          placeItems={"center"}
          fontSize={["md", "md", "lg"]}
          fontWeight="700"
        >
          {spyMode && (
            <Image
              src="https://s3.amazonaws.com/static.simiotics.com/play/cu/spy-icon.png"
              alt="Spy Mode"
              h="24px"
              pr="2"
              filter="invert(100%)"
            ></Image>
          )}
          {spyMode ? "Spy Mode" : "Inventory"}
          <Spacer />
          {spyMode && (
            <Center
              display="inline-flex"
              pr={6}
              onClick={() => {
                setSpyMode(false);
                setDisplayType(0);
                if (spyAddressInput?.current != null) {
                  spyAddressInput.current.value = "";
                }
              }}
            >
              <Text pr={2} cursor="pointer">
                exit
              </Text>
              {/* <CloseIcon h="10px" /> */}
            </Center>
          )}
        </Flex>
        {spyMode && (
          <Flex w="100%" pb={4}>
            <InputGroup size="md" textColor={"white"}>
              <Input
                ref={spyAddressInput}
                colorScheme="transparent"
                bgColor="transparent"
                variant="outline"
                onChange={(e) => {
                  const nextValue = e.target.value;
                  if (web3ctx.web3.utils.isAddress(nextValue)) {
                    setCurrentAccount(nextValue);
                  }
                }}
                placeholder="Type an address"
                _placeholder={{ color: "white" }}
              />
              <InputRightElement width="3rem">
                <Button
                  h="2rem"
                  size="md"
                  bg="transparent"
                  _hover={{
                    backgroundColor: "transparent",
                  }}
                  _focus={{
                    textDecoration: "none",
                  }}
                  onClick={() => {
                    if (spyAddressInput?.current != null) {
                      spyAddressInput.current.value = "";
                    }
                  }}
                >
                  X
                </Button>
              </InputRightElement>
            </InputGroup>
          </Flex>
        )}
        <Flex pb={4} flexDirection="row" wrap="wrap">
          <Button
            variant="whiteOutline"
            data-selected={displayType == 0 ? true : false}
            onClick={() => {
              setDisplayType(0);
            }}
          >
            <Text px={3}>Unicorns</Text>
          </Button>
          <Button
            variant="whiteOutline"
            data-selected={displayType == 6 ? true : false}
            onClick={() => {
              setDisplayType(6);
            }}
          >
            <Text px={3}>Shadowcorns</Text>
          </Button>
          <Button
            variant="whiteOutline"
            data-selected={displayType == 1 ? true : false}
            onClick={() => {
              setDisplayType(1);
            }}
          >
            <Text px={3}>Lands</Text>
          </Button>
          <Button
            variant="whiteOutline"
            data-selected={displayType == 2 ? true : false}
            onClick={() => {
              setDisplayType(2);
            }}
          >
            <Text px={3}>Lootboxes</Text>
          </Button>
          <Button
            variant="whiteOutline"
            data-selected={displayType == 3 ? true : false}
            onClick={() => {
              setDisplayType(3);
            }}
          >
            <Text px={3}>Keystones</Text>
          </Button>
          <Button
            variant="whiteOutline"
            data-selected={displayType == 4 ? true : false}
            onClick={() => {
              setDisplayType(4);
            }}
          >
            <Text px={3}>Badges</Text>
          </Button>
          <Button
            variant="whiteOutline"
            data-selected={displayType == 5 ? true : false}
            onClick={() => {
              setDisplayType(5);
            }}
          >
            <Text px={3}>Miscellaneous</Text>
          </Button>
        </Flex>
        {!spyMode && (
          <Flex justifyContent="end">
            <Button
              variant="cuButton"
              color="white"
              bg="transparent"
              _hover={{
                backgroundColor: "#454545",
              }}
              onClick={() => {
                router.push({
                  pathname: "/games/CryptoUnicorns/leaderboard",
                });
              }}
            >
              Leaderboard
            </Button>
            <Button
              variant="cuButton"
              textColor="#D43F8C"
              borderColor="#FFFFFF"
              bgColor="white"
              onClick={() => {
                setSpyMode(true);
              }}
            >
              <Image
                src="https://s3.amazonaws.com/static.simiotics.com/play/cu/spy-icon.png"
                alt="Spy Mode"
                h={["12px", "14px", "16px"]}
                pr="2"
              ></Image>
              Spy Mode
            </Button>
          </Flex>
        )}
        {unicorns?.data && displayERC721List(unicorns.data, 0, false)}
        {lands?.data && displayERC721List(lands.data, 1, false)}
        {lootboxBalances?.data && displayCardList(lootboxes, 2)}
        {lootboxBalances?.data && displayCardList(keystones, 3)}
        {lootboxBalances?.data && displayCardList(badges, 4, false)}
        {lootboxBalances?.data && displayCardList(miscItems, 5)}
        {shadowcorns?.data &&
          displayERC721List(shadowcorns.data, 6, false, true)}
      </Flex>
    </Flex>
  );
};

export async function getStaticProps() {
  const metatags = {
    title: "Moonstream player portal: crypto unicorns",
    description: "Stash RBW and UNIM in game now!",
  };
  return {
    props: { metaTags: { DEFAULT_METATAGS, ...metatags } },
  };
}

CryptoUnicorns.getLayout = getLayout;

export default CryptoUnicorns;
