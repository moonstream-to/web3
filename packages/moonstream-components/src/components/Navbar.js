import React, { Suspense } from "react";
import { Flex } from "@chakra-ui/react";

const LandingNavbar = React.lazy(() => import("./LandingNavbar"));

const Navbar = () => {
  return (
    <Flex
      boxShadow={["md", "lg"]}
      zIndex={1}
      shadow={"outline"}
      alignItems="center"
      id="Navbar"
      minH="3rem"
      maxH="3rem"
      bgColor="#1A1D22"
      direction="row"
      w="100%"
      overflow="hidden"
    >
      <Suspense fallback={""}>
        <LandingNavbar />
      </Suspense>
    </Flex>
  );
};

export default Navbar;
