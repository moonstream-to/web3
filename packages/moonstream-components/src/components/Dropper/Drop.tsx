import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Heading,
  ListItem,
  UnorderedList,
  Button,
  Link,
} from "@chakra-ui/react";
import Papa from "papaparse";
import FileUpload from "../FileUpload";
import OverlayContext from "../../core/providers/OverlayProvider/context";
import { MODAL_TYPES } from "../../core/providers/OverlayProvider/constants";
import { useRouter } from "../../core/hooks";

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

  const query = router.query;

  const onDrop = (file: any) => {
    console.log("onDrop!,", file);
    console.log("Who is papa", Papa);
    Papa.parse(file[0], {
      header: true,
      skipEmptyLines: true,
      complete: (result: any) => {
        console.log("Complete: uploading file", claim.id, result.data);
        overlay.toggleModal({
          type: MODAL_TYPES.CSV_DIFF,
          props: { newValue: result.data, dropId: claim.id },
        });
        // uploadFile.mutate({
        //   dropperClaimId: claim.id,
        //   claimants: result.data,
        // });
      },
      error: (err: Error) => console.log("acceptedFiles csv:", err.message),
    });
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
      <Heading as={"h2"} fontSize="lg" borderBottomWidth={1}>
        {"Claim: "}
        {claim.title}
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
            <UnorderedList>
              <ListItem>
                Deadline: &#9;&#9;&#9;&#9;&#9;&#9;&#9;
                {claim.claim_block_deadline}
              </ListItem>
              <ListItem>Description: {claim.description}</ListItem>
              <ListItem>Enabled: {claim.active ? "True" : "False"}</ListItem>
              <ListItem>
                Dropper address: {claim.dropper_contract_address}
              </ListItem>
              <ListItem>Terminus address: {claim.terminus_address}</ListItem>
              <ListItem>Terminus address: {claim.terminus_pool_id}</ListItem>
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
