import React from "react";

import { Flex, Button, ButtonGroup, Select, Spacer } from "@chakra-ui/react";
import { useRouter } from "../core/hooks";

const Paginator = ({
  children,
  onForward,
  onBack,
  setLimit,
}) => {
  const router = useRouter();
  const { page, limit } = router.query;
  const PageBar = () => (
    <Flex justifyContent={"space-between"} pt={2}>
      <ButtonGroup
        size="sm"
        variant={"outline"}
        colorScheme="orange"
        justifyContent={"space-between"}
        w="100%"
        alignItems="baseline"
      >
        <Button isDisabled={page == "0"} onClick={onBack}>
          {`<<<`}
        </Button>
        <Spacer />
        <Select
          size="sm"
          maxW="150px"
          placeholder="Select page size"
          onChange={(e) => setLimit(e.target.value)}
          value={limit}
        >
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="100">100</option>
          <option value="300">300</option>
          <option value="500">500</option>
        </Select>
        <Button onClick={onForward}>{`>>>`}</Button>
      </ButtonGroup>
    </Flex>
  );
  return (
    <Flex className="Paginator" direction={"column"} w="100%">
      <PageBar />
      {children}
      <PageBar />
    </Flex>
  );
};
export default Paginator;
