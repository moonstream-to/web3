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
  Heading,
  Box,
  Badge,
} from "@chakra-ui/react";
import Papa from "papaparse";
import FileUpload from "../FileUpload";
import { useRouter } from "../../core/hooks";
import {
  useClaim,
  useDrop,
  useDropperContract,
} from "../../core/hooks/dropper";
import { CheckIcon, CloseIcon } from "@chakra-ui/icons";
import Web3Context from "../../core/providers/Web3Provider/context";
import { useToast } from "../../core/hooks";
import { UpdateClaim } from "../../../../../types/Moonstream";
import Metadata from "../Metadata";
import dynamic from "next/dynamic";
const ReactJson = dynamic(() => import("react-json-view"), {
  ssr: false,
});
const _Claim = ({
  isActive,
  claimId,
  claimIdx,
  children,
  deadline,
  dropNumber,
  dropperAddress,
  ...props
}: {
  isActive: boolean;
  dropperAddress: string;
  claimIdx: number;
  deadline?: string;
  dropNumber?: string;
  claimId: string;
  children?: React.ReactNode;
}) => {
  const router = useRouter();
  const toast = useToast();

  const web3ctx = useContext(Web3Context);
  const { claim } = useClaim({
    ctx: web3ctx,
    claimId: claimId,
    dropperAddress: dropperAddress,
  });

  const { claimState, setClaimSigner, setClaimURI, claimUri } =
    useDropperContract({
      dropperAddress,
      ctx: web3ctx,
      claimId: claimIdx.toString(),
    });

  const query = router.query;

  const [isUploading, setIsUploading] = useState(false);

  var parserLineNumber = 0;

  const { update, uploadFile, activateDrop, deactivateDrop } = useDrop({
    ctx: web3ctx,
    claimId: claimId,
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

  const onSubmit = (data: UpdateClaim) =>
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

  console.log("tt,", claimState.data);

  return (
    <Flex
      direction={"column"}
      // bgColor="blue.1000"
      flexWrap={"wrap"}
      // pt={4}
      px={0}
      w="100%"
      {...props}
      boxShadow={"md"}
      borderRadius="md"
      border={"4px solid #373E9B"}
      boxSizing="content-box"
    >
      <Metadata
        // borderColor={"blue.1200"}
        w="315px"
        metadata={claimUri.data}
      >
        <Box
          // fontSize={"12px"}
          fontWeight={"600"}
          borderRadius="xl"
          p={2}
          // bgColor="#454545"
          textColor={isActive ? "green.900" : "inherit"}
          w="auto"
          position={"absolute"}
          top={2}
          left={5}
        >
          {isActive ? "Active" : "Not active"}
        </Box>
        <Box
          fontSize={"12px"}
          borderRadius="xl"
          p={2}
          bgColor="#454545"
          w="auto"
          position={"absolute"}
          bottom={5}
          right={5}
        >
          {claimState.data?.claim[0] == "20" && "ERC 20"}
          {claimState.data?.claim[0] == "1" && "Terminus"}
        </Box>
        <Box
          fontSize={"12px"}
          borderRadius="xl"
          p={2}
          bgColor="#454545"
          w="auto"
          position={"absolute"}
          bottom={5}
          left={5}
        >
          Polygon
        </Box>
      </Metadata>
      <Flex mx={4} direction="column">
        <Box my={8} fontSize="sm" p={2} bgColor={"blue.1400"} borderRadius="md">
          Deadline: {deadline} <br />
          Drop number: {dropNumber} <br />
        </Box>
        <Button w="100%" colorScheme={"green"}>
          Manage
        </Button>
      </Flex>
    </Flex>
  );
};

const DropCard = chakra(_Claim);

export default DropCard;

{
  /* <Stack direction={"column"} py={4} w="70%" flexGrow={1} px={[0, 4]}>
  <Skeleton colorScheme={"orange"} isLoaded={!claim.isLoading}>
    <Editable
      my={2}
      p={2}
      submitOnBlur={false}
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
      <EditableControls />
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
        <code
          key={`terminus-address-${claim.data?.terminus_address}`}
        >
          Terminus address:
          <Skeleton
            colorScheme={"orange"}
            isLoaded={!claim.isLoading}
          >
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
        <code key={`terminusPoolId-${claim.data?.terminus_pool_id}`}>
          Terminus Pool Id:
          <Skeleton
            colorScheme={"orange"}
            isLoaded={!claim.isLoading}
          >
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
        </code>
        <code
          key={`claimDeadline-${claim.data?.claim_block_deadline}`}
        >
          Deadline:
          <Skeleton
            colorScheme={"orange"}
            isLoaded={!claim.isLoading}
          >
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
        </code>
        <code key={`claimUri-${claimState.data?.claimUri}`}>
          URI:
          <Skeleton
            colorScheme={"orange"}
            isLoaded={!claimState.isLoading && !setClaimURI.isLoading}
          >
            <Editable
              submitOnBlur={false}
              bgColor={"blue.700"}
              size="sm"
              fontSize={"sm"}
              textColor="gray.500"
              w="100%"
              minW={["280px", "300px", "360px", "420px", null]}
              variant={"outline"}
              placeholder={"claim uri"}
              defaultValue={claimState.data?.claimUri}
              onSubmit={(nextValue) => {
                setClaimURI.mutate(
                  { uri: nextValue },
                  {
                    onSettled: () => {
                      setClaimURI.reset();
                    },
                  }
                );
              }}
            >
              <EditablePreview w="100%" px={2} cursor={"text"} />
              <EditableInput wordBreak={"keep-all"} w="100%" px={2} />
            </Editable>
          </Skeleton>
        </code>

        <code key={`signer-${claimState.data?.signer}`}>
          Signer:
          <Skeleton
            colorScheme={"orange"}
            isLoaded={
              !claimState.isLoading && !setClaimSigner.isLoading
            }
          >
            <Editable
              submitOnBlur={false}
              bgColor={"blue.700"}
              size="sm"
              fontSize={"sm"}
              textColor="gray.500"
              w="100%"
              minW={["280px", "300px", "360px", "420px", null]}
              variant={"outline"}
              selectAllOnFocus={true}
              placeholder={claimState.data?.signer ?? "claim signer"}
              defaultValue={claimState.data?.signer}
              onSubmit={(nextValue) => {
                setClaimSigner.mutate(
                  { signer: nextValue },
                  {
                    onSettled: () => {
                      setClaimSigner.reset();
                    },
                  }
                );
              }}
            >
              <EditablePreview w="100%" px={2} cursor={"text"} />
              <EditableInput wordBreak={"keep-all"} w="100%" px={2} />
            </Editable>
          </Skeleton>
        </code>
        <Skeleton isLoaded={!claimUri.isLoading}>
          {claimUri?.data && (
            <Box cursor="crosshair" overflowWrap={"break-word"}>
              <ReactJson
                name="metadata"
                collapsed
                style={{
                  cursor: "text",
                  lineBreak: "anywhere",
                }}
                src={claimUri?.data}
                theme="harmonic"
                displayDataTypes={false}
                displayObjectSize={false}
                collapseStringsAfterLength={128}
              />
            </Box>
          )}
        </Skeleton>
      </Stack>
    </Flex>
    <Flex
      flexGrow={1}
      h="auto"
      flexBasis={"220px"}
      placeSelf="center"
    >
      <FileUpload
        onDrop={onDrop}
        alignSelf="center"
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
          { dropperClaimId: claimId },
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
          { dropperClaimId: claimId },
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
            pathname: "dropper/claims/details",
            query: {
              claimId: claimId,
              contractAddress: dropperAddress,
              claimIdx: claimIdx,
            },
          });
        }
      }}
    >
      {query?.dropId ? `Back to list` : `See whitelist`}
    </Button>
  </Flex>
</Stack> */
}
