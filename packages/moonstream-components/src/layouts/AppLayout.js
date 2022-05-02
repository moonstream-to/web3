import React, { useContext, useEffect } from "react";
import { Flex, Spinner, Box } from "@chakra-ui/react";
import { getLayout as getSiteLayout } from "./RootLayout";
import UIContext from "../core/providers/UIProvider/context";
import { IS_AUTHENTICATION_REQUIRED } from "../core/constants";

const AppLayout = ({ children }) => {
  const ui = useContext(UIContext);

  useEffect(() => {
    ui.setAppView(true);
    return () => {
      ui.setAppView(false);
    };
    // eslint-disable-next-line
  }, []);

  const allowApp = IS_AUTHENTICATION_REQUIRED
    ? ui.isAppReady && ui.isLoggedIn
    : ui.isAppReady;

  return (
    <Flex
      direction="row"
      id="AppWrapper"
      flexGrow={1}
      maxH="100%"
      w="100%"
      overflow="hidden"
    >
      {!allowApp && (
        <Spinner
          position="absolute"
          top="50%"
          left="50%"
          size="xl"
          speed="1s"
          zIndex={100001}
        />
      )}
      {!allowApp && (
        <Box
          position="absolute"
          top="0"
          bottom={0}
          left={0}
          right={0}
          bg="rgba(0,0,0,0.7)"
          zIndex={100000}
        />
      )}

      {allowApp && children}
    </Flex>
  );
};

export const getLayout = (page) => getSiteLayout(<AppLayout>{page}</AppLayout>);

export default AppLayout;
