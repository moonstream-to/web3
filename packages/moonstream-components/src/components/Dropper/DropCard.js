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
const ContractCard = ({ title, description, claimId, ...props }) => {
  const web3ctx = useContext(Web3Context);

  const { uploadFile } = useClaimAdmin({
    targetChain: targetChain,
    ctx: web3ctx,
  });

  // const claimants = useClaimCard({
  //   targetChain,
  //   ctx: web3ctx,
  //   claimId: claimId,
  // });

  // console.log(claimants?.data);

  const onDrop = (file) => {
    console.log("onDrop!,", file);
    console.log("Who is papa", Papa);
    Papa.parse(file[0], {
      header: true,
      skipEmptyLines: true,
      complete: (result) => {
        console.log("Complete: uploading file", claimId, result.data);
        uploadFile.mutate({
          dropperClaimId: claimId,
          claimants: result.data,
        });
      },
      error: (err) => console.log("acceptedFiles csv:", err.message),
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
      // {...props}
    >
      <Flex w="100%" direction={["column", "row", null]}>
        <Flex
          direction={"column"}
          w="100%"
          bgColor={"blue.900"}
          borderRadius="md"
          px={2}
        >
          <Heading as={"h2"} fontSize="lg" borderBottomWidth={1}>
            {"Claim: "}
            {title}
          </Heading>
          <UnorderedList>
            <ListItem>Deadline: {props.claim_block_deadline}</ListItem>
          </UnorderedList>
        </Flex>
      </Flex>
      {description && <chakra.span as={"h3"}>{description}</chakra.span>}
      <FileUpload onDrop={onDrop} />
      <Flex direction={"row"} justifyContent="space-evenly" pt={4}>
        <Button>Activate</Button>
        <Button>Deactivate</Button>
        <Button>See whitelist</Button>
      </Flex>
    </Flex>
  );
};

export default chakra(ContractCard);
