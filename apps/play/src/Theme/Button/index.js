// import { mode, transparentize } from "@chakra-ui/theme-tools"

const variantAccountMenu = (props) => {
  const { colorScheme: c } = props;

  return {
    width: "100%",
    w: "100%",
    borderRadius: "0px",
    borderStyle: "solid",
    borderTopWidth: "1px",
    bgColor: `white.200`,
    borderColor: `gray.100`,
    color: `black.100`,
    m: 0,
    _hover: {
      bg: `white.300`,
      // color: `white.100`,
    },
    _focus: {
      textDecoration: "underline",
      outline: "none",
      // color: `white.100`,
    },
    _active: {
      textDecoration: "none",
      // bg: `${c}.200`,
      // color: `white.100`,
      _before: {
        position: "absolute",
        content: "''",
        top: "0",
        bottom: "0",
        left: "0",
        width: "0.5rem",
        backgroundColor: `${c}.400`,
      },
      _last: {
        _before: {
          borderBottomLeftRadius: "md",
        },
      },
    },
    _last: {
      my: "-1px",
      borderBottomWidth: "1px",
      boxSizing: "border-box",
      borderBottomRadius: "md",
    },
  };
};

const variantLink = () => {
  // const { colorScheme: c } = props;
  return {
    _focus: {
      textDecoration: "underline",
    },
  };
};

const variantOutline = (props) => {
  const { colorScheme: c } = props;
  return {
    borderColor: `${c}.900`,
    borderWidth: `0.125rem`,
    boxSizing: "border-box",
    color: `${c}.900`,
    _hover: {
      boxShadow: "md",
    },
    _focus: {
      textDecoration: "underline",
    },
  };
};
const variantSolid = (props) => {
  const { colorScheme: c } = props;
  return {
    bg: `${c}.900`,
    _focus: {
      textDecoration: "underline",
    },
    _disabled: {
      bg: `${c}.200`,
    },
    _hover: {
      bg: `${c}.500`,
      // color: `${c}.100`,
      _disabled: {
        bg: `${c}.100`,
      },
    },
  };
};

const variantGhost = (props) => {
  const { colorScheme: c } = props;

  return {
    // color: `white.100`,
    _focus: {
      textDecoration: "underline",
    },
    _disabled: {
      bg: `${c}.50`,
    },
    _hover: {
      // bg: `${c}.600`,
      _disabled: {
        bg: `${c}.100`,
      },
    },
  };
};

const variantWhiteOutline = (props) => {
  const color = props["data-selected"] ? "white" : "#BFBFBF";
  return {
    color,
    borderColor: color,
    padding: ["2px 5px", "5px 10px", "10px 20px"],
    borderWidth: "2px",
    borderStyle: "solid",
    borderRadius: ["50px", "75px", "100px"],
    fontWeight: "400",
    fontSize: ["sm", "md", "lg"],
  };
};

const variantOrangeOutline = () => {
  return {
    color: "#F56646",
    backgroundColor: "transparent",
    borderColor: "#F56646",
    borderStyle: "solid",
    borderWidth: "2px",
    borderRadius: "10px",
    fontWeight: "500",
    _hover: {
      borderColor: "#F4532F",
      backgroundColor: "transparent",
      color: "#F4532F",
      fontWeight: "700",
    },
    _active: {
      color: "#F4532F",
      borderColor: "#F4532F",
      textDecoration: "none",
    },
  };
};

const variantCUbutton = () => {
  return {
    padding: ["5px 10px", "5px 10px", "10px 20px"],
    fontSize: ["sm", "md", "lg"],
    fontWeight: "700",
    borderRadius: "10px",
    _hover: {
      backgroundColor: "#D5D5D5",
    },
  };
};

const Button = {
  // 1. We can update the base styles
  baseStyle: () => ({
    px: "1rem",
    py: "1rem",
    transition: "0.1s",
    width: "fit-content",
    borderRadius: "md",
    borderStyle: "solid",
    fontWeight: "600",
    m: 1,

    // _active: {
    //   bg: `${props.colorScheme}.${props.colorMode}.200`,
    //   color: `${props.colorScheme}.${props.colorMode}.50`,
    // },
    // _focus: {
    //   bg: `${props.colorScheme}.${props.colorMode}.400`,
    //   color: `${props.colorScheme}.${props.colorMode}.50`,
    // },
  }),
  // 2. We can add a new button size or extend existing
  sizes: {
    xl: {
      h: 16,
      minW: 16,
      fontSize: "4xl",
      px: 8,
    },
  },
  // 3. We can add a new visual variant
  variants: {
    accountMenu: variantAccountMenu,
    solid: variantSolid,
    ghost: variantGhost,
    outline: variantOutline,
    link: variantLink,
    orangeOutline: variantOrangeOutline,
    whiteOutline: variantWhiteOutline,
    cuButton: variantCUbutton,
  },
};
export default Button;
