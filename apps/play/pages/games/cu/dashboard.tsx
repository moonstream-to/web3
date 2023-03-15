import React, { useState } from "react";
import { useQuery } from "react-query";
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
import {
  Period,
  AssetType,
} from "moonstream-components/src/core/types/DashboardTypes";
import LineChart from "moonstream-components/src/components/LineChart";
import RecentSales from "moonstream-components/src/components/CryptoUnicorns/RecentSales";
import MostActiveUsers from "moonstream-components/src/components/CryptoUnicorns/MostActiveUsers";
import TotalSupply from "moonstream-components/src/components/CryptoUnicorns/TotalSupply";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";
import http from "moonstream-components/src/core/utils/http";

const DATA_API = "https://data.moonstream.to/prod/";

const Dashboard = () => {
  const [volumeAssetType, setVolumeAssetType] = useState<AssetType>(
    AssetType.UNIM
  );

  const getAssetAddress = () => {
    if (volumeAssetType == AssetType.UNIM)
      return "0x64060aB139Feaae7f06Ca4E63189D86aDEb51691";
    if (volumeAssetType == AssetType.RBW)
      return "0x431CD3C9AC9Fc73644BF68bF5691f4B83F9E104f";
    if (volumeAssetType == AssetType.Unicorn)
      return "0xdC0479CC5BbA033B3e7De9F178607150B3AbCe1f";
    if (volumeAssetType == AssetType.Land)
      return "0xA2a13cE1824F3916fC84C65e559391fc6674e6e8";
    return "0x0000000000000000000000000000000000000000";
  };

  const [volumePeriod, setVolumePeriod] = useState<Period>(Period.Day);
  const volumeEndpoint = () => {
    const endpoint = `${DATA_API}erc20_721_volume/${getAssetAddress()}/${volumePeriod}/data.json`;
    return endpoint;
  };

  const fetchVolume = async () => {
    return http(
      {
        method: "GET",
        url: volumeEndpoint(),
      },
      true
    );
  };

  const scaleERC20 = (value: number) => {
    return Math.floor(Math.pow(10, -18) * value);
  };

  const unim_volume = useQuery(
    ["unim_volume", volumePeriod, volumeAssetType],
    () => {
      return fetchVolume().then((res) => {
        try {
          const formattedData = [
            {
              id: "UNIM",
              color: "#F5468F",
              data: res.data.data.map((item: any) => {
                let volume: number = item.value;
                if (
                  volumeAssetType == AssetType.UNIM ||
                  volumeAssetType == AssetType.RBW
                )
                  volume = scaleERC20(volume);
                return {
                  x: item.time,
                  y: volume,
                };
              }),
            },
          ];
          return formattedData;
          // return LINE_CHART_TEST_DATA;
        } catch (err) {
          console.log(err);
        }
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const panelBackground = "#2D2D2D";
  const changeVolumePeriod = (index: Number) => {
    if (index == 1) setVolumePeriod(Period.Week);
    else if (index == 2) setVolumePeriod(Period.Month);
    else setVolumePeriod(Period.Day);
  };

  return (
    <Box
      className="Dashboard"
      borderRadius={"xl"}
      pt={10}
      minH="100vh"
      bgColor="#1A1D22"
    >
      <Heading>Crypto Unicorns Dashboard</Heading>
      <HStack my="10" alignItems="top">
        <VStack mr="40px">
          <Flex
            px="5"
            pt="5"
            w="600px"
            h="250px"
            bgColor={panelBackground}
            rounded="xl"
            flexDir="column"
          >
            <Flex>
              <Text fontSize="lg" fontWeight="bold">
                Trading Volume
              </Text>
              <Spacer />
              <Select
                w="150px"
                h="30px"
                onChange={(e) => {
                  setVolumeAssetType(e.target.value as AssetType);
                }}
              >
                <option value="UNIM">Unim</option>
                <option value="RBW">RBW</option>
                <option value="Unicorn">Unicorns</option>
                <option value="Land">Lands</option>
              </Select>
            </Flex>
            {unim_volume.data ? (
              <LineChart
                data={unim_volume.data}
                period={volumePeriod}
              ></LineChart>
            ) : (
              <Spinner />
            )}
          </Flex>
          <Flex mt={5}>
            <Tabs
              onChange={(index) => changeVolumePeriod(index)}
              variant="unstyled"
              defaultIndex={0}
            >
              <TabList>
                <Tab color="grey" _selected={{ color: "white" }}>
                  24H
                </Tab>
                <Tab color="grey" _selected={{ color: "white" }}>
                  1W
                </Tab>
                <Tab color="grey" _selected={{ color: "white" }}>
                  1M
                </Tab>
              </TabList>
            </Tabs>
          </Flex>
        </VStack>
        <TotalSupply dataApi={DATA_API}></TotalSupply>
      </HStack>

      <HStack my={5} alignItems="top">
        <RecentSales dataApi={DATA_API} />
        <MostActiveUsers dataApi={DATA_API} />
      </HStack>
    </Box>
  );
};

Dashboard.getLayout = getLayout;

export default Dashboard;
