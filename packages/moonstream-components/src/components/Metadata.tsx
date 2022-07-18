import React, { useState, useRef, useEffect } from "react";
import {
  chakra,
  Flex,
  Box,
  Button,
  ButtonGroup,
  Heading,
} from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MAX_POSSIBLE_HEIGHT = 10000;
const maxHeight = (16 + 8) * 4;
const Metadata = ({
  metadata,
  children,
  ...props
}: {
  noPreviewChars?: number;
  children: React.ReactNode;
  metadata: any;
}) => {
  const ref = useRef<any>();
  // const [shouldShowExpand, setShouldShowExpand] = useState(false);
  // const [expanded, setExpanded] = useState(true);

  // useEffect(() => {
  //   if (ref.current.scrollHeight > maxHeight) {
  //     setShouldShowExpand(true);
  //     setExpanded(false);
  //   }
  // }, [ref.current?.scrollHeight]);

  return (
    <Flex
      boxShadow={"md"}
      w="315px"
      h="420px"
      direction="column"
      borderRadius={"lg"}
      whiteSpace="break-spaces"
      {...props}
    >
      <Box
        borderRadius={"lg"}
        id="img"
        w="315px"
        h="315px"
        minH="315px"
        minW="315px"
        m={0}
        p={0}
        backgroundPosition="center"
        bgImage={metadata?.image ?? "none"}
        backgroundSize="contain"
        backgroundRepeat={"no-repeat"}
        position="relative"
      >
        {children && children}
      </Box>
      <Flex
        direction={"column"}
        px={4}
        h="146px"
        overflow={"hidden"}
        textOverflow="ellipsis"
        isTruncated
      >
        <Box
          ref={ref}
          overflowY="hidden"
          w="100%"
          transition={"0.3s"}
          // transitionTimingFunction={expanded ? "ease-in" : "ease-out"}
          // style={{ maxHeight: expanded ? MAX_POSSIBLE_HEIGHT : maxHeight }}
        >
          <Heading size="md" mt={4}>
            {metadata?.name}
          </Heading>
          {/* <Box isTruncated noOfLines={2}> */}
          <ReactMarkdown
            // escapeHtml={false}
            // components={renderers}
            className="markdown"
            remarkPlugins={[remarkGfm]}
            // renderers={{ root: React.Fragment }}
          >
            {metadata?.description}
          </ReactMarkdown>
          {/* </Box> */}
        </Box>
        {/* <ButtonGroup>
          <Button
            hidden={!shouldShowExpand}
            onClick={() => setExpanded(!expanded)}
            variant={"link"}
            colorScheme="orange"
          >
            Read {expanded ? "less" : "more"}
          </Button>
        </ButtonGroup> */}
      </Flex>
    </Flex>
  );
};

export default chakra(Metadata);
