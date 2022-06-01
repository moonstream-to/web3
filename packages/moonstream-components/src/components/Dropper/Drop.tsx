import React, { useContext, useState } from "react";
import {
  chakra,
  Flex,
  Button,
  Link,
  IconButton,
  useDisclosure,
  Stack,
  ButtonGroup,
  EditablePreview,
  EditableInput,
  Editable,
  Skeleton,
  EditableTextarea,
  useEditableControls,
} from "@chakra-ui/react";
import Papa from "papaparse";
import FileUpload from "../FileUpload";
import { useRouter } from "../../core/hooks";
import { useClaim, useDrop } from "../../core/hooks/dropper";
import { CheckIcon, CloseIcon } from "@chakra-ui/icons";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
import { useToast } from "../../core/hooks";
import { UpdateClaim } from "../../../../../types/Moonstream";
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
    claimId: dropId,
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

  const { onClose, isOpen } = useDisclosure();

  React.useEffect(() => {
    if (isOpen && update.isSuccess) {
      onClose();
      update.reset();
    }
  }, [isOpen, update, onClose]);

  const onSubmit = (data: updateClaim) =>
    update.mutate(
      { ...data },
      {
        onSuccess: () => {
          claim.refetch();
        },
      }
    );

  function EditableControls() {
    const { isEditing, getSubmitButtonProps, getCancelButtonProps } =
      useEditableControls();

    return isEditing ? (
      <ButtonGroup justifyContent="end" size="sm" w="full" spacing={2} mt={2}>
        <IconButton
          aria-label="Confirm"
          colorScheme={"green"}
          icon={<CheckIcon />}
          {...getSubmitButtonProps()}
        />
        <IconButton
          aria-label="Cancel"
          colorScheme={"red"}
          icon={<CloseIcon boxSize={3} />}
          {...getCancelButtonProps()}
        />
      </ButtonGroup>
    ) : (
      <></>
    );
  }

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
      <Skeleton colorScheme={"orange"} isLoaded={!claim.isLoading}>
        <Editable
          my={2}
          submitOnBlur={false}
          selectAllOnFocus={true}
          bgColor={"blue.700"}
          size="lg"
          fontSize={"lg"}
          fontWeight="600"
          textColor="gray.500"
          w="100%"
          minW={["280px", "300px", "360px", "420px", null]}
          variant={"outline"}
          placeholder={claim.data?.title}
          defaultValue={claim.data?.title}
          isDisabled={claim.isLoading}
          onSubmit={(nextValue) => {
            onSubmit({ title: nextValue });
          }}
        >
          <EditablePreview w="100%" px={2} />
          <EditableInput w="100%" px={2} />
        </Editable>
      </Skeleton>
      <Skeleton colorScheme={"orange"} isLoaded={!claim.isLoading}>
        <Editable
          my={2}
          p={2}
          // selectAllOnFocus={true}
          submitOnBlur={false}
          // isPreviewFocusable={false}
          // onEdit={() => {
          //   setIsEditing(true);
          // }}
          // onBlur={() => setIsEditing(false)}
          bgColor={"blue.800"}
          size="lg"
          fontSize={"lg"}
          textColor="gray.500"
          w="100%"
          minW={["280px", "300px", "360px", "420px", null]}
          variant={"outline"}
          placeholder={claim.data?.description}
          defaultValue={claim.data?.description}
          isDisabled={claim.isLoading}
          onSubmit={(nextValue) => {
            onSubmit({ description: nextValue });
          }}
        >
          <EditablePreview
            w="100%"
            h="fit-content"
            maxH="unset"
            whiteSpace={"break-spaces"}
            px={2}
          />
          <EditableTextarea w="100%" px={2}></EditableTextarea>
          <EditableControls
          // isEditing={isEditing}
          // key={isEditing ? `sadadadediting` : `asdadahidden`}
          />
        </Editable>
      </Skeleton>
      <Flex w="100%" direction={["row", null]} flexWrap="wrap">
        <Flex
          direction={"row"}
          flexGrow={1}
          flexBasis={"200px"}
          wordBreak="break-word"
        >
          <Stack direction={"column"} py={4} w="100%">
            <code key={`terminus-address`}>
              Terminus address:
              <Skeleton colorScheme={"orange"} isLoaded={!claim.isLoading}>
                <Editable
                  submitOnBlur={false}
                  selectAllOnFocus={true}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={claim.data?.terminus_address}
                  defaultValue={claim.data?.terminus_address}
                  isDisabled={claim.isLoading}
                  onSubmit={(nextValue) => {
                    onSubmit({ terminus_address: nextValue });
                  }}
                >
                  <EditablePreview w="100%" px={2} />
                  <EditableInput w="100%" px={2} />
                </Editable>
              </Skeleton>
            </code>
            <code key={`terminus-pool-id`}>
              Terminus Pool Id:
              <Skeleton colorScheme={"orange"} isLoaded={!claim.isLoading}>
                <Editable
                  submitOnBlur={false}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={claim.data?.terminus_pool_id}
                  defaultValue={claim.data?.terminus_pool_id}
                  isDisabled={claim.isLoading}
                  onSubmit={(nextValue) => {
                    onSubmit({ terminus_pool_id: nextValue });
                  }}
                >
                  <EditablePreview w="100%" px={2} />
                  <EditableInput w="100%" px={2} />
                </Editable>
              </Skeleton>
              {/* <Input
                      defaultValue={claim.data?.terminus_address}
                      placeholder={
                        "Terminus contract address that manages access tokens"
                      }
                    ></Input> */}
            </code>
            <code key={`deadline`}>
              Deadline:
              <Skeleton colorScheme={"orange"} isLoaded={!claim.isLoading}>
                <Editable
                  submitOnBlur={false}
                  bgColor={"blue.700"}
                  size="sm"
                  fontSize={"sm"}
                  textColor="gray.500"
                  w="100%"
                  minW={["280px", "300px", "360px", "420px", null]}
                  variant={"outline"}
                  placeholder={claim.data?.claim_block_deadline}
                  defaultValue={claim.data?.claim_block_deadline}
                  isDisabled={claim.isLoading}
                  onSubmit={(nextValue) => {
                    onSubmit({ claim_block_deadline: nextValue });
                  }}
                >
                  <EditablePreview w="100%" px={2} />
                  <EditableInput w="100%" px={2} />
                </Editable>
              </Skeleton>
              {/* <Input
                      defaultValue={claim.data?.terminus_address}
                      placeholder={
                        "Terminus contract address that manages access tokens"
                      }
                    ></Input> */}
            </code>
          </Stack>
          {/* </Flex> */}
        </Flex>
        <Flex flexGrow={1} h="auto" flexBasis={"220px"} placeSelf="center">
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
