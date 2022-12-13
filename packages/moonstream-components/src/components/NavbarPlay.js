import React, { Suspense } from "react";
import { Flex } from "@chakra-ui/react";

const LandingNavbar = React.lazy(() => import("./LandingNavbarPlay"));

const Navbar = () => {
  return (
    <Flex
      zIndex={1}
      alignItems="center"
      id="Navbar"
      minH="56px"
      maxH="56px"
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
