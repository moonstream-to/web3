import React from "react";
import { RedocStandalone } from "redoc";
import { Box } from "@chakra-ui/react";

const RedocComponent = ({ specUrl }) => {
  return (
    <Box w="100%" maxH="100vh" overflowY="scroll">
      <RedocStandalone
        specUrl={specUrl}
        options={{
          theme: {
            colors: {
              primary: { main: "#212990" },
              success: { main: "#92D050" },
              warning: { main: "#FD5602" },
              error: { main: "#C53030" },
              gray: { 50: "#f7f8fa", 100: "#eff1f4" },
            },
            rightPanel: { backgroundColor: "#34373d" },
          },
        }}
      />
    </Box>
  );
};

export default RedocComponent;
