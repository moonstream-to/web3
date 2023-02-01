import React, { useContext } from "react";
import { useQuery } from "react-query";
import { Flex, HStack, Text, Spacer, Spinner } from "@chakra-ui/react";
import Web3Context from "moonstream-components/src/core/providers/Web3Provider/context";
import { useERC20 } from "moonstream-components/src/core/hooks";
import queryCacheProps from "moonstream-components/src/core/hooks/hookCommon";
import http from "moonstream-components/src/core/utils/http";
import {
  UNICORN_CONTRACT_ADDRESS,
  LAND_CONTRACT_ADDRESS,
  SHADOWCORN_CONTRACT_ADDRESS,
} from "../../core/cu/constants";

const TotalSupply = ({ dataApi }: { dataApi: string }) => {
  const web3ctx = useContext(Web3Context);

  const rbw = useERC20({
    contractAddress: "0x431CD3C9AC9Fc73644BF68bF5691f4B83F9E104f",
    spender: "0x0000000000000000000000000000000000000000",
    ctx: web3ctx,
    account: "0x0000000000000000000000000000000000000000",
  });

  const unim = useERC20({
    contractAddress: "0x64060aB139Feaae7f06Ca4E63189D86aDEb51691",
    spender: "0x0000000000000000000000000000000000000000",
    ctx: web3ctx,
    account: "0x0000000000000000000000000000000000000000",
  });

  const unicorns = useQuery(
    ["unicorns"],
    async () => {
      return http(
        {
          method: "GET",
          url: `${dataApi}total_supply_erc721/${UNICORN_CONTRACT_ADDRESS}/data.json`,
        },
        true
      ).then((res: any) => {
        return res.data.data;
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const lands = useQuery(
    ["lands"],
    async () => {
      return http(
        {
          method: "GET",
          url: `${dataApi}total_supply_erc721/${LAND_CONTRACT_ADDRESS}/data.json`,
        },
        true
      ).then((res: any) => {
        return res.data.data;
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  const shadowcorns = useQuery(
    ["shadowcorns"],
    async () => {
      return http(
        {
          method: "GET",
          url: `${dataApi}total_supply_erc721/${SHADOWCORN_CONTRACT_ADDRESS}/data.json`,
        },
        true
      ).then((res: any) => {
        return res.data.data;
      });
    },
    {
      ...queryCacheProps,
      onSuccess: () => {},
    }
  );

  return (
    <Flex w="600px" p={5} bgColor="#2D2D2D" rounded="xl" flexDirection="column">
      <Text fontSize="lg" fontWeight="bold">
        Total Supply
      </Text>
      <HStack mt="5" mb={2}>
        <Text fontWeight="bold">RBW</Text>
        <Spacer />
        {rbw.tokenState.data ? (
          <Text justifySelf="end">
            {Math.floor(
              Number(rbw.tokenState.data.totalSupply) * Math.pow(10, -18)
            )}
          </Text>
        ) : (
          <Spinner />
        )}
      </HStack>
      <HStack mb={2}>
        <Text fontWeight="bold">UNIM</Text>
        <Spacer />
        {unim.tokenState.data ? (
          <Text justifySelf="end">
            {Math.floor(
              Number(unim.tokenState.data.totalSupply) * Math.pow(10, -18)
            )}
          </Text>
        ) : (
          <Spinner />
        )}
      </HStack>
      <HStack mb={2}>
        <Text fontWeight="bold">Unicorns</Text>
        <Spacer />
        {unicorns.data ? (
          <Text justifySelf="end">{unicorns.data[0].total_supply}</Text>
        ) : (
          <Spinner />
        )}
      </HStack>
      <HStack mb={2}>
        <Text fontWeight="bold">Lands</Text>
        <Spacer />
        {lands.data ? (
          <Text justifySelf="end">{lands.data[0].total_supply}</Text>
        ) : (
          <Spinner />
        )}
      </HStack>
      <HStack mb={2}>
        <Text fontWeight="bold">Shadowcorns</Text>
        <Spacer />
        {shadowcorns.data ? (
          <Text justifySelf="end">{shadowcorns.data[0].total_supply}</Text>
        ) : (
          <Spinner />
        )}
      </HStack>
    </Flex>
  );
};

export default TotalSupply;
