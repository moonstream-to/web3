import React from "react";
import {
  Flex,
  Button,
  chakra,
  Fade,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from "@chakra-ui/react";

const Web3MethodForm = ({
  method,
  argumentFields,
  rendered,
  onClick,
  isLoading,
  onCancel,
}: {
  method: any;
  argumentFields: any;
  rendered: any;
  onClick: any;
  isLoading: any;
  onCancel: any;
}) => {
  const setArguments = (
    state: any,
    { value, index }: { value: any; index: any }
  ) => {
    const newState = { ...state };

    newState.inputs[index]["meta"]["value"] = value;
    return { ...newState };
  };

  const initialState = React.useMemo(() => {
    // console.debug("memo trig");
    const newState = { ...method };
    newState.inputs.forEach((element: any, index: any) => {
      newState.inputs[index]["meta"] = {
        placeholder: argumentFields[element.name]?.placeholder ?? element.name,
        value: argumentFields[element.name]?.initialValue ?? "",
      };
    });
    return newState;
    //eslint-disable-next-line
  }, [method]);

  const [state, dispatchArguments] = React.useReducer(
    setArguments,
    initialState
  );

  const [wasSent, setWasSent] = React.useState(false);

  const handleClose = React.useCallback(() => {
    state.inputs.forEach((inputElement: any, index: any) => {
      dispatchArguments({
        value: argumentFields[inputElement.name]?.initialValue ?? undefined,
        index,
      });
    });
    onCancel();
  }, [state, argumentFields, onCancel]);
  const handleSubmit = () => {
    const returnedObject: any = {};
    state.inputs.forEach((inputElement: any) => {
      returnedObject[inputElement.name] = inputElement.meta.value;
    });

    onClick(returnedObject);
  };

  React.useEffect(() => {
    if (!isLoading && wasSent) {
      setWasSent(false);
      handleClose();
    }
    if (!wasSent && isLoading) {
      setWasSent(true);
    }
  }, [isLoading, state, argumentFields, onCancel, wasSent, handleClose]);

  const handleKeypress = (e: any) => {
    console.debug("handleKeypress!", e.charCode);
    //it triggers by pressing the enter key
    if (e.charCode === 13) {
      handleSubmit();
    }
  };

  if (!rendered) return <></>;
  return (
    <Fade in={rendered} style={{ width: "100%" }}>
      <Flex w="100%" justifyContent="center" px={20} alignItems="center">
        {state.inputs.map((inputItem: any, index: any) => {
          if (
            Object.keys(argumentFields).includes(inputItem.name) &&
            inputItem.name
          ) {
            return (
              <>
                {inputItem.type === "string" && (
                  <Input
                    onKeyPress={handleKeypress}
                    type="search"
                    key={`argument-string-${inputItem.name}`}
                    value={inputItem.meta.value}
                    onChange={(event) =>
                      dispatchArguments({
                        value: event.target.value,
                        index,
                      })
                    }
                    placeholder={inputItem.meta.placeholder}
                    size="sm"
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                    minW="420px"
                  />
                )}
                {inputItem.type === "address" && (
                  <Input
                    onKeyPress={handleKeypress}
                    type="search"
                    key={`argument-address-${inputItem.name}`}
                    value={inputItem.meta.value}
                    onChange={(event) =>
                      dispatchArguments({
                        value: event.target.value,
                        index,
                      })
                    }
                    placeholder={inputItem.meta.placeholder}
                    size="sm"
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                    minW="420px"
                  />
                )}
                {inputItem.type === "uint256" && (
                  <NumberInput
                    key={`argument-num-${inputItem.name}`}
                    onKeyPress={handleKeypress}
                    defaultValue={0}
                    onChange={(value) =>
                      dispatchArguments({
                        value: value,
                        index,
                      })
                    }
                    value={inputItem.meta.value}
                    size="sm"
                    mx={2}
                    isDisabled={isLoading}
                    variant="outline"
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                )}
              </>
            );
          }
        })}
        <Button
          variant={"solid"}
          colorScheme={"orange"}
          size="sm"
          onClick={handleSubmit}
          isLoading={isLoading}
        >
          Submit
        </Button>
        <Button
          variant={"solid"}
          colorScheme={"orange"}
          size="sm"
          onClick={() => handleClose()}
        >
          Cancel
        </Button>
      </Flex>
    </Fade>
  );
};

export default chakra(Web3MethodForm);
