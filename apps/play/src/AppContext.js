import React, { useEffect } from "react";
import { ChakraProvider } from "@chakra-ui/react";
import theme from "./Theme/theme";
import {
  AnalyticsProvider,
  UserProvider,
  UIProvider,
  DataProvider,
  OverlayProvider,
  Web3Provider,
} from "moonstream-components/src/core/providers";
import { StripeProvider } from "moonstream-components/src/core/providers/StripeProvider";
import Fonts from "./Theme/Fonts";

const AppContext = (props) => {
  useEffect(() => {
    const version = "0.0.2";
    if (version) console.log(`Frontend version: ${version}`);
    else
      console.error(
        "NEXT_PUBLIC_FRONTEND_VERSION version variable is not exported"
      );
  }, []);

  return (
    <UserProvider>
      <StripeProvider>
        <ChakraProvider theme={theme}>
          <Fonts />
          <Web3Provider>
            <DataProvider>
              <UIProvider>
                <OverlayProvider>
                  <AnalyticsProvider>{props.children}</AnalyticsProvider>
                </OverlayProvider>
              </UIProvider>
            </DataProvider>
          </Web3Provider>
        </ChakraProvider>
      </StripeProvider>
    </UserProvider>
  );
};

export default AppContext;
