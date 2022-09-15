import React from "react";
import Link from "next/link";
import {
  Stack,
  Image as ChakraImage,
  Heading,
  chakra,
  Link as ChakraLink,
} from "@chakra-ui/react";
// export interface FeatureCardArgs extends ChakraProps {
//   text: string;
//   heading: string;
//   link: string;
//   imageUrl: string;
//   textColor: string;
//   alt: string;
//   level?: any;
// }

const FeatureCard = ({
  text,
  heading,
  link,
  imageUrl,
  textColor,
  imgH,
  alt,
  level,
  imgPading,
  isExternal,
  ...props
}) => {
  const Wrapper = (wrapperProps) => {
    if (props.disabled) return wrapperProps.children;
    return (
      <Link href={link} shallow scroll passHref>
        <ChakraLink isExternal={isExternal}>{wrapperProps.children}</ChakraLink>
      </Link>
    );
  };
  return (
    <Wrapper>
      <Stack
        bgColor={props.disabled ? "gray.1600" : undefined}
        {...props}
        transition={"1s"}
        spacing={1}
        px={5}
        alignItems="center"
        borderRadius="12px"
        borderColor="gray.100"
        borderWidth={"1px"}
        _hover={{ transform: "scale(1.05)", transition: "0.42s" }}
        m={2}
        pb={2}
        pt={imgPading}
        // justifyContent={"center"}
      >
        {imageUrl && (
          <ChakraImage
            boxSize={["220px", "220px", "xs", null, "xs"]}
            maxH={imgH}
            minH={imgH}
            objectFit="contain"
            src={imageUrl}
            alt={alt}
            mb={12}
          />
        )}
        <Heading textAlign="center" as={level ?? "h2"} _hover={{}}>
          {heading}
        </Heading>
        <chakra.span
          textAlign={"center"}
          textColor={textColor ?? "blue.400"}
          px={2}
        >
          {text}
        </chakra.span>
      </Stack>
    </Wrapper>
  );
};

export default chakra(FeatureCard);
