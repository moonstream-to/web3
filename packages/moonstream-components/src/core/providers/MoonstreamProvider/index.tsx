import React from "react";
import MoonstreamContext from "./context";
import { ConstantsInterface } from "../../../../../../types/Site";

const MoonstreamProvider = ({
  children,
  constants,
}: {
  children: JSX.Element;
  constants: ConstantsInterface;
}) => {
  const [values] = React.useState(constants);

  return (
    <MoonstreamContext.Provider value={{ ...values }}>
      {children}
    </MoonstreamContext.Provider>
  );
};

export default MoonstreamProvider;
