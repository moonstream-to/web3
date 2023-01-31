import React, { useState, useContext, useEffect } from "react";
import { useQuery, useMutation } from "react-query";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import {
  Box,
  Heading,
  Spinner,
  Flex,
  HStack,
  VStack,
  Spacer,
  Text,
  Tabs,
  TabList,
  Tab,
  Select,
} from "@chakra-ui/react";
import http from "moonstream-components/src/core/utils/http";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
const GardenABI = require("../../games/GoFPABI.json");
import { GOFPFacet as GardenABIType } from "../../../../types/contracts/GOFPFacet";
const MulticallABI = require("../../games/cu/Multicall2.json");
import { Multicall2 } from "../../games/cu/Multicall2";
const ERC721MetadataABI = require("../../../../abi/MockERC721.json");
import { MockERC721 } from "../../../../types/contracts/MockERC721";
import { GOFP_CONTRACT_ADDRESS, MULTICALL2_CONTRACT_ADDRESS, SHADOWCORN_CONTRACT_ADDRESS } from "moonstream-components/src/core/cu/constants";
import SessionPanel from "moonstream-components/src/components/GoFPSessionPanel";
import MetadataPanel from "moonstream-components/src/components/GoFPMetadataPanel";
import CharacterPanel from "moonstream-components/src/components/GoFPCharacterPanel";
import { SessionMetadata, StageMetadata, PathMetadata} from "moonstream-components/src/components/GoFPTypes"
import { hookCommon, useToast } from "moonstream-components/src/core/hooks";
import {
  chainByChainId,
} from "moonstream-components/src/core/providers/Web3Provider";

const DATA_API = "https://data.moonstream.to/prod/";

const Garden = () => {
  const toast = useToast();

  const MY_ADDRESS = "0x9f8B214bF13F62cFA5160ED135E233C9dDb95974";
  const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";
  const web3ctx = useContext(Web3Context);

  const panelBackground = "#2D2D2D";

  const generatePathId = (stage: number, path: number) => {
    return `stage_${stage}_path_${path}`;
  };

  const [selectedStage, setSelectedStage] = React.useState<number>(1);
  const [selectedPath, setSelectedPath] = React.useState<number>(0);
  const [gardenContractAddress, setGardenContractAddress] = React.useState<string>(ZERO_ADDRESS);
  const [sessionId, setSessionId] = React.useState<number>(101);
  const [tokenContract, setTokenContract] = React.useState<any>();

  useEffect(() => {
    const chain: string | undefined = chainByChainId[web3ctx.chainId];
    if (!chain) {
      setGardenContractAddress("0x0000000000000000000000000000000000000000");
    } else {
      setGardenContractAddress("0x8b9493d84e70e94ff9EB1385aD0ed632FD5edE13")
    }
  }, [web3ctx.chainId]);

  const fetchMetadataUri = async (uri: string) => {
    return http(
      {
        method: "GET",
        url: uri,
      },
      true
    );
  };

  const sessionInfo = useQuery(
    ["get_session", gardenContractAddress, sessionId],
    async () => {
      if (gardenContractAddress == ZERO_ADDRESS || sessionId < 1) return null;

      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      console.log("Attempting to fetch session.");
      const info = await gardenContract.methods
                    .getSession(sessionId)
                    .call();

      console.log("Session Info: ");
      console.log(info);
      console.log(info[0]);
      return info;
    },
    {
      ...hookCommon,
    }
  );

  const sessionMetadata = useQuery<SessionMetadata|undefined>(
    ["get_metadata", sessionInfo],
    async () => {
      if (!sessionInfo || !sessionInfo.data) {
        return;
      }

      const uri = sessionInfo.data[5];

      return fetchMetadataUri(uri).then((res) => {
        console.log(res.data);
        return res.data as SessionMetadata;
      });
    },
    {
      ...hookCommon,
    }
  );

  const currentStage = useQuery<number>(
    ["get_current_stage", gardenContractAddress, sessionId],
    async () => {
      if(gardenContractAddress == ZERO_ADDRESS || sessionId < 1) return 1;

      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      const result = await gardenContract.methods
                      .getCurrentStage(sessionId)
                      .call();
      const _stage = parseInt(result);
      console.log("Current stage is ", _stage);
      setSelectedStage(_stage);
      return _stage;
    },
    {
      ...hookCommon,
      refetchInterval: 30 * 1000
    }
  );

  const correctPaths = useQuery<number[]>(
    ["get_correct_paths", gardenContractAddress, sessionId, currentStage],
    async () => {
      const answers: number[] = [];

      if(gardenContractAddress == ZERO_ADDRESS 
          || sessionId < 1 
          || !currentStage.data 
          || currentStage.data <= 1) return answers;

      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      for(let i = 1; i < currentStage.data; i++) {
        const ans = await gardenContract.methods
                            .getCorrectPathForStage(sessionId, i)
                            .call();
        answers.push(parseInt(ans));
      }
      
      console.log("Correct paths ", answers);
      return answers;
    },
    {
      ...hookCommon
    }
  );

  const tokenIds = useQuery(
    ["get_token", sessionInfo],
    async () => {
      if (!sessionInfo || !sessionInfo.data) {
        return;
      }

      const tokenAddress = sessionInfo.data[0];

      console.log("Token address: ", tokenAddress);

      const tokenContract = new web3ctx.web3.eth.Contract(
        ERC721MetadataABI
      ) as unknown as MockERC721;
      tokenContract.options.address = tokenAddress;

      setTokenContract(tokenContract);

      const balance = await tokenContract.methods
        .balanceOf(web3ctx.account)
        .call();

      console.log("Balance: ", balance);

      const firstTokenId = await tokenContract.methods
        .tokenOfOwnerByIndex(web3ctx.account, 0)
        .call();

      console.log("First token: ", firstTokenId);

      return [firstTokenId];
    },
    {
      ...hookCommon,
    }
  );

  const setApproval = useMutation(
    () => {
      return tokenContract.methods.setApprovalForAll(gardenContractAddress, true).send({
        from: web3ctx.account
      });
    },
    {
      onSuccess: () => {
        toast("SetApproval successful.", "success");
      },
      onError: () => {
        toast("SetApproval failed.", "error");
      },
    }
  );

  const stakeTokens = useMutation(
    () => {
      console.log("Attempting to stake ", tokenIds.data, " into session ", sessionId, ".");
      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;
      return gardenContract.methods.stakeTokensIntoSession(sessionId, tokenIds.data).send({
        from: web3ctx.account
      });
    },
    {
      onSuccess: () => {
        toast("Staking successful.", "success");
      },
      onError: (error) => {
        toast("Staking failed.", "error");
        console.error(error);
      },
    }
  );

  const unstakeTokens = useMutation(
    () => {
      console.log("Attempting to unstake ", [18], " from session ", sessionId, ".");
      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;
      return gardenContract.methods.unstakeTokensFromSession(sessionId, [18]).send({
        from: web3ctx.account
      });
    },
    {
      onSuccess: () => {
        toast("Unstaking successful.", "success");
      },
      onError: (error) => {
        toast("Unstaking failed.", "error");
        console.error(error);
      },
    }
  );

  const choosePath = useMutation(
    (path) => {
      console.log("Attempting to choose path ", path, " in stage ", currentStage, "for tokens ", tokenIds.data, ".");
      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;
      return gardenContract.methods.chooseCurrentStagePaths(sessionId, tokenIds.data, [path]).send({
        from: web3ctx.account
      });
    },
    {
      onSuccess: () => {
        toast("Path choice successful.", "success");
      },
      onError: (error) => {
        toast("Path choice failed.", "error");
        console.error(error);
      },
    }
  );

  return (
    <Box
      className="Garden"
      borderRadius={"xl"}
      pt={10}
      minH="100vh"
      bgColor="#1A1D22"
    >
      <Heading>Garden of Forking Paths</Heading>
      {sessionMetadata?.data &&
        <HStack my="10" alignItems="top">
          <CharacterPanel sessionMetadata={sessionMetadata.data} path={selectedPath} setApproval={setApproval} stakeTokens={stakeTokens} unstakeTokens={unstakeTokens} choosePath={choosePath}></CharacterPanel>
          <SessionPanel sessionMetadata={sessionMetadata.data} currentStage={currentStage} correctPaths={correctPaths} generatePathId={generatePathId} setSelectedStage={setSelectedStage} setSelectedPath={setSelectedPath} />
          <Spacer />
          <MetadataPanel sessionMetadata={sessionMetadata.data} selectedStage={selectedStage} />
        </HStack>
      }
    </Box>
  );
};

Garden.getLayout = getLayout;

export default Garden;
