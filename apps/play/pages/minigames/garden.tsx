import React, { useContext, useState } from "react";
import { getLayout } from "moonstream-components/src/layoutsForPlay/EngineLayout";
import { Box, Heading, HStack, Flex } from "@chakra-ui/react";

import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
const GardenABI = require("../../games/GoFPABI.json");
import { GOFPFacet as GardenABIType } from "../../../../types/contracts/GOFPFacet";
const MulticallABI = require("../../games/cu/Multicall2.json");
const ERC721MetadataABI = require("../../../../abi/MockERC721.json");
import { MockERC721 } from "../../../../types/contracts/MockERC721";
import {
  GOFP_CONTRACT_ADDRESS,
  MULTICALL2_CONTRACT_ADDRESS,
  SHADOWCORN_CONTRACT_ADDRESS,
} from "moonstream-components/src/core/cu/constants";
import SessionPanel from "moonstream-components/src/components/GoFPSessionPanel";
import { SessionMetadata } from "./GoFPTypes";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { TouchBackend } from "react-dnd-touch-backend";
import { usePreview } from "react-dnd-preview";
import { default as Character } from "../../components/GoFPCharacter";

const DATA_API = "https://data.moonstream.to/prod/";

const Garden = () => {
  const MY_ADDRESS = "0x9f8B214bF13F62cFA5160ED135E233C9dDb95974";
  // console.log(GardenABI);
  const web3ctx = useContext(Web3Context);
  const gardenContract = new web3ctx.polygonClient.eth.Contract(
    GardenABI,
    GOFP_CONTRACT_ADDRESS
  ) as any as GardenABIType;
  const multicallContract = new web3ctx.polygonClient.eth.Contract(
    MulticallABI,
    MULTICALL2_CONTRACT_ADDRESS
  );
  const shadowcornsContract = new web3ctx.web3.eth.Contract(
    ERC721MetadataABI,
    SHADOWCORN_CONTRACT_ADDRESS
  ) as unknown as MockERC721;
  let sessionStakeQueries = [
    {
      target: GOFP_CONTRACT_ADDRESS,
      callData: gardenContract.methods
        .numTokensStakedIntoSession(1, MY_ADDRESS)
        .encodeABI(),
    },
    {
      target: GOFP_CONTRACT_ADDRESS,
      callData: gardenContract.methods
        .numTokensStakedIntoSession(2, MY_ADDRESS)
        .encodeABI(),
    },
    {
      target: GOFP_CONTRACT_ADDRESS,
      callData: gardenContract.methods
        .numTokensStakedIntoSession(3, MY_ADDRESS)
        .encodeABI(),
    },
  ];

  let ownerOfQueries = [
    {
      target: SHADOWCORN_CONTRACT_ADDRESS,
      callData: shadowcornsContract.methods.ownerOf(1).encodeABI(),
    },
    {
      target: SHADOWCORN_CONTRACT_ADDRESS,
      callData: shadowcornsContract.methods.ownerOf(2).encodeABI(),
    },
    {
      target: SHADOWCORN_CONTRACT_ADDRESS,
      callData: shadowcornsContract.methods.ownerOf(3).encodeABI(),
    },
  ];

  multicallContract.methods
    .tryAggregate(false, sessionStakeQueries)
    .call()
    .then((results: any[]) => {
      let stakedTokenQueries: any[] = [];
      results.forEach((result, i) => {
        let j = 1;
        const numTokensInSession = Number(result[1]);
        for (j = 1; j <= numTokensInSession; j++)
          stakedTokenQueries.push({
            target: GOFP_CONTRACT_ADDRESS,
            callData: gardenContract.methods
              .tokenOfStakerInSessionByIndex(i + 1, MY_ADDRESS, j)
              .encodeABI(),
          });
      });

      return multicallContract.methods
        .tryAggregate(false, stakedTokenQueries)
        .call();
    })
    .then(console.log("qq"));
  // const fetchVolume = async () => {
  //   return http(
  //     {
  //       method: "GET",
  //       url: volumeEndpoint(),
  //     },
  //     true
  //   );
  // };

  // const scaleERC20 = (value: number) => {
  //   return Math.floor(Math.pow(10, -18) * value);
  // };

  // const unim_volume = useQuery(
  //   ["unim_volume", volumePeriod, volumeAssetType],
  //   () => {
  //     return fetchVolume().then((res) => {
  //       try {
  //         const formattedData = [
  //           {
  //             id: "UNIM",
  //             color: "#F5468F",
  //             data: res.data.data.map((item: any) => {
  //               let volume: number = item.value;
  //               if (
  //                 volumeAssetType == AssetType.UNIM ||
  //                 volumeAssetType == AssetType.RBW
  //               )
  //                 volume = scaleERC20(volume);
  //               return {
  //                 x: item.time,
  //                 y: volume,
  //               };
  //             }),
  //           },
  //         ];
  //         return formattedData;
  //         // return LINE_CHART_TEST_DATA;
  //       } catch (err) {
  //         console.log(err);
  //       }
  //     });
  //   },
  //   {
  //     ...queryCacheProps,
  //     onSuccess: () => {},
  //   }
  // );

  const panelBackground = "#2D2D2D";
  // const changeVolumePeriod = (index: Number) => {
  //   if (index == 1) setVolumePeriod(Period.Week);
  //   else if (index == 2) setVolumePeriod(Period.Month);
  //   else setVolumePeriod(Period.Day);
  // };

  const sessionData: SessionMetadata = {
    lore: "Choose your paths carefully to destroy the ring",
    imageUrl: "",
    stages: [
      {
        lore: "Choose your first path",
        imageUrl: "",
        paths: [
          {
            lore: "",
            imageUrl:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQd1dHOHHLoULDmElWCEsoECVnZC--pKM3R5A&usqp=CAU",
          },
          {
            lore: "",
            imageUrl:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSKLyKo4XaiM8nmvCbh4rQfzU9hUgtdWMI0Ow&usqp=CAU",
          },
          {
            lore: "",
            imageUrl:
              "https://static8.depositphotos.com/1529496/993/i/600/depositphotos_9938676-stock-photo-stairway-to-forest.jpg",
          },
        ],
      },
      {
        lore: "Choose your second path",
        imageUrl: "",
        paths: [
          {
            lore: "",
            imageUrl:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQOmAZPGeabh12-ICI83pFy7tQtjQLlgYNi-Q&usqp=CAU",
          },
          {
            lore: "",
            imageUrl:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWe9gbq9hHm6M2izUXxv4sDyW3rDZ9iN832A&usqp=CAU",
          },
          {
            lore: "",
            imageUrl:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT-vvbStZedOAkqb31qrnw1zkahZaPIX4ZwWg&usqp=CAU",
          },
        ],
      },
      {
        lore: "Choose your third path",
        imageUrl: "",
        isCurrent: true,
        paths: [
          {
            lore: "",
            imageUrl:
              "https://media.gettyimages.com/id/683732297/photo/storm-vehicle-with-the-center-for-severe-weather-research-driving-into-the-path-of-tornado.jpg?s=1024x1024&w=gi&k=20&c=aiGZkG7T_J9es9a1eTGyKr-ke2HesoPfuWHRO8OPJJM=",
          },
          {
            lore: "",
            imageUrl:
              "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRV4ccN4oFjMwSuPa5PA2Pr7As7v0v3zIZL3g&usqp=CAU",
          },
          {
            lore: "",
            imageUrl:
              "https://media.gettyimages.com/id/683732297/photo/storm-vehicle-with-the-center-for-severe-weather-research-driving-into-the-path-of-tornado.jpg?s=1024x1024&w=gi&k=20&c=aiGZkG7T_J9es9a1eTGyKr-ke2HesoPfuWHRO8OPJJM=",
          },
          {
            lore: "",
            imageUrl:
              "data:image/jpeg;base64,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",
          },
        ],
      },
    ],
  };

  const [availableCharacters, setAvailableCharacters] = useState([
    "Frodo",
    "Sam",
    "Pippin",
  ]);

  const handleDrop = (name) => {
    console.log(name);

    setAvailableCharacters((prev) => {
      console.log(prev);
      const newChars = prev.filter((char) => {
        console.log(char, name);
        return char !== name.name;
      });
      console.log("qq", newChars);

      return newChars;
    });
  };

  function isTouchDevice() {
    console.log("ontouchstart" in window || navigator.maxTouchPoints > 0);
    return "ontouchstart" in window || navigator.maxTouchPoints > 0;
  }
  const MyPreview = () => {
    const preview = usePreview();
    if (!preview.display) {
      return null;
    }
    const { itemType, item, style } = preview;
    return (
      <div className="item-list__item" style={style}>
        {itemType}
      </div>
    );
  };

  return (
    <Box
      className="Garden"
      borderRadius={"xl"}
      pt={10}
      minH="100vh"
      bgColor="#1A1D22"
    >
      <DndProvider backend={isTouchDevice() ? TouchBackend : HTML5Backend}>
        {isTouchDevice() && <MyPreview />}
        <Heading>Garden of Forking Paths</Heading>
        <Flex alignItems="center">
          <HStack my="10" alignItems="top" mr="20px">
            {/* <ResizeObserver onResize={handleResize}> */}
            <SessionPanel
              sessionMetadata={sessionData}
              onDrop={(item) => handleDrop(item)}
              // links={links}
            />
            {/* </ResizeObserver> */}
          </HStack>
          <Flex direction="column" gap="15px">
            {availableCharacters.map((char, idx) => {
              return <Character character={char} key={idx} />;
            })}
          </Flex>
        </Flex>
      </DndProvider>
    </Box>
  );
};

Garden.getLayout = getLayout;

export default Garden;
