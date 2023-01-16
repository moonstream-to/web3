import React from "react";
import { Flex, Image } from "@chakra-ui/react";
import { PathMetadata } from "./GoFPTypes";
import { useDrop } from "react-dnd";

interface CardProps {
  pathMetadata: PathMetadata;
  accept: string | string[];
  onDrop: (item: any) => void;
  id: string;
}

const PathCard = ({ pathMetadata, accept, onDrop, id }: CardProps) => {
  // const onDrop = () => {
  //   alert(pathMetadata.lore);
  // };
  const [{ isOver, canDrop }, drop] = useDrop({
    accept,
    drop: onDrop,
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  });
  return (
    <Flex flexDirection="column" ref={drop} id={id}>
      <Image
        src={pathMetadata.imageUrl}
        h="200px"
        w="200px"
        border={
          isOver && canDrop
            ? "3px solid yellow"
            : canDrop
            ? "1px solid yellow"
            : "none"
        }
      ></Image>
      {/* <Button bg="gray">Choose</Button> */}
    </Flex>
  );
};

export default PathCard;
