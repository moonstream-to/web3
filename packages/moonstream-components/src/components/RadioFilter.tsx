import React from "react";
import {
  useRadio,
  useRadioGroup,
  Stack,
  HStack,
  Box,
  Text,
  chakra,
} from "@chakra-ui/react";

const RadioFilter = ({
  list,
  handleChange,
}: {
  list: string[];
  handleChange: any;
}) => {
  function CustomRadio(props: any) {
    const { label, ...radioProps } = props;
    const { state, getInputProps, getCheckboxProps, htmlProps, getLabelProps } =
      useRadio(radioProps);

    return (
      <chakra.label {...htmlProps} cursor="pointer">
        <input {...getInputProps({})} hidden />
        <Box
          {...getCheckboxProps()}
          border="1px"
          px={2}
          textColor={state.isChecked ? "white" : "#B6B6B6"}
          borderColor={state.isChecked ? "white" : "#B6B6B6"}
          bgColor="transparent"
          borderRadius="20px"
        >
          <Text {...getLabelProps()}>{label}</Text>
        </Box>
      </chakra.label>
    );
  }
  const { getRadioProps, getRootProps } = useRadioGroup({
    defaultValue: list[0],
    onChange: handleChange,
  });

  return (
    <Stack mt={5} {...getRootProps()}>
      <HStack>
        {list.map((item) => {
          return (
            <CustomRadio
              key={item}
              label={item}
              {...getRadioProps({ value: item })}
            />
          );
        })}
      </HStack>
    </Stack>
  );
};

export default RadioFilter;
