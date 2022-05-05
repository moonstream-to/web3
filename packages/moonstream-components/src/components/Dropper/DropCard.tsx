import React, { useContext } from "react";
import {
  chakra,
  Flex,
  Heading,
  ListItem,
  UnorderedList,
  Button,
} from "@chakra-ui/react";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
import useClaimAdmin from "../../core/hooks/useClaimAdmin";
import useClaimCard from "../../core/hooks/useClaimCard";
import Papa from "papaparse";
import FileUpload from "../FileUpload";
import ReactDiffViewer from "react-diff-viewer";

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

const ContractCard = ({ claim, ...props }: { claim: ClaimInterface }) => {
  const web3ctx = useContext(Web3Context);

  const { uploadFile } = useClaimAdmin({
    targetChain: targetChain,
    ctx: web3ctx,
  });

  const claimants = useClaimCard({
    targetChain,
    ctx: web3ctx,
    claimId: claim.id,
  });

  console.log(claimants?.data);

  const onDrop = (file: any) => {
    console.log("onDrop!,", file);
    console.log("Who is papa", Papa);
    Papa.parse(file[0], {
      header: true,
      skipEmptyLines: true,
      complete: (result: any) => {
        console.log("Complete: uploading file", claim.id, result.data);
        uploadFile.mutate({
          dropperClaimId: claim.id,
          claimants: result.data,
        });
      },
      error: (err: Error) => console.log("acceptedFiles csv:", err.message),
    });
  };

  // console.log("claimants", claimants.data.data.);
  let comparison = "";
  claimants.data?.data?.drops?.forEach(
    (dropItem: any) =>
      (comparison += dropItem.address + "," + dropItem.amount) + `\n`
  );
  console.log("claimants", comparison);
  return (
    <Flex
      borderRadius={"md"}
      bgColor="blue.800"
      w="100%"
      direction={"column"}
      p={4}
      mt={2}
      textColor={"gray.300"}
      // {...props}
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
        <Button colorScheme={"orange"} variant="outline">
          See whitelist
        </Button>
      </Flex>
      <ReactDiffViewer oldValue={comparison} newValue={""} splitView={true} />
    </Flex>
  );
};

export default chakra(ContractCard);
