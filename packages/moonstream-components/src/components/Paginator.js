import React from "react";

import {
  Flex,
  Button,
  ButtonGroup,
  Select,
  Spacer,
  chakra,
  ScaleFade,
} from "@chakra-ui/react";
import { useRouter } from "../core/hooks";

const _Paginator = ({
  children,
  setLimit,
  setPage,
  paginatorKey,
  hasMore,
  pageOptions,
  page,
  pageSize,
  ...props
}) => {
  const router = useRouter();

  const _pageOptions = pageOptions ?? ["25", "50", "100", "300", "500"];
  const [pageUpdate, setpageUpdate] = React.useState(true);
  const [isMounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    let timer1;
    if (pageUpdate) {
      timer1 = setTimeout(() => {
        setpageUpdate(false);
      }, 200);
    }
    return () => {
      clearTimeout(timer1);
    };
    //eslint-disable-next-line
  }, [pageUpdate]);

  React.useEffect(() => {
    let queries = {};
    if (!router.query[`${paginatorKey}Page`]) {
      queries[`${paginatorKey}Page`] = 0;
    }
    if (!router.query[`${paginatorKey}Limit`]) {
      queries[`${paginatorKey}Limit`] = _pageOptions[0];
    }
    router.appendQueries({ ...queries });
    if (!isMounted) {
      setMounted(true);
    }

    //eslint-disable-next-line
  }, []);

  const __page = router.query[`${paginatorKey}Page`];
  const __limit = router.query[`${paginatorKey}Limit`];
  React.useLayoutEffect(() => {
    const _page = Number(router.query[`${paginatorKey}Page`]);
    const _limit = Number(router.query[`${paginatorKey}Limit`]);

    if (!isNaN(_page) && page !== _page) {
      setPage(_page);
    }
    if (!isNaN(_limit) && pageSize !== _limit) {
      if (isMounted) {
        router.appendQuery(`${paginatorKey}Page`, 0);
        setPage(0);
      }
      setLimit(_limit);
    }

    //eslint-disable-next-line
  }, [__page, __limit, page, pageSize, paginatorKey, setPage, setLimit]);

  const PageBar = () => (
    <Flex justifyContent={"space-between"} py={4} pt={2}>
      <ButtonGroup
        size="sm"
        variant={"outline"}
        colorScheme="orange"
        justifyContent={"space-between"}
        w="100%"
        alignItems="baseline"
      >
        <Button
          isDisabled={router.query[`${paginatorKey}Page`] == "0"}
          onClick={() => {
            setpageUpdate(true);
            router.appendQuery(
              `${paginatorKey}Page`,
              Number(router.query[`${paginatorKey}Page`]) - 1 <= 0
                ? 0
                : Number(router.query[`${paginatorKey}Page`]) - 1
            );
          }}
        >
          {`<<<`}
        </Button>
        <Spacer />
        <Select
          size="sm"
          maxW="150px"
          placeholder="Select page size"
          onChange={(e) => {
            router.appendQuery(`${paginatorKey}Limit`, e.target.value);
          }}
          value={router.query[`${paginatorKey}Limit`] ?? _pageOptions[0]}
          bgColor="blue.500"
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
        <Button
          isDisabled={!hasMore}
          onClick={() => {
            setpageUpdate(true);
            router.appendQuery(
              `${paginatorKey}Page`,
              Number(router.query[`${paginatorKey}Page`]) + 1
            );
          }}
        >{`>>>`}</Button>
      </ButtonGroup>
    </Flex>
  );
  return (
    <Flex className="Paginator" direction={"column"} w="100%" {...props}>
      <PageBar />
      <ScaleFade in={!pageUpdate}>{children}</ScaleFade>
      <PageBar />
    </Flex>
  );
};

const Paginator = chakra(React.memo(_Paginator));

export default Paginator;
