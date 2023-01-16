import { useDrag } from "react-dnd";
import { Flex, Text } from "@chakra-ui/react";

const GoFPCharacter = ({ character }) => {
  const [{ isDragging }, drag] = useDrag({
    item: { name: character },
    type: character === "Frodo" ? "Frodo" : "character",
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const opacity = isDragging ? 0.3 : 1;

  return (
    <Flex
      w="75px"
      h="75px"
      border="1px solid white"
      borderRadius="10px"
      ref={drag}
      className="movable-item"
      style={{ opacity }}
      cursor="pointer"
    >
      <Text m="auto">{character}</Text>
    </Flex>
  );
};

export default GoFPCharacter;
