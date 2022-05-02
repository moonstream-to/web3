import React, { FC } from "react";
import { Flex, Button, chakra, Stack, Input, Fade } from "@chakra-ui/react";
import { TERMINUS_DIAMOND_ADDRESS } from "../AppDefintions";
import { targetChain } from "../core/providers/Web3Provider";
import { FlexProps } from "@chakra-ui/react";
import useTerminus from "../core/hooks/useTerminus";

const STATES = {
  buttons: 0,
  transferOwnershipArgs: 1,
};
const TerminusOwnerPanel: FC<FlexProps> = (props) => {
  const terminus = useTerminus({
    diamondAddress: TERMINUS_DIAMOND_ADDRESS,
    targetChain: targetChain,
  });

  const [state, setState] = React.useState(STATES.buttons);
  const [newOwner, setNewOwnerField] = React.useState("");
  const handleNewOwnerFieldChange = (event: any) =>
    setNewOwnerField(event.target.value);

  return (
    <Flex {...props}>
      <Stack direction={"column"} w="100%">
        <Flex justifyContent={"center"} fontWeight="600" textColor={"blue.50"}>
          Pool owner panel
        </Flex>
        {state === STATES.buttons && (
          <Fade in={state === STATES.buttons ? true : false}>
            <Flex w="100%" justifyContent="space-evenly">
              <Button
                variant={"solid"}
                colorScheme={"orange"}
                size="sm"
                onClick={() => setState(STATES.transferOwnershipArgs)}
              >
                Transfer ownership
              </Button>
            </Flex>
          </Fade>
        )}
        {state === STATES.transferOwnershipArgs && (
          <Fade in={state === STATES.transferOwnershipArgs ? true : false}>
            <Flex
              w="100%"
              justifyContent="center"
              px={[2, 4, 20, null, 20]}
              direction={["column", "column", "row", null, "row"]}
              alignItems="center"
            >
              <Input
                value={newOwner}
                onChange={handleNewOwnerFieldChange}
                placeholder="New terminus owner address"
                size="sm"
                fontSize={"sm"}
              />
              <Flex direction={"row"} alignSelf="center">
                <Button
                  variant={"solid"}
                  colorScheme={"orange"}
                  size="sm"
                  onClick={() =>
                    terminus.transferTerminusOwnershipMutation.mutate({
                      newOwner: newOwner,
                    })
                  }
                  isLoading={
                    terminus.transferTerminusOwnershipMutation.isLoading
                  }
                >
                  Submit
                </Button>
                <Button
                  variant={"solid"}
                  colorScheme={"orange"}
                  size="sm"
                  onClick={() => setState(STATES.buttons)}
                >
                  Cancel
                </Button>
              </Flex>
            </Flex>
          </Fade>
        )}
      </Stack>
    </Flex>
  );
};
export default chakra(TerminusOwnerPanel, {
  baseStyle: {
    w: "100%",
    direction: "row",
    bgColor: "red.100",
    boxShadow: "revert",
  },
});
