import React, { useContext } from "react";
import {
    chakra,
    Flex,
    Heading,
    ListItem,
    UnorderedList,
} from "@chakra-ui/react";
import { targetChain } from "../../core/providers/Web3Provider";
import Web3Context from "../../core/providers/Web3Provider/context";
import useLootbox from "../../core/hooks/useLootbox";

const LootboxCard = ({ lootboxId, ...props }) => {
    const web3ctx = useContext(Web3Context);

    //TODO(yhtiyar): remove hardcoded address
    const { state } = useLootbox({
        contractAddress: "0x44b43b762E15Fb3dFC132030672Ca47caD5aa68c",
        lootboxId: lootboxId,
        targetChain: targetChain,
        ctx: web3ctx,
    });

    const onOpen = () => {
        console.log("open!");
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
            <Heading as={"h2"} fontSize="lg" borderBottomWidth={1}>
                {"Claim: "}
                {lootboxId}
            </Heading>
            <UnorderedList>
                <ListItem>Deadline: {props.claim_block_deadline}</ListItem>
            </UnorderedList>
            {description && <chakra.span as={"h3"}>{description}</chakra.span>}
            <FileUpload onDrop={onDrop} />
        </Flex>
    );
};

export default chakra(ContractCard);
