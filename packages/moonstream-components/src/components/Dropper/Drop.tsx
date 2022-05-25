import React, { useContext, useState } from "react";
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
import { useRouter } from "../../core/hooks";
import { useClaim, useDrop } from "../../core/hooks/dropper";
import { EditIcon } from "@chakra-ui/icons";
import FocusLock from "react-focus-lock";
import { useForm } from "react-hook-form";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
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

const _DropCard = ({
  dropId,
  children,
  ...props
}: {
  initalClaim: ClaimInterface;
  dropId: string;
  children: React.ReactNode;
}) => {
  const router = useRouter();
  const toast = useToast();
  const { register, handleSubmit } = useForm();

  const web3ctx = useContext(Web3Context);
  const { claim } = useClaim({
    targetChain,
    ctx: web3ctx,
    claimId: dropId,
  });

  const query = router.query;

  const [isUploading, setIsUploading] = useState(false);

  var parserLineNumber = 0;

  const { update, uploadFile, activateDrop, deactivateDrop } = useDrop({
    targetChain: targetChain,
    ctx: web3ctx,
  });

  const handleParsingError = function (error: string): void {
    setIsUploading(false);
    toast(error, "error", "CSV Parse Error");
    throw error;
  };

  const validateHeader = function (
    headerValue: string,
    column: number
  ): string {
    const header = headerValue.trim().toLowerCase();
    if (column == 0 && header != "address") {
      handleParsingError("First column header must be 'address'.");
    }
    if (column == 1 && header != "amount") {
      handleParsingError("Second column header must be 'amount'");
    }
    return header;
  };

  const validateCellValue = function (cellValue: string, column: any): string {
    const value = cellValue.trim();
    if (column == "address") {
      parserLineNumber++;
      try {
        web3ctx.web3.utils.toChecksumAddress(value);
      } catch (error) {
        handleParsingError(
          `Error parsing value '${value}' on line ${parserLineNumber}. Value in 'address' column must be a valid address.`
        );
      }
    }
    if (column == "amount") {
      const numVal = parseInt(value);
      if (isNaN(numVal) || numVal < 0) {
        handleParsingError(
          `Error parsing value: '${value}' on line ${parserLineNumber}. Value in 'amount' column must be an integer.`
        );
      }
    }
    return value;
  };

  const onDrop = (file: any) => {
    parserLineNumber = 0;
    setIsUploading(true);
    Papa.parse(file[0], {
      header: true,
      skipEmptyLines: true,
      fastMode: true,
      transform: validateCellValue,
      transformHeader: validateHeader,
      complete: (result: any) => {
        uploadFile.mutate(
          {
            dropperClaimId: claim.data?.id,
            claimants: result.data,
          },
          {
            onSettled: () => {
              setIsUploading(false);
            },
          }
        );
      },
      error: (err: Error) => handleParsingError(err.message),
    });
  };

  const { onOpen, onClose, isOpen } = useDisclosure();

  React.useEffect(() => {
    if (isOpen && update.isSuccess) {
      onClose();
      update.reset();
    }
  }, [isOpen, update, onClose]);
  const firstFieldRef = React.useRef(null);

  const onSubmit = (data: any) =>
    update.mutate(
      { dropperClaimId: claim.data?.id, ...data },
      {
        onSuccess: () => {
          claim.refetch();
        },
      }
    );


  // if (true) return <Spinner />;
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
              {claim.data?.title}
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
                      defaultValue={claim.data?.title}
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
                      defaultValue={claim.data?.description}
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
                      defaultValue={claim.data?.claim_block_deadline}
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
                      isLoading={update.isLoading}
                    >
                      Cancel
                    </Button>
                    <Button
                      colorScheme="orange"
                      type="submit"
                      isLoading={update.isLoading}
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
        {claim.data?.description}
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
                {claim.data?.claim_block_deadline}
              </ListItem>
              <ListItem>
                Enabled: {claim.data?.active ? "True" : "False"}
              </ListItem>
              <ListItem>
                Dropper: <code>{claim.data?.dropper_contract_address}</code>
              </ListItem>
              <ListItem>
                Terminus: <code>{claim.data?.terminus_address}</code>
              </ListItem>
              <ListItem>Pool id: {claim.data?.terminus_pool_id}</ListItem>
            </UnorderedList>
          </Flex>
        </Flex>
        <Flex flexGrow={1} h="auto" flexBasis={"220px"}>
          <FileUpload
            onDrop={onDrop}
            alignSelf="center"
            // as={Flex}
            minW="220px"
            isUploading={isUploading}
          />
        </Flex>
      </Flex>
      <Flex direction={"row"} justifyContent="space-evenly" pt={4}>
        <Button
          variant={"outline"}
          colorScheme="green"
          isDisabled={!!claim.data?.active}
          isLoading={activateDrop.isLoading}
          onClick={() =>
            activateDrop.mutate(
              { dropperClaimId: dropId },
              {
                onSuccess: () => {
                  claim.refetch();
                },
              }
            )
          }
        >
          Activate
        </Button>
        <Button
          variant={"outline"}
          colorScheme="red"
          isDisabled={!claim.data?.active}
          isLoading={deactivateDrop.isLoading}
          onClick={() =>
            deactivateDrop.mutate(
              { dropperClaimId: dropId },
              {
                onSuccess: () => {
                  claim.refetch();
                },
              }
            )
          }
        >
          Deactivate
        </Button>
        <Button
          as={Link}
          colorScheme={"orange"}
          variant="outline"
          onClick={() => {
            if (query?.dropId) {
              router.push({
                pathname: "/drops",
              });
            } else {
              router.push({
                pathname: "drops/details",
                query: {
                  dropId: claim.data?.id,
                },
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

const DropCard = chakra(_DropCard);

export default DropCard;
