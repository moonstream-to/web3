import React, { useState } from "react";
import { useQuery } from "react-query";
import { Flex, Text, Spinner, Link, HStack, Spacer } from "@chakra-ui/react";
import RadioFilter from "../RadioFilter";
import http from "moonstream-components/src/core/utils/http";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";
import { AssetType } from "moonstream-components/src/core/types/DashboardTypes";
import {
  UNICORN_CONTRACT_ADDRESS,
  LAND_CONTRACT_ADDRESS,
  SHADOWCORN_CONTRACT_ADDRESS,
} from "../../core/cu/constants";

const RecentSales = ({ dataApi }: { dataApi: string }) => {
  const [salesAssetType, setSalesAssetType] = useState<AssetType>(
    AssetType.Unicorn
  );

  const getAssetAddress = () => {
    if (salesAssetType == AssetType.Unicorn) return UNICORN_CONTRACT_ADDRESS;
    else if (salesAssetType == AssetType.Land) return LAND_CONTRACT_ADDRESS;
    else return SHADOWCORN_CONTRACT_ADDRESS;
  };

  const salesEndpoint = () => {
    const endpoint = `${dataApi}most_recent_sale/${getAssetAddress()}/10/data.json`;
    return endpoint;
  };

  const fetchSales = async () => {
    return http(
      {
        method: "GET",
        url: salesEndpoint(),
      },
      true
    );
  };

  const salesData = useQuery(
    ["sales", salesAssetType],
    () => {
      return fetchSales().then((res) => {
        return res.data.data;
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const displayTimeGap = (timestamp: number) => {
    var currentSeconds = new Date().getTime() / 1000;
    var timePassed = currentSeconds - timestamp;
    if (timePassed < 120) {
      // less than 2 minutes
      return "just now";
    } else if (timePassed < 7200) {
      // less than 2 hours
      var minutesPassed = Math.floor(timePassed / 60);
      return `${minutesPassed} minutes ago`;
    } else if (timePassed < 172800) {
      // less than 2 days
      var hoursPassed = Math.floor(timePassed / 3600);
      return `${hoursPassed} hours ago`;
    } else {
      // more than 2 days
      var daysPassed = Math.floor(timePassed / 86400);
      return `${daysPassed} days ago`;
    }
  };

  // var now = new Date().getTime() / 1000;
  // console.log(displayTimeGap(now - 65));
  // console.log(displayTimeGap(now - 135));
  // console.log(displayTimeGap(now - 4500));
  // console.log(displayTimeGap(now - 11000));
  // console.log(displayTimeGap(now - 100000));
  // console.log(displayTimeGap(1661700846));

  const handleChange = (value: string) => {
    if (value == "Shadowcorns") setSalesAssetType(AssetType.Shadowcorn);
    else if (value == "Lands") setSalesAssetType(AssetType.Land);
    else setSalesAssetType(AssetType.Unicorn);
  };

  const buildOpenseaLink = (tokenId: string) => {
    return `https://opensea.io/assets/matic/${getAssetAddress()}/${tokenId}`;
  };

  return (
    <Flex
      w="600px"
      h="340px"
      mr="40px"
      p={5}
      bgColor="#2D2D2D"
      rounded="xl"
      flexDirection="column"
    >
      <Text fontSize="lg" fontWeight="bold">
        Recent Sales
      </Text>
      <RadioFilter
        list={["Unicorns", "Shadowcorns", "Lands"]}
        handleChange={handleChange}
      ></RadioFilter>
      <Flex
        mt={8}
        mr={10}
        borderBottom="1px"
        borderColor="#8B8B8B"
        direction="row"
      >
        <Text fontWeight="bold">Item id</Text>
        <Spacer />
        <Text fontWeight="bold">Sale time</Text>
      </Flex>
      {salesData.data ? (
        <Flex mt={2} flexDirection="column" overflow="auto">
          {salesData.data.map((item: any, idx: number) => {
            return (
              <Link
                key={idx}
                mb={2}
                _hover={{ bgColor: "#454545" }}
                href={buildOpenseaLink(item.token_id)}
                isExternal
              >
                <HStack>
                  <Text>{item.token_id}</Text>
                  <Spacer />
                  <Text pr={10}>{displayTimeGap(item.block_timestamp)}</Text>
                </HStack>
              </Link>
            );
          })}
        </Flex>
      ) : (
        <Spinner />
      )}
    </Flex>
  );
};

export default RecentSales;
