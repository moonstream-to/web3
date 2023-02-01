import React, { useState } from "react";
import { useQuery } from "react-query";
import {
  Flex,
  Text,
  Spinner,
  Spacer,
  Select,
  Link,
  HStack,
} from "@chakra-ui/react";
import RadioFilter from "../RadioFilter";
import http from "moonstream-components/src/core/utils/http";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";
import {
  Period,
  AssetType,
} from "moonstream-components/src/core/types/DashboardTypes";
import {
  UNICORN_CONTRACT_ADDRESS,
  LAND_CONTRACT_ADDRESS,
  SHADOWCORN_CONTRACT_ADDRESS,
} from "../../core/cu/constants";

const MostActiveUsers = ({ dataApi }: { dataApi: string }) => {
  const [volumePeriod, setVolumePeriod] = useState<Period>(Period.Day);
  const [userType, setUserType] = useState<string>("seller");
  const [userAssetType, setUserAssetType] = useState<AssetType>(
    AssetType.Unicorn
  );

  const getAssetAddress = () => {
    if (userAssetType == AssetType.Unicorn) return UNICORN_CONTRACT_ADDRESS;
    else if (userAssetType == AssetType.Land) return LAND_CONTRACT_ADDRESS;
    else return SHADOWCORN_CONTRACT_ADDRESS;
  };

  const activeUsersEndpoint = () => {
    const endpoint = `${dataApi}most_active_${userType}s/${getAssetAddress()}/${volumePeriod}/data.json`;
    return endpoint;
  };

  const fetchActiveUsers = async () => {
    return http(
      {
        method: "GET",
        url: activeUsersEndpoint(),
      },
      true
    );
  };

  const activeUsersData = useQuery(
    ["sales", volumePeriod, userType, userAssetType],
    () => {
      return fetchActiveUsers().then((res) => {
        console.log(res);
        return res.data.data;
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const buildOpenseaLink = (userId: string) => {
    return `https://opensea.io/${userId}`;
  };

  const handleChange = (value: string) => {
    if (value == "Shadowcorns") setUserAssetType(AssetType.Shadowcorn);
    else if (value == "Lands") setUserAssetType(AssetType.Land);
    else setUserAssetType(AssetType.Unicorn);
  };

  return (
    <Flex
      mt={10}
      w="600px"
      h="340px"
      p={5}
      bgColor="#2D2D2D"
      rounded="xl"
      flexDirection="column"
    >
      <HStack>
        <Text fontSize="lg" fontWeight="bold">
          Most Active Users
        </Text>
        <Spacer />
        <Flex mt={5}>
          <Select
            mr={4}
            w="200px"
            h="30px"
            borderRadius="20px"
            onChange={(e) => {
              setUserType(e.target.value);
            }}
          >
            <option value="seller">User Type: Sellers</option>
            <option value="buyer">User Type: Buyers</option>
          </Select>
          <Select
            w="120px"
            h="30px"
            borderRadius="20px"
            onChange={(e) => {
              setVolumePeriod(e.target.value as Period);
            }}
          >
            <option value={Period.Day}>1 day</option>
            <option value={Period.Week}>7 days</option>
            <option value={Period.Month}>30 days</option>
          </Select>
        </Flex>
      </HStack>
      <Flex>
        <RadioFilter
          list={["Unicorns", "Shadowcorns", "Lands"]}
          handleChange={handleChange}
        ></RadioFilter>
      </Flex>
      <Flex
        mt={8}
        mr={10}
        borderBottom="1px"
        borderColor="#8B8B8B"
        direction="row"
      >
        <Text fontWeight="bold">Address</Text>
        <Spacer />
        <Text fontWeight="bold">
          Units {userType == "seller" ? "sold" : "bought"}
        </Text>
      </Flex>
      {activeUsersData.data ? (
        <Flex mt={2} flexDirection="column" overflow="auto">
          {activeUsersData.data.map((item: any, idx: number) => {
            return (
              <Link
                key={idx}
                mb={2}
                _hover={{ bgColor: "#454545" }}
                href={buildOpenseaLink(item[userType])}
                isExternal
              >
                <HStack>
                  <code>{item[userType]}</code>
                  <Spacer />
                  <Text pr={10} key={`trans-${idx}`}>
                    {item["sale_count"]}
                  </Text>
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

export default MostActiveUsers;
