import React, { useState } from "react";
import { Flex } from "@chakra-ui/react";
// import { SessionMetadata } from "./GoFPTypes";
import { UseMutationResult } from "react-query";
import ActiveCharPanel from "./GoFPActiveCharPanel";
import AddCharPanel from "./GoFPAddCharPanel";
import { ChoosePathData } from "./GoFPTypes";

const CharacterPanel = ({
  ownedTokens,
  stakedTokens,
  tokenMetadata,
  tokenPaths,
  tokenGuards,
  path,
  setApproval,
  stakeTokens,
  unstakeTokens,
  choosePath,
}: {
  ownedTokens: number[];
  stakedTokens: number[];
  tokenMetadata: any;
  tokenPaths?: Map<number, number>;
  tokenGuards?: Map<number, boolean>;
  path: number;
  setApproval: UseMutationResult<unknown, unknown, void, unknown>;
  stakeTokens: UseMutationResult<unknown, unknown, number[], unknown>;
  unstakeTokens: UseMutationResult<unknown, unknown, number[], unknown>;
  choosePath: UseMutationResult<unknown, unknown, ChoosePathData, unknown>;
}) => {
  const [showActive, setShowActive] = useState<boolean>(
    stakedTokens.length > 0
  );

  return (
    <Flex
      backgroundColor="#353535"
      border="4px solid white"
      borderRadius="20px"
      w="420px"
      h="fit-content"
      minH="320px"
      px={4}
      flexDirection="column"
    >
      {tokenMetadata && (
        <>
          {showActive && (
            <ActiveCharPanel
              activeTokens={stakedTokens}
              tokenMetadata={tokenMetadata}
              tokenPaths={tokenPaths}
              path={path}
              unstakeTokens={unstakeTokens}
              choosePath={choosePath}
              setShowActive={setShowActive}
            />
          )}
          {!showActive && (
            <AddCharPanel
              ownedTokens={ownedTokens}
              tokenMetadata={tokenMetadata}
              tokenGuards={tokenGuards}
              setApproval={setApproval}
              stakeTokens={stakeTokens}
              setShowActive={setShowActive}
            />
          )}
        </>
      )}
    </Flex>
  );
};

export default CharacterPanel;
