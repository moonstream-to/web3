import React, { useState, useRef, useEffect } from "react";
import { chakra, Flex, Box, Button, ButtonGroup } from "@chakra-ui/react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const MAX_POSSIBLE_HEIGHT = 10000;
const maxHeight = (16 + 8) * 4;
const Metadata = ({
  metadata,
  ...props
}: {
  noPreviewChars?: number;
  metadata: any;
}) => {
  const ref = useRef<any>();
  const [shouldShowExpand, setShouldShowExpand] = useState(false);
  const [expanded, setExpanded] = useState(true);

  useEffect(() => {
    if (ref.current.scrollHeight > maxHeight) {
      setShouldShowExpand(true);
      setExpanded(false);
    }
  }, [ref.current?.scrollHeight]);

  return (
    <Flex
      boxShadow={"md"}
      flexGrow={1}
      borderColor={"blue.1200"}
      borderWidth={"3px"}
      minW={["280px", "320px", "420px", null]}
      minH="420px"
      direction="column"
      borderRadius={"lg"}
      whiteSpace="break-spaces"
      px={2}
      {...props}
    >
      <Box
        borderRadius={"lg"}
        h="220px"
        minH="220px"
        w="100%"
        minW="120px"
        id="img"
        m={2}
        p={0}
        backgroundPosition="center"
        bgImage={metadata?.image ?? "none"}
        backgroundSize="contain"
        backgroundRepeat={"no-repeat"}
      ></Box>
      <Box
        ref={ref}
        overflowY="hidden"
        transition={"0.3s"}
        transitionTimingFunction={expanded ? "ease-in" : "ease-out"}
        style={{ maxHeight: expanded ? MAX_POSSIBLE_HEIGHT : maxHeight }}
      >
        <ReactMarkdown className="markdown" remarkPlugins={[remarkGfm]}>
          {metadata?.description}
        </ReactMarkdown>
      </Box>
      <ButtonGroup>
        <Button
          hidden={!shouldShowExpand}
          onClick={() => setExpanded(!expanded)}
          variant={"link"}
          colorScheme="orange"
        >
          Read {expanded ? "less" : "more"}
        </Button>
      </ButtonGroup>
    </Flex>
  );
};

export default chakra(Metadata);
