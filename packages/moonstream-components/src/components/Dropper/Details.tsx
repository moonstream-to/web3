import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Spinner,
  VStack,
  Stack,
  Input,
  Box,
  Button,
  Heading,
  useDisclosure,
  InputGroup,
  ScaleFade,
} from "@chakra-ui/react";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
import useDrop from "../../core/hooks/dropper/useDrop";
import Paginator from "../Paginator";
import ClaimantDetails from "../ClaimantDetails";
import ClaimersList from "../ClaimersList";

const _Drop = ({ dropId, ...props }: { dropId: string }) => {
  const web3ctx = useContext(Web3Context);

  const {
    claimants,
    deleteClaimants,
    setClaimantsPage,
    claimantsPage,
    setClaimantsPageSize,
    claimantsPageSize,
  } = useDrop({
    targetChain,
    ctx: web3ctx,
    claimId: dropId,
  });

  const { onOpen, onClose, isOpen } = useDisclosure();
  const [filter, setFilter] = React.useState("");


  return (
    <Flex
      borderRadius={"md"}
      bgColor="blue.800"
      w="100%"
      direction={"column"}
      p={4}
      mt={2}
      textColor={"gray.300"}
      {...props}
    >
      <Flex bgColor={"blue.1200"} borderRadius="md" p={2} direction="column">
        <Box>
          {/* <ScaleFade in> */}
          <Heading variant="tokensScreen"> Claimants </Heading>
          <VStack
            overflow="initial"
            maxH="unset"
            height="100%"
            w="100%"
            maxW="100%"
          >
            {!isOpen && (
              <>
                <Stack direction={["column", "row", null]} w="100%">
                  {" "}
                  <InputGroup size="sm" variant="outline" w="100%">
                    <Input
                      type="search"
                      maxW="800px"
                      flexBasis="50px"
                      flexGrow={1}
                      display="flex"
                      minW="150px"
                      w="unset"
                      borderRadius="md"
                      placeholder="Check if address is on the list"
                      value={filter}
                      onChange={(e) => setFilter(e.target.value)}
                    />
                  </InputGroup>
                  <Button
                    alignSelf="flex-end"
                    onClick={onOpen}
                    colorScheme="orange"
                    variant="solid"
                    px="2rem"
                    size="sm"
                  >
                    Check now
                  </Button>
                </Stack>
              </>
            )}
            {isOpen && (
              <ScaleFade in>
                <ClaimantDetails
                  onClose={onClose}
                  address={filter}
                  claimId={dropId}
                  onDeleteClaimant={(address: string) => {
                    deleteClaimants.mutate({ list: [address] });
                  }}
                />
              </ScaleFade>
            )}

            <Paginator
              paginatorKey={"claimants"}
              setPage={setClaimantsPage}
              setLimit={setClaimantsPageSize}
              hasMore={
                claimants.data?.length == claimantsPageSize ? true : false
              }
              page={claimantsPage}
              pageSize={claimantsPageSize}
            >
              {!claimants.isLoading && (
                <ClaimersList
                  data={claimants.data}
                  onDeleteClaimant={deleteClaimants}
                />
              )}
              {claimants.isLoading && <Spinner />}
            </Paginator>
          </VStack>
        </Box>
      </Flex>
    </Flex>
  );
};

const Drop = chakra(_Drop);

export default Drop;
