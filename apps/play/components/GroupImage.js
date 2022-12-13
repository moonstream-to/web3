import { HStack, Image } from "@chakra-ui/react";

const GroupImage = ({ shadowcorns, metadata }) => {
  if (!metadata) return <></>;
  return (
    <HStack>
      <span
        style={{
          position: "relative",
          width: `${shadowcorns.length * 16 + 8}px`,
          height: "24px",
        }}
      >
        {shadowcorns.map((item, idx) => {
          return (
            metadata.has(item.address) && (
              <Image
                key={item.address}
                src={metadata.get(item.address)?.image ?? ""}
                w="24px"
                h="24px"
                alt={item.address}
                borderRadius="50%"
                position="absolute"
                left={`${idx * 16}px`}
                top="0"
                zIndex={10 - idx}
              />
            )
          );
        })}
      </span>
    </HStack>
  );
};

export default GroupImage;
