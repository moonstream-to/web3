import { Flex, Image } from "@chakra-ui/react";

const GroupImage = ({ shadowcorns, metadata }) => {
  if (!metadata) return <></>;
  return (
    <Flex alignItems="center">
      <span
        style={{
          marginTop: "auto",
          marginBottom: "auto",
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
                w={["16px", "20px", "24px"]}
                h={["16px", "20px", "24px"]}
                alt={item.address}
                borderRadius="50%"
                position="absolute"
                left={`${idx * 16}px`}
                top={["4px", "2px", "0px"]}
                zIndex={10 - idx}
              />
            )
          );
        })}
      </span>
    </Flex>
  );
};

export default GroupImage;
