import React, { useContext, useState } from "react";
import { chakra, Button, Flex, Heading, Image } from "@chakra-ui/react";
import Web3Context from "../../core/providers/Web3Provider/context";
import useLootboxToken from "../../core/hooks/useLootboxToken";

const LootboxCard = ({
  contractAddress,
  lootboxId,
  hasActiveOpening,
  activeOpening,
  ...props
}) => {
  const web3ctx = useContext(Web3Context);
  const [metadata, setMetadata] = useState(null);

  const { state, openLootbox, completeLootboxOpening } = useLootboxToken({
    contractAddress: contractAddress,
    lootboxId: lootboxId,
    ctx: web3ctx,
  });

  if (state.isFetched && !metadata) {
    console.log(state.data);

    if (state.data.lootboxUri === "") {
      setMetadata({
        name: "No metadata",
        title: "No metadata",
        description: "No metadata",
      });

      return;
    } else {
      console.log("it has url", state.data.lootboxUri);
    }

    fetch(state.data.lootboxUri).then((response) => {
      response.json().then((data) => {
        console.log(data);
        setMetadata(data);
      });
    });
  }

  const openTheLootbox = () => {
    console.log("openLootbox");
    openLootbox(lootboxId, 1);
  };

  return (
    <Flex
      borderRadius={"20px"}
      border="1px solid white"
      bgColor="#1A1D22"
      w="100%"
      direction={"column"}
      p={4}
      mt={2}
      textColor={"gray.300"}
      {...props}
    >
      <Heading as={"h2"} fontSize="lg" borderBottomWidth={1}>
        {"LootboxId: "}
        {lootboxId}
      </Heading>

      {metadata && <chakra.span as={"h3"}>{metadata.name}</chakra.span>}
      {state.isFetched && (
        <chakra.span as={"h3"}>
          Balance: {state.data.lootboxBalance}
        </chakra.span>
      )}
      {metadata?.image && (
        <Image
          boxSize="200px"
          border="1px solid #4D4D4D"
          borderRadius="10px"
          src={metadata.image}
          alt={metadata.description}
        />
      )}
      {!hasActiveOpening && (
        <Button
          variant="orangeOutline"
          onClick={openTheLootbox}
          isDisabled={!(state.isFetched && state.data.lootboxBalance !== "0")}
        >
          {" "}
          Open{" "}
        </Button>
      )}
      {hasActiveOpening && (
        <Button
          variant="orangeOutline"
          onClick={completeLootboxOpening}
          isDisabled={!activeOpening.isReadyToComplete}
        >
          {" "}
          Complete Opening{" "}
        </Button>
      )}
    </Flex>
  );
};

export default chakra(LootboxCard);
