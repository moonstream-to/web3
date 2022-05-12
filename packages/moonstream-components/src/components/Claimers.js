import React, { useState, useEffect } from "react";
import ClaimersList from "./ClaimersList";
import {
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
import Paginator from "./Paginator";
import ClaimantDetails from "./ClaimantDetails";
import { useRouter } from "../core/hooks";

const Claimers = ({ list, onDeleteClaimant, setPage, setLimit, hasMore }) => {
  const { onOpen, onClose, isOpen } = useDisclosure();
  const [filter, setFilter] = useState("");

  const router = useRouter();
  const { dropId } = router.query;

  useEffect(() => {
    document.title = `Tokens`;
  }, []);

  const handleChange = (event) => setFilter(event.target.value);
  return (
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
                  onChange={handleChange}
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
              dropId={dropId}
              onDeleteClaimant={onDeleteClaimant}
            />
          </ScaleFade>
        )}

        <Paginator
          onBack={() => setPage((_currentPage) => _currentPage - 1)}
          onForward={() => setPage((_currentPage) => _currentPage + 1)}
          paginatorKey={"claimants"}
          setLimit={setLimit}
          hasMore={hasMore}
        >
          <ClaimersList data={list} onDeleteClaimant={onDeleteClaimant} />
        </Paginator>
      </VStack>
      {/* </ScaleFade> */}
    </Box>
  );
};

export default Claimers;
