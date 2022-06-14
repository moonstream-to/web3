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
  WHITE_LOGO_W_TEXT_URL,
} from "./constants";
import { PAGETYPE } from "../../../types/Site";

const AppContext = (props) => {
  useEffect(() => {
    const version = "0.35";
    if (version) console.log(`Frontend version: ${version}`);
    else console.error("version variable is not set");
  }, []);

  return (
    <ChakraProvider theme={theme}>
      <Fonts />
      <Web3Provider>
        <MoonstreamProvider
          constants={{
            SITEMAP: [
              {
                title: "Resources",
                children: [
                  { title: "Api Docs", path: "/docs", type: PAGETYPE.CONTENT },
                ],
              },
            ],
            DEFAULT_METATAGS: DEFAULT_METATAGS,
            TIME_RANGE_SECONDS: TIME_RANGE_SECONDS,
            COPYRIGHT_NAME: COPYRIGHT_NAME,
            SUPPORT_EMAIL: SUPPORT_EMAIL,
            APP_NAME: APP_NAME,
            WHITE_LOGO_W_TEXT_URL: WHITE_LOGO_W_TEXT_URL,
            AWS_ASSETS_PATH: AWS_ASSETS_PATH,
          }}
        >
          <UIProvider>
            <OverlayProvider>
              <AnalyticsProvider
                mixpanelToken={process.env.NEXT_PUBLIC_ENGINE_MIXPANEL_TOKEN}
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
