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
import OverlayContext from "../../core/providers/OverlayProvider/context";
import { MODAL_TYPES } from "../../core/providers/OverlayProvider/constants";
import { useDrop, useRouter } from "../../core/hooks";
import { EditIcon } from "@chakra-ui/icons";
import FocusLock from "react-focus-lock";
import { useForm } from "react-hook-form";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";

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
  children,
  ...props
}: {
  claim: ClaimInterface;
  children: React.ReactNode;
}) => {
  const router = useRouter();
  const overlay = useContext(OverlayContext);
  const web3ctx = useContext(Web3Context);

  const { register, handleSubmit } = useForm();

  const { update } = useDrop({ targetChain, ctx: web3ctx, claimId: claim.id });

  const query = router.query;

  const onDrop = (file: any) => {
    Papa.parse(file[0], {
      header: true,
      skipEmptyLines: true,
      complete: (result: any) => {
        overlay.toggleModal({
          type: MODAL_TYPES.CSV_DIFF,
          props: { newValue: result.data, dropId: claim.id },
        });
      },
      error: (err: Error) => console.log("acceptedFiles csv:", err.message),
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

  const onSubmit = (data: any) => update.mutate({ ...data });

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
                      name="title"
                      ref={register({ required: "title is required!" })}
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
                      name="description"
                      ref={register({ required: "description is required!" })}
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
                      <NumberInputField
                        px={2}
                        name="deadline"
                        ref={register({ required: "deadline is required!" })}
                      />
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
        >
          Activate
        </Button>
        <Button
          variant={"outline"}
          colorScheme="red"
          isDisabled={!claim.active}
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
