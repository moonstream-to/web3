import React, { useState, useContext } from "react";
import { useQuery, useMutation } from "react-query";
import { getLayout } from "moonstream-components/src/layouts/EngineLayout";
import { Box, Heading, HStack, Spacer } from "@chakra-ui/react";
import http from "moonstream-components/src/core/utils/http";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
const GardenABI = require("../../games/GoFPABI.json");
import { GOFPFacet as GardenABIType } from "../../../../types/contracts/GOFPFacet";
// const MulticallABI = require("../../games/cu/Multicall2.json");
// import { Multicall2 } from "../../games/cu/Multicall2";
const ERC721MetadataABI = require("../../../../abi/MockERC721.json");
import { MockERC721 } from "../../../../types/contracts/MockERC721";
import SessionPanel from "../../components/gofp/GoFPSessionPanel";
import MetadataPanel from "../../components/gofp/GoFPMetadataPanel";
import CharacterPanel from "../../components/gofp/GoFPCharacterPanel";
import { SessionMetadata } from "../../components/gofp/GoFPTypes";
import {
  hookCommon,
  useRouter,
  useToast,
} from "moonstream-components/src/core/hooks";
// import {
//   chainByChainId,
// } from "moonstream-components/src/core/providers/Web3Provider";

const Garden = () => {
  const router = useRouter();
  const toast = useToast();

  const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";
  const web3ctx = useContext(Web3Context);

  const generatePathId = (stage: number, path: number) => {
    return `stage_${stage}_path_${path}`;
  };

  const [selectedStage, setSelectedStage] = useState<number>(1);
  const [selectedPath, setSelectedPath] = useState<number>(1);
  const [gardenContractAddress] = useState<string>(
    router.query["contractId"] || ZERO_ADDRESS
  );
  const [sessionId] = useState<number>(router.query["sessionId"]);
  const [tokenContract, setTokenContract] = useState<any>();
  // Not sure if we need to do anything basedo n ChainId
  // useEffect(() => {
  //   const chain: string | undefined = chainByChainId[web3ctx.chainId];
  //   if (!chain || !gardenContractAddress) {
  //     setGardenContractAddress("0x0000000000000000000000000000000000000000");
  //   }
  // }, [web3ctx.chainId]);

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
      const info = await gardenContract.methods.getSession(sessionId).call();

      console.log("Session Info: ");
      console.log(info);
      console.log(info[0]);
      return info;
    },
    {
      ...hookCommon,
    }
  );

  const sessionMetadata = useQuery<SessionMetadata | undefined>(
    ["get_metadata", sessionInfo],
    async () => {
      if (!sessionInfo || !sessionInfo.data) {
        return;
      }

      const uri = sessionInfo.data[5];

      return fetchMetadataUri(uri).then((res) => {
        return res.data as SessionMetadata;
      });
    },
    {
      ...hookCommon,
    }
  );

  const currentStage = useQuery<number>(
    ["get_current_stage", gardenContractAddress, sessionId, sessionInfo],
    async () => {
      if (
        gardenContractAddress == ZERO_ADDRESS ||
        sessionId < 1 ||
        !sessionInfo.data
      )
        return 1;

      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      const result = await gardenContract.methods
        .getCurrentStage(sessionId)
        .call();
      const _stage = parseInt(result);
      console.log("Current stage is ", _stage);
      setSelectedStage(Math.min(_stage, sessionInfo.data[6].length));
      return _stage;
    },
    {
      ...hookCommon,
      refetchInterval: 15 * 1000,
    }
  );

  const correctPaths = useQuery<number[]>(
    ["get_correct_paths", gardenContractAddress, sessionId, currentStage],
    async () => {
      const answers: number[] = [];

      if (
        gardenContractAddress == ZERO_ADDRESS ||
        sessionId < 1 ||
        !currentStage.data ||
        currentStage.data <= 1
      )
        return answers;

      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      for (let i = 1; i < currentStage.data; i++) {
        const ans = await gardenContract.methods
          .getCorrectPathForStage(sessionId, i)
          .call();
        answers.push(parseInt(ans));
      }

      console.log("Correct paths ", answers);
      return answers;
    },
    {
      ...hookCommon,
    }
  );

  const userOwnedTokens = useQuery<number[]>(
    ["get_token", sessionInfo],
    async () => {
      if (!sessionInfo || !sessionInfo.data) {
        return [];
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

      console.log("Owned balance: ", balance);

      const tokens = [];

      for (let i = 0; i < parseInt(balance); i++) {
        const tok = await tokenContract.methods
          .tokenOfOwnerByIndex(web3ctx.account, i)
          .call();
        tokens.push(parseInt(tok));
      }

      console.log("User owned tokens: ", tokens);

      return tokens;
    },
    {
      ...hookCommon,
    }
  );

  const stakedTokens = useQuery<number[]>(
    ["get_token", gardenContractAddress, sessionId, web3ctx.account],
    async () => {
      if (
        gardenContractAddress == ZERO_ADDRESS ||
        sessionId < 1 ||
        !web3ctx.account
      )
        return [];

      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      console.log("Fetching staked tokens...");

      const balance = await gardenContract.methods
        .numTokensStakedIntoSession(sessionId, web3ctx.account)
        .call();

      console.log("Staked balance: ", balance);

      const tokens = [];

      for (let i = 1; i <= parseInt(balance); i++) {
        const tok = await gardenContract.methods
          .tokenOfStakerInSessionByIndex(sessionId, web3ctx.account, i)
          .call();
        tokens.push(parseInt(tok));
      }

      console.log("Staked: ", tokens);

      return tokens;
    },
    {
      ...hookCommon,
    }
  );

  const tokenMetadata = useQuery<any>(
    ["get_token", stakedTokens, userOwnedTokens, sessionInfo],
    async () => {
      if (!sessionInfo.data || !stakedTokens.data || !userOwnedTokens.data) {
        return undefined;
      }

      const tokenAddress = sessionInfo.data[0];
      const tokenContract = new web3ctx.web3.eth.Contract(
        ERC721MetadataABI
      ) as unknown as MockERC721;
      tokenContract.options.address = tokenAddress;

      // Need to get Multicall2 address on Mumbai.
      // const multicallContract = new web3ctx.polygonClient.eth.Contract(
      //   MulticallABI,
      //   MULTICALL2_CONTRACT_ADDRESS
      // );

      const tokenIds = stakedTokens.data.concat(userOwnedTokens.data);
      console.log("Fetching metdata for ", tokenIds);
      console.log("Character contract ", tokenAddress);

      const tokenMetadata: any = {};

      for (let i = 0; i < tokenIds.length; i++) {
        const uri = await tokenContract.methods.tokenURI(tokenIds[i]).call();
        const metadata = await fetchMetadataUri(uri);
        console.log(metadata);
        tokenMetadata[tokenIds[i]] = metadata.data;
      }

      // let tokenMetdataQueries = [];
      // for (let i = 0; i < tokenIds.length; i++) {
      //   tokenMetdataQueries.push({
      //     target: tokenAddress,
      //     callData: tokenContract.methods.tokenURI(tokenIds[i]).encodeABI(),
      //   });
      // }

      // return multicallContract.methods
      //   .tryAggregate(false, tokenMetdataQueries)
      //   .call()
      //   .then((results: any[]) => {
      //     console.log("Metadata URIs");
      //     console.log(results);
      //     return {};
      //   });

      console.log(tokenMetadata);
      return tokenMetadata;
    },
    {
      ...hookCommon,
    }
  );

  const setApproval = useMutation(
    () => {
      return tokenContract.methods
        .setApprovalForAll(gardenContractAddress, true)
        .send({
          from: web3ctx.account,
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
    (tokenIds: number[]) => {
      console.log(
        "Attempting to stake ",
        tokenIds,
        " into session ",
        sessionId,
        "."
      );
      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;
      return gardenContract.methods
        .stakeTokensIntoSession(sessionId, tokenIds)
        .send({
          from: web3ctx.account,
        });
    },
    {
      onSuccess: () => {
        toast("Staking successful.", "success");
        userOwnedTokens.refetch();
        stakedTokens.refetch();
      },
      onError: (error) => {
        toast("Staking failed.", "error");
        console.error(error);
      },
    }
  );

  const unstakeTokens = useMutation(
    (tokenIds: number[]) => {
      console.log(
        "Attempting to unstake ",
        tokenIds,
        " from session ",
        sessionId,
        "."
      );
      console.log(gardenContractAddress);
      console.log(web3ctx.account);
      const gardenContract = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;

      if (!stakedTokens.data) {
        throw new Error("Missing staked token data.");
      }

      return gardenContract.methods
        .unstakeTokensFromSession(sessionId, tokenIds)
        .send({
          from: web3ctx.account,
        });
    },
    {
      onSuccess: () => {
        toast("Unstaking successful.", "success");
        userOwnedTokens.refetch();
        stakedTokens.refetch();
      },
      onError: (error) => {
        toast("Unstaking failed.", "error");
        console.error(error);
      },
    }
  );

  const choosePath = useMutation<unknown, unknown, number, unknown>(
    (path) => {
      console.log(
        "Attempting to choose path ",
        path,
        " in stage ",
        currentStage,
        "for tokens ",
        stakedTokens.data,
        "."
      );
      const gardenContract: any = new web3ctx.web3.eth.Contract(
        GardenABI
      ) as any as GardenABIType;
      gardenContract.options.address = gardenContractAddress;
      return gardenContract.methods
        .chooseCurrentStagePaths(sessionId, stakedTokens.data, [path])
        .send({
          from: web3ctx.account,
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
      {sessionMetadata.data && (
        <HStack my="10" alignItems="top">
          <MetadataPanel
            sessionMetadata={sessionMetadata.data}
            selectedStage={selectedStage}
          />
          <Spacer />
          <SessionPanel
            sessionMetadata={sessionMetadata.data}
            currentStage={currentStage}
            correctPaths={correctPaths}
            generatePathId={generatePathId}
            setSelectedStage={setSelectedStage}
            setSelectedPath={setSelectedPath}
          />
          <Spacer />
          <CharacterPanel
            // sessionMetadata={sessionMetadata.data}
            ownedTokens={userOwnedTokens.data || []}
            stakedTokens={stakedTokens.data || []}
            tokenMetadata={tokenMetadata.data}
            path={selectedPath}
            setApproval={setApproval}
            stakeTokens={stakeTokens}
            unstakeTokens={unstakeTokens}
            choosePath={choosePath}
          ></CharacterPanel>
        </HStack>
      )}
    </Box>
  );
};

Garden.getLayout = getLayout;

export default Garden;
