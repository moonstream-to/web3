import { Flex } from "@chakra-ui/react";

const LeaderboardRank = ({ rank }) => {
  return (
    <Flex
      my="auto"
      fontWeight="700"
      w={["20px", "20px", "34px"]}
      h={["20px", "20px", "28px"]}
      bg={
        rank === 1
          ? "#F5C841"
          : rank === 2
          ? "#DADADA"
          : rank === 3
          ? "#E98F5C"
          : "transparent"
      }
      color={rank < 4 ? "black" : "white"}
      borderRadius="6px"
      textAlign="center"
      justifyContent="center"
      alignItems="center"
    >
      {rank}
    </Flex>
  );
};

export default LeaderboardRank;
