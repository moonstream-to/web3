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
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  InputGroup,
} from "@chakra-ui/react";
import Paginator from "./Paginator";

const Claimers = ({ list, onDeleteClaimant, setPage, setLimit }) => {
  const { onOpen, onClose, isOpen } = useDisclosure();
  const [filter, setFilter] = useState("");

  useEffect(() => {
    document.title = `Tokens`;
  }, []);

  const handleChange = (event) => setFilter(event.target.value);
  return (
    <Box>
      {/* <ScaleFade in> */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg" trapFocus={false}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add claimant</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {/* <TokenRequest setNewToken={setNewToken} onClose={onClose} /> */}
          </ModalBody>
        </ModalContent>
      </Modal>
      <Heading variant="tokensScreen"> Claimants </Heading>
      <VStack overflow="initial" maxH="unset" height="100%" maxW="100%">
        <Stack direction={["column", "row", null]} w="100%">
          <InputGroup size="sm" variant="outline">
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
        <Paginator
          onBack={() => setPage((_currentPage) => _currentPage - 1)}
          onForward={() => setPage((_currentPage) => _currentPage + 1)}
          // currentPage={currentPage}
          // limit={limit}
          setLimit={setLimit}
        >
          <ClaimersList data={list} onDeleteClaimant={onDeleteClaimant} />
        </Paginator>
      </VStack>
      {/* </ScaleFade> */}
    </Box>
  );
};

export default Claimers;
