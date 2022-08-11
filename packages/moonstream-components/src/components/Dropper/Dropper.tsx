import React, { useContext } from "react";
import {
  Flex,
  Spinner,
  Text,
  Heading,
  Skeleton,
  Editable,
  EditablePreview,
  EditableInput,
} from "@chakra-ui/react";
import Claim from "./Claim";
import Web3Context from "../../core/providers/Web3Provider/context";
import Paginator from "../Paginator";
import { ClaimInterface } from "../../../../../types/Moonstream";
import { useDropperContract, useDrops } from "../../core/hooks/dropper";
const Dropper = ({
  contractAddress,
  children,
  ...props
}: {
  contractAddress: string;
  children: React.ReactNode;
  props: any;
}) => {
  const web3ctx = useContext(Web3Context);

  const dropper = useDropperContract({
    dropperAddress: contractAddress,
    ctx: web3ctx,
  });

  const { adminClaims, pageOptions, dropperContracts } = useDrops({
    dropperAddress: contractAddress,
    ctx: web3ctx,
  });

  if (!contractAddress)
    return <Text>{"Please specify terminus address "}</Text>;
  if (
    dropper.contractState.isLoading ||
    !dropper.contractState.data ||
    dropperContracts.isLoading
  )
    return <Spinner />;

  return (
    <Flex
      w="100%"
      minH="100vh"
      direction={"column"}
      id="flexid"
      alignSelf={"center"}
      {...props}
    >
      <Flex bgColor="blue.1000" p={[0, 0, 4, null]} direction="column">
        <Heading>
          <Editable
            submitOnBlur={false}
            bgColor={"blue.700"}
            size="sm"
            fontSize={"sm"}
            textColor="gray.500"
            w="100%"
            minW={["280px", "300px", "360px", "420px", null]}
            variant={"outline"}
            placeholder={"Contract title"}
            defaultValue={
              dropperContracts.data.find(
                (element: any) => element.address === contractAddress
              )?.title
            }
            isDisabled={
              true ||
              dropper.contractState.isLoading ||
              dropper.contractState.data?.owner !== web3ctx.account
            }
          >
            <Skeleton
              colorScheme={"orange"}
              isLoaded={
                !dropper.contractState.isLoading &&
                !dropper.transferOwnership.isLoading
              }
            >
              <EditablePreview w="100%" px={2} />
              <EditableInput w="100%" px={2} />
            </Skeleton>
          </Editable>
        </Heading>
        <Flex direction={"column"} bgColor="blue.1000" flexWrap={"wrap"}>
          <code key={"PoolController"}>
            Owner:
            <Editable
              submitOnBlur={false}
              bgColor={"blue.700"}
              size="sm"
              fontSize={"sm"}
              textColor="gray.500"
              w="100%"
              minW={["280px", "300px", "360px", "420px", null]}
              variant={"outline"}
              placeholder={
                dropper.contractState.data.owner === web3ctx.account
                  ? "You ;) "
                  : dropper.contractState.data?.owner
              }
              defaultValue=""
              isDisabled={
                dropper.contractState.isLoading ||
                dropper.contractState.data.owner !== web3ctx.account
              }
              onSubmit={(nextValue) => {
                const _checksumAddress =
                  web3ctx.web3.utils.toChecksumAddress(nextValue);
                if (web3ctx.web3.utils.isAddress(_checksumAddress)) {
                  dropper.transferOwnership.mutate({ to: _checksumAddress });
                }
              }}
            >
              <Skeleton
                colorScheme={"orange"}
                isLoaded={
                  !dropper.contractState.isLoading &&
                  !dropper.transferOwnership.isLoading
                }
              >
                <EditablePreview w="100%" px={2} />
                <EditableInput w="100%" px={2} />
              </Skeleton>
            </Editable>
          </code>
          <code>
            <Flex>
              {dropper.contractState.data?.paused ? "Paused" : "Running"}
            </Flex>
          </code>
          <code>Number of claims: {dropper.contractState.data?.numClaims}</code>
        </Flex>
      </Flex>

      <Paginator
        paginatorKey={"adminClaims"}
        setPage={pageOptions.setPage}
        setLimit={pageOptions.setPageSize}
        hasMore={adminClaims?.data?.length == pageOptions.pageSize}
      >
        {adminClaims.isLoading && <Spinner />}
        {web3ctx.account &&
          adminClaims?.data?.map((claim: ClaimInterface) => {
            return (
              <Claim
                dropperAddress={contractAddress}
                key={`contract-card-${claim.id}}`}
                claimId={claim.id}
                claimIdx={claim.drop_number}
              />
            );
          })}
      </Paginator>
      {children}
    </Flex>
  );
};

export default Dropper;
