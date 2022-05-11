import React from "react";

import { Flex, Button, ButtonGroup, Select, Spacer } from "@chakra-ui/react";
import { useRouter } from "../core/hooks";

const Paginator = ({
  children,
  onForward,
  onBack,
  setLimit,
  paginatorKey,
  hasMore,
  pageOptions,
  ...props
}) => {
  const router = useRouter();
  /**
   *  @dev set page and limit by appending query to url path:
   * @example
   * router.appendQueries({
      claimantsLimit: claimantsPageSize,
      claimantsPage: claimantsPage,
    });
   */
  const page = router.query[`${paginatorKey}Page`];
  const limit = router.query[`${paginatorKey}Limit`];
  const _pageOptions = pageOptions ?? ["25", "50", "100", "300", "500"];

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
          {_pageOptions.map((pageSize) => {
            return (
              <option
                key={`paginator-options-pagesize-${pageSize}`}
                value={pageSize}
              >
                {pageSize}
              </option>
            );
          })}
        </Select>
        <Button isDisabled={!hasMore} onClick={onForward}>{`>>>`}</Button>
      </ButtonGroup>
    </Flex>
  );
  return (
    <Flex className="Paginator" direction={"column"} w="100%" {...props}>
      <PageBar />
      {children}
      <PageBar />
    </Flex>
  );
};
export default Paginator;
