import React, { useContext, useState } from "react";
import { IconButton, Spinner } from "@chakra-ui/react";
import {
  Table,
  Th,
  Td,
  Tr,
  Thead,
  Tbody,
  Button,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverHeader,
  PopoverBody,
  PopoverArrow,
  PopoverCloseButton,
  useBreakpointValue,
} from "@chakra-ui/react";
import { DeleteIcon, TriangleDownIcon } from "@chakra-ui/icons";
import CopyButton from "./CopyButton";
import { BiHappyHeartEyes } from "react-icons/bi";
import ConfirmationRequest from "./ConfirmationRequest";
import { useDrop } from "../core/hooks/dropper";
import Web3Context from "../core/providers/Web3Provider/context";
import Paginator from "./Paginator";

const SORT_BY_TYPES = {
  AMOUNT: 0,
};
const SORT_DIRECTION_TYPES = {
  ASC: true,
  DESC: false,
};
const _ClaimersList = ({ dropId }) => {
  const web3ctx = useContext(Web3Context);
  const {
    deleteClaimants,
    claimants,
    setClaimantsPage,
    claimantsPage,
    setClaimantsPageSize,
    claimantsPageSize,
  } = useDrop({
    ctx: web3ctx,
    claimId: dropId,
  });

  const [sortBy, setSortBy] = useState({
    column: SORT_BY_TYPES.AMOUNT,
    direction: SORT_DIRECTION_TYPES.ASC,
  });

  const buttonSize = useBreakpointValue({
    base: "xs",
    sm: "sm",
    md: "sm",
    lg: "sm",
    xl: "sm",
    "2xl": "sm",
  });

  const cellProps = {
    px: ["2px", "6px", "inherit"],
  };
  return (
    <Paginator
      paginatorKey={"claimants"}
      setPage={setClaimantsPage}
      setLimit={setClaimantsPageSize}
      hasMore={claimants.data?.length == claimantsPageSize ? true : false}
      page={claimantsPage}
      pageSize={claimantsPageSize}
    >
      {!claimants.isLoading && (
        <Table
          variant="simple"
          colorScheme="blue"
          justifyContent="center"
          alignItems="baseline"
          h="auto"
          size="sm"
        >
          <Thead>
            <Tr>
              <Th {...cellProps} fontSize={["xx-small", "xs", null]}>
                Address
              </Th>
              <Th {...cellProps} fontSize={["xx-small", "xs", null]}>
                <Button
                  mx={0}
                  variant="link"
                  my={0}
                  size={buttonSize}
                  colorScheme={
                    sortBy.column !== SORT_BY_TYPES.AMOUNT ? "blue" : "orange"
                  }
                  onClick={() =>
                    setSortBy({
                      column: SORT_BY_TYPES.AMOUNT,
                      direction:
                        sortBy.column !== SORT_BY_TYPES.AMOUNT
                          ? SORT_DIRECTION_TYPES.ASC
                          : !sortBy.direction,
                    })
                  }
                  rightIcon={
                    <TriangleDownIcon
                      color={
                        sortBy.column !== SORT_BY_TYPES.AMOUNT && "transparent"
                      }
                      boxSize="12px"
                      transform={
                        sortBy.direction === SORT_DIRECTION_TYPES.ASC
                          ? "rotate(0deg)"
                          : "rotate(180deg)"
                      }
                    />
                  }
                >
                  {`Amount`}
                </Button>
              </Th>
              <Th {...cellProps} fontSize={["xx-small", "xs", null]}>
                Actions
              </Th>
            </Tr>
          </Thead>
          <Tbody>
            {claimants.data?.map((claimant) => {
              return (
                <Tr key={`token-row-${claimant.address}`}>
                  <Td
                    mr={4}
                    py={0}
                    {...cellProps}
                    isTruncated
                    maxW={["100px", "150px", "300px"]}
                  >
                    <CopyButton text={claimant.address}>
                      <code>{claimant.address}</code>
                    </CopyButton>
                  </Td>
                  <Td py={0} {...cellProps}>
                    {claimant.amount}
                  </Td>
                  <Td py={0} {...cellProps}>
                    <ConfirmationRequest
                      header="Please confirm"
                      confirmLabel="confirm"
                      cancelLabel="cancel"
                      bodyMessage="This will delete claimant form the list"
                      onConfirm={() => {
                        deleteClaimants.mutate({ list: [claimant.address] });
                      }}
                    >
                      <IconButton
                        size="sm"
                        variant="ghost"
                        colorScheme="blue"
                        icon={<DeleteIcon />}
                      />
                    </ConfirmationRequest>

                    <Popover>
                      <PopoverTrigger>
                        <IconButton
                          size="sm"
                          variant="ghost"
                          colorScheme="blue"
                          icon={<BiHappyHeartEyes />}
                        />
                      </PopoverTrigger>
                      <PopoverContent bgColor={"blue.900"}>
                        <PopoverArrow />
                        <PopoverCloseButton />
                        <PopoverHeader>Added by </PopoverHeader>
                        <PopoverBody>{claimant.added_by}</PopoverBody>
                      </PopoverContent>
                    </Popover>
                  </Td>
                </Tr>
              );
            })}
          </Tbody>
        </Table>
      )}
      {(claimants.isLoading || claimants.isFetching) && <Spinner />}
    </Paginator>
  );
};

export default React.memo(_ClaimersList);
