import React, { useEffect } from "react";
import { ChakraProvider } from "@chakra-ui/react";
import theme from "./Theme/theme";
import {
  AnalyticsProvider,
  UIProvider,
  MoonstreamProvider,
  OverlayProvider,
  Web3Provider,
} from "moonstream-components/src/core/providers";
import Fonts from "./Theme/Fonts";
import {
  APP_NAME,
  AWS_ASSETS_PATH,
  COPYRIGHT_NAME,
  DEFAULT_METATAGS,
  SUPPORT_EMAIL,
  TIME_RANGE_SECONDS,
  PRIMARY_MOON_LOGO_URL,
  BACKGROUND_COLOR,
} from "./constants";

const AppContext = (props) => {
  useEffect(() => {
    const version = "0.12";
    if (version) console.log(`Frontend version: ${version}`);
    else
      console.error(
        "NEXT_PUBLIC_FRONTEND_VERSION version variable is not exported"
      );
  }, []);

  return (
    <ChakraProvider theme={theme}>
      <Fonts />
      <Web3Provider>
        <MoonstreamProvider
          constants={{
            SITEMAP: [],
            DEFAULT_METATAGS: DEFAULT_METATAGS,
            TIME_RANGE_SECONDS: TIME_RANGE_SECONDS,
            COPYRIGHT_NAME: COPYRIGHT_NAME,
            SUPPORT_EMAIL: SUPPORT_EMAIL,
            APP_NAME: APP_NAME,
            PRIMARY_MOON_LOGO_URL: PRIMARY_MOON_LOGO_URL,
            AWS_ASSETS_PATH: AWS_ASSETS_PATH,
            BACKGROUND_COLOR: BACKGROUND_COLOR,
          }}
        >
          <UIProvider>
            <OverlayProvider>
              <AnalyticsProvider
                mixpanelToken={process.env.NEXT_PUBLIC_PLAY_MIXPANEL_TOKEN}
              >
                {props.children}
              </AnalyticsProvider>
            </OverlayProvider>
          </UIProvider>
        </MoonstreamProvider>
      </Web3Provider>
    </ChakraProvider>
  );
};

export default AppContext;
