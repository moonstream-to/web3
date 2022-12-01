// import { mode, whiten } from "@chakra-ui/theme-tools"

const Menu = {
  parts: ["list", "item"],
  baseStyle: (props) => {
    const { colorScheme: c } = props;
    return {
      item: {
        fontWeight: "medium",
        lineHeight: "normal",
        textColor: `${c}.900`,

        _hover: {
          bg: `orange.800`,
          textColor: "white.100",
        },
        _focus: {
          bg: `orange.700`,
          textColor: "white.100",
        },
      },
      list: {
        bg: "white.200",
        borderWidth: 0,
      },
    };
  },
  variants: {
    bw: {
      list: {
        bg: "black.300",
        color: "white",
        borderRadius: "10px",
        border: "1px solid white",
        px: "10px",
      },
      item: {
        my: "5px",
        fontSize: "16px",
        border: "1px solid transparent",
        borderRadius: "10px",
        _hover: {
          _disabled: {
            color: "white",
          },
          backgroundColor: "transparent",
          color: "orange.1000",
          borderColor: "white",
        },
        _focus: {
          backgroundColor: "transparent",
          color: "orange.1000",
        },
        _disabled: {
          borderColor: "white",
          _after: {
            marginLeft: "10px",
            content: '" \u2713"',
          },
        },
      },
    },
  },
};

export default Menu;
