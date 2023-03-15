import React from "react";
import { RedocStandalone } from "redoc";
import { Box } from "@chakra-ui/react";
import { getLayout } from "moonstream-components/src/layouts/RootLayout";
import { DEFAULT_METATAGS } from "../../src/constants";

const API =
  process.env.NEXT_PUBLIC_ENGINE_API_URL ??
  process.env.NEXT_PUBLIC_PLAY_API_URL;

const Docs = () => {
  return (
    <>
      <Box w="100%" maxH="100vh" overflowY="scroll" zIndex={0} bgColor="white">
        <RedocStandalone
          specUrl={`${API}/admin/openapi.json`}
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
    </>
    // </Box>
  );
};

export async function getStaticProps() {
  const metaTags = {
    title: "Moonstream: engine API Documentation",
    description: "API Documentation to use engine.moonstream.to",
    keywords: "API, docs",
    url: "https://www.engine.moonstream.to/docs",
  };
  return { props: { metaTags: { ...DEFAULT_METATAGS, ...metaTags } } };
}

Docs.getLayout = getLayout;
export default Docs;
