import React from "react";
import { Flex, Image, Text, Box } from "@chakra-ui/react";
import { PathMetadata, PathStatus } from "./GoFPTypes";

const PathCard = ({
  pathMetadata,
  status = PathStatus.undecided,
  pathId,
  setSelectedPath,
}: {
  pathMetadata: PathMetadata;
  status: PathStatus;
  pathId: string;
  setSelectedPath: any;
}) => {
  const correctPathColor = "#3BB563";
  const incorrectPathColor = "#E85858";
  const undecidedPathColor = "#4C4C4C";

  const trophy =
    "https://s3.amazonaws.com/static.simiotics.com/play/minigames/trophy.png";
  const skull =
    "https://s3.amazonaws.com/static.simiotics.com/play/minigames/skull.png";

  var cardFill = "";

  switch (status) {
    case PathStatus.correct:
      cardFill = correctPathColor;
      break;
    case PathStatus.incorrect:
      cardFill = incorrectPathColor;
      break;
    case PathStatus.undecided:
      cardFill = undecidedPathColor;
      break;
    default:
      cardFill = undecidedPathColor;
      break;
  }

  return (
    <Box id={pathId} px={2} onClick={() => setSelectedPath()}>
      <Flex
        flexDirection="column"
        position="relative"
        w="122.5px"
        h="170px"
        alignItems="center"
      >
        <Box position="absolute" w="122.5px" h="170px">
          <svg
            width="122.5"
            height="170"
            viewBox="0 0 100 138"
            fill={cardFill}
            opacity="0.5"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M1 8.09388C1 8.09388 6.77761 10.0895 6.7459 12.2739C6.69769 15.5947 6.69769 17.3041 6.69769 17.3041L6.69768 120.696C6.69768 120.696 6.69769 122.405 6.7459 125.726C6.77761 127.91 1 129.906 1 129.906L1.67215 136.343L7.6697 137C7.6697 137 9.28032 131.035 11.9902 131.035H88.0098C90.7197 131.035 92.3303 137 92.3303 137L98.3279 136.343L99 129.906C99 129.906 93.2224 127.91 93.2541 125.726C93.3023 122.405 93.3023 120.696 93.3023 120.696V17.3041C93.3023 17.3041 93.3023 15.5947 93.2541 12.2739C93.2224 10.0895 99 8.09388 99 8.09388L98.3279 1.65679L92.3303 1C92.3303 1 90.7197 6.96489 88.0098 6.96489H11.9902C9.28032 6.96489 7.6697 1 7.6697 1L1.67215 1.65679L1 8.09388Z"
              stroke="white"
            />
          </svg>
        </Box>
        <Box position="relative" h="90px" w="90px">
          <Image
            alt={pathId}
            src={status == PathStatus.correct ? trophy : skull}
            h="40px"
            w="40px"
            mt="30px"
            ml="25px"
            position="absolute"
            display={status == PathStatus.undecided ? "none" : ""}
          ></Image>
          <Image
            alt={pathId}
            src={pathMetadata.imageUrl}
            h="90px"
            w="90px"
            mt={4}
            border="1px solid"
            borderColor="white"
            position="relative"
            opacity={status == PathStatus.undecided ? 1.0 : 0.4}
          ></Image>
          <Text fontSize="sm" color="white" align="center">
            {pathMetadata.title}
          </Text>
        </Box>
      </Flex>
    </Box>
  );
};

export default PathCard;
