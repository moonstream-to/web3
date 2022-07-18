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
  Stack,
  Select,
  Button,
  Spacer,
} from "@chakra-ui/react";
import Claim from "./Claim";
import Web3Context from "../../core/providers/Web3Provider/context";
import Paginator from "../Paginator";
import { ClaimInterface } from "../../../../../types/Moonstream";
import { useDropperContract, useDrops } from "../../core/hooks/dropper";
import { useRouter } from "../../core/hooks";
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
  const router = useRouter();
  const dropper = useDropperContract({
    dropperAddress: contractAddress,
    ctx: web3ctx,
  });

  const { adminClaims, pageOptions, dropperContracts } = useDrops({
    dropperAddress: contractAddress,
    ctx: web3ctx,
  });
  const { contractState } = useDropperContract({
    dropperAddress: contractAddress,
    ctx: web3ctx,
  });

  if (!contractAddress)
    return <Text>{"Please specify terminus address "}</Text>;
  if (
    dropper.contractState.isLoading ||
    !dropper.contractState.data ||
    dropperContracts.isLoading ||
    contractState.isLoading
  )
    return <Spinner />;

  console.log("contractState", contractState.data);

  return (
    <Flex
      w="100%"
      minH="100vh"
      direction={"column"}
      id="flexid"
      alignSelf={"center"}
      {...props}
    >
      <Flex mt={14} direction="column">
        <Heading>
          <Editable
            submitOnBlur={false}
            // bgColor={"blue.700"}
            size="sm"
            fontSize={"xl"}
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
        <Stack direction={"row"} flexWrap={"wrap"} spacing={8} mt={8}>
          {/* <code key={"PoolController"}>
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
          </code> */}
          {/* <code>
            <Flex>
              {dropper.contractState.data?.paused ? "Paused" : "Running"}
            </Flex>
          </code> */}
          <code>
            <b>Address:</b> {contractAddress}
          </code>
          <code>
            <b>NUMBER OF CLAIMS:</b> {dropper.contractState.data?.numClaims}
          </code>
        </Stack>
      </Flex>
      <Flex id="Drops Navbar" alignItems={"center"} justifyItems="flex-end">
        <Spacer />
        <Select
          size="sm"
          maxW="75px"
          mr={2}
          placeholder="Select page size"
          onChange={(e) => {
            router.appendQuery(`adminClaimsLimit`, e.target.value);
          }}
          value={router.query[`adminClaimsLimit`] ?? "25"}
          bgColor="blue.900"
          borderRadius={"md"}
        >
          {["25", "50", "100", "300", "500"].map((pageSize) => {
            return (
              <option
                key={`paginator-options-pagesize-${pageSize}`}
                value={pageSize}
              >
                {pageSize}
              </option>
            );
          })}
        </Select>{" "}
        per page
        <Button variant={"solid"} ml={24} colorScheme="orange" size="sm">
          + Add new drop
        </Button>
      </Flex>

      <Paginator
        hideSelect={true}
        paginatorKey={"adminClaims"}
        direction="row"
        spacing="4px"
        totalItems={contractState.data?.numClaims}
        w="100%"
        setPage={pageOptions.setPage}
        setLimit={pageOptions.setPageSize}
        hasMore={adminClaims?.data?.length == pageOptions.pageSize}
        mb={20}
      >
        {adminClaims.isLoading && <Spinner />}
        {web3ctx.account &&
          adminClaims?.data?.map((claim: ClaimInterface) => {
            return (
              <>
                <Claim
                  isActive={claim.active}
                  deadline={claim.claim_block_deadline.toString()}
                  dropNumber={claim.claim_id.toString()}
                  w="315px"
                  m={"20px"}
                  dropperAddress={contractAddress}
                  key={`contract-card-${claim.id}}`}
                  claimId={claim.id}
                  claimIdx={claim.claim_id}
                ></Claim>
              </>
            );
          })}
      </Paginator>
      {children}
    </Flex>
  );
};

export default Dropper;
