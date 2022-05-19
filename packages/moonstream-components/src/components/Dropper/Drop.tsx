import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Heading,
  ListItem,
  UnorderedList,
  Button,
  Link,
  IconButton,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
  PopoverCloseButton,
  useDisclosure,
  Stack,
  FormControl,
  FormLabel,
  Input,
  ButtonGroup,
  PopoverAnchor,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from "@chakra-ui/react";
import Papa from "papaparse";
import FileUpload from "../FileUpload";
import { useDrops, useRouter } from "../../core/hooks";
import { EditIcon } from "@chakra-ui/icons";
import FocusLock from "react-focus-lock";
import { useForm } from "react-hook-form";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
import { UseMutationResult } from "react-query";
import { updateDropArguments } from "../../../../../types/Moonstream";
import { useToast } from "../../core/hooks";

interface ClaimInterface {
  active: boolean;
  claim_block_deadline: number;
  claim_id: number;
  description: string;
  dropper_contract_address: string;
  id: string;
  terminus_address: string;
  terminus_pool_id: number;
  title: string;
}

const DropCard = ({
  claim,
  onUpdate,
  activateDrop,
  deactivateDrop,
  children,
  ...props
}: {
  claim: ClaimInterface;
  activateDrop: UseMutationResult<unknown, unknown, string, unknown>;
  deactivateDrop: UseMutationResult<unknown, unknown, string, unknown>;
  onUpdate: UseMutationResult<
    unknown,
    unknown,
    {
      id: string;
      data: updateDropArguments;
    },
    unknown
  >;
  children: React.ReactNode;
}) => {
  const router = useRouter();
  const web3ctx = useContext(Web3Context);
  const toast = useToast();
  const { register, handleSubmit } = useForm();

  const { uploadFile } = useDrops({ targetChain, ctx: web3ctx });
  const query = router.query;

  const handleParsingError = function (error: string): void {
    toast(error, "error", "CSV Parse Error");
    throw error;
  };

  const validateHeader = function (
    headerValue: string,
    column: number
  ): string {
    const header = headerValue.trim().toLowerCase();
    if (column == 0 && header != "address") {
      handleParsingError("First column hedaer must be 'address'.");
    }
    if (column == 1 && header != "amount") {
      handleParsingError("Second column header must be 'amount'");
    }
    return header;
  };

  const validateCellValue = function (cellValue: string, column: any): string {
    const value = cellValue.trim();
    if (column == "address") {
      try {
        web3ctx.web3.utils.toChecksumAddress(value);
      } catch (error) {
        handleParsingError(
          `Error parsing value: ${value}. Value in 'address' column must be a valid address.`
        );
      }
    }
    if (column == "amount") {
      if (isNaN(parseInt(value))) {
        handleParsingError(
          `Error parsing value: ${value}. Value in 'amount' column must be an integer.`
        );
      }
    }
    return value;
  };

  const onDrop = (file: any) => {
    Papa.parse(file[0], {
      header: true,
      skipEmptyLines: true,
      fastMode: true,
      transform: validateCellValue,
      transformHeader: validateHeader,
      complete: (result: any) => {
        uploadFile.mutate({
          dropperClaimId: claim.id,
          claimants: result.data,
        });
      },
      error: (err: Error) => handleParsingError(err.message),
    });
  };

  const { onOpen, onClose, isOpen } = useDisclosure();

  React.useEffect(() => {
    if (isOpen && onUpdate.isSuccess) {
      onClose();
      onUpdate.reset();
    }
  }, [isOpen, onUpdate, onClose]);
  const firstFieldRef = React.useRef(null);

  const onSubmit = (data: any) =>
    onUpdate.mutate({ id: claim.id, data: { ...data } });

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
      <Popover
        isOpen={isOpen}
        initialFocusRef={firstFieldRef}
        onOpen={onOpen}
        onClose={onClose}
        placement="bottom"
        closeOnBlur={false}
      >
        <Flex dir="row" borderBottomWidth={1} p={0}>
          <PopoverAnchor>
            <Heading as={"h2"} fontSize="lg" w="90%" mt={2}>
              {"Drop: "}
              {claim.title}
            </Heading>
          </PopoverAnchor>

          <PopoverTrigger>
            <IconButton
              mt={2}
              aria-label="edit"
              colorScheme="orange"
              variant={"ghost"}
              size="sm"
              icon={<EditIcon />}
              display="inline"
              float="right"
            />
          </PopoverTrigger>
          <PopoverContent
            p={5}
            bgColor="blue.1000"
            boxShadow={"lg"}
            minW="300px"
          >
            <FocusLock returnFocus persistentFocus={false}>
              <PopoverArrow />
              <PopoverCloseButton />
              <form onSubmit={handleSubmit(onSubmit)}>
                <Stack spacing={4}>
                  <FormControl>
                    <FormLabel htmlFor={"title"}>{"Title"}</FormLabel>
                    <Input
                      px={2}
                      variant={"flushed"}
                      colorScheme="orange"
                      defaultValue={claim.title}
                      {...register("title")}
                    />
                  </FormControl>
                  <FormControl>
                    <FormLabel htmlFor={"description"}>
                      {"Description"}
                    </FormLabel>
                    <Input
                      px={2}
                      variant={"flushed"}
                      colorScheme="orange"
                      defaultValue={claim.description}
                      {...register("description")}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel htmlFor={"deadline"}>
                      {"Block deadline"}
                    </FormLabel>
                    <NumberInput
                      variant={"flushed"}
                      name="deadline"
                      colorScheme="orange"
                      defaultValue={claim.claim_block_deadline}
                    >
                      <NumberInputField px={2} {...register("deadline")} />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>

                  <ButtonGroup d="flex" justifyContent="flex-end">
                    <Button
                      variant="outline"
                      onClick={onClose}
                      isLoading={onUpdate.isLoading}
                    >
                      Cancel
                    </Button>
                    <Button
                      colorScheme="orange"
                      type="submit"
                      isLoading={onUpdate.isLoading}
                    >
                      Save
                    </Button>
                  </ButtonGroup>
                </Stack>
              </form>
            </FocusLock>
          </PopoverContent>
        </Flex>
      </Popover>
      <Heading as={"h3"} fontSize="md">
        {claim.description}
      </Heading>
      <Flex w="100%" direction={["row", null]} flexWrap="wrap">
        <Flex
          direction={"row"}
          flexGrow={1}
          flexBasis={"200px"}
          wordBreak="break-word"
        >
          <Flex
            mt={2}
            direction={"row"}
            minW="200px"
            flexWrap={"wrap"}
            w="100%"
            bgColor={"blue.1100"}
            borderRadius="md"
            px={2}
            // pt={4}
          >
            <UnorderedList fontSize={"sm"}>
              <ListItem>
                Deadline: &#9;&#9;&#9;&#9;&#9;&#9;&#9;
                {claim.claim_block_deadline}
              </ListItem>
              <ListItem>Enabled: {claim.active ? "True" : "False"}</ListItem>
              <ListItem>
                Dropper: <code>{claim.dropper_contract_address}</code>
              </ListItem>
              <ListItem>
                Terminus: <code>{claim.terminus_address}</code>
              </ListItem>
              <ListItem>Pool id: {claim.terminus_pool_id}</ListItem>
            </UnorderedList>
          </Flex>
        </Flex>
        <Flex flexGrow={1} h="auto" flexBasis={"220px"}>
          <FileUpload
            onDrop={onDrop}
            alignSelf="center"
            // as={Flex}
            minW="220px"
          />
        </Flex>
      </Flex>
      <Flex direction={"row"} justifyContent="space-evenly" pt={4}>
        <Button
          variant={"outline"}
          colorScheme="green"
          isDisabled={!!claim.active}
          onClick={() => activateDrop.mutate(claim.id)}
        >
          Activate
        </Button>
        <Button
          variant={"outline"}
          colorScheme="red"
          isDisabled={!claim.active}
          onClick={() => deactivateDrop.mutate(claim.id)}
        >
          Deactivate
        </Button>
        <Button
          as={Link}
          colorScheme={"orange"}
          variant="outline"
          // href={`/drops/details/`}
          onClick={() => {
            // router.appendQuery("dropId", claim.id);
            if (query?.dropId) {
              router.push({
                pathname: "/drops",
              });
            } else {
              router.push({
                pathname: "drops/details",
                query: { dropId: claim.id },
              });
            }
          }}
        >
          {query?.dropId ? `Back to list` : `See whitelist`}
        </Button>
      </Flex>
      {children && children}
    </Flex>
  );
};

export default chakra(DropCard);
