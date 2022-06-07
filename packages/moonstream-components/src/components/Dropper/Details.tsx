import React from "react";
import {
  chakra,
  Flex,
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
import ClaimantDetails from "../ClaimantDetails";
import ClaimersList from "../ClaimersList";
import Web3 from "web3";
import { useToast } from "../../core/hooks";

const _Drop = ({ dropId, ...props }: { dropId: string }) => {
  const { onOpen, onClose, isOpen } = useDisclosure();
  const [filter, setFilter] = React.useState("");
  const toast = useToast();
  const handleCheckNow = () => {
    const web3 = new Web3();
    if (web3.utils.isAddress(filter)) {
      onOpen();
    } else {
      toast("Not a valid address", "error");
    }
  };
  const handleKeypress = (e: any) => {
    //it triggers by pressing the enter key
    if (e.charCode === 13) {
      handleCheckNow();
    }
  };

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
                      onKeyPress={handleKeypress}
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
                    onClick={handleCheckNow}
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
                  onClose={() => {
                    setFilter("");
                    onClose();
                  }}
                  address={filter}
                  claimId={dropId}
                />
              </ScaleFade>
            )}
            <ClaimersList dropId={dropId} />
          </VStack>
        </Box>
      </Flex>
    </Flex>
  );
};

const Drop = chakra(_Drop);

export default Drop;
