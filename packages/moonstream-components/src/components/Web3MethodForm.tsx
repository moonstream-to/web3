import React, { Fragment, useContext } from "react";
import {
  Flex,
  Button,
  chakra,
  Fade,
  Input,
  Stack,
  Text,
  Heading,
  Box,
} from "@chakra-ui/react";
import { AbiInput, AbiItem } from "web3-utils";
import { useMutation } from "react-query";
import Web3Context from "../core/providers/Web3Provider/context";
import { useToast } from "../core/hooks";

interface argumentField {
  placeholder: string;
  initialValue: string;
  // hide: boolean;
}
interface argumentFields {
  [Key: string]: argumentField;
}

interface extendedInputs extends AbiInput {
  meta?: {
    value: number | string;
    placeholder: number | string;
    hide: boolean;
  };
}
interface stateInterface extends Omit<AbiItem, "inputs"> {
  inputs: Array<extendedInputs>;
}

// interface

const Web3MethodForm = ({
  method,
  argumentFields,
  hide,
  rendered,
  onClick,
  onCancel,
  contractAddress,
  ...props
}: {
  method: AbiItem;
  argumentFields?: argumentFields;
  hide?: string[];
  rendered: boolean;
  onClick?: Function;
  onCancel?: Function;
  contractAddress: string;
  props?: any;
}) => {
  const setArguments = (
    state: any,
    { value, index }: { value: any; index: any }
  ) => {
    const newState = { ...state };

    newState.inputs[index]["meta"]["value"] = value;
    return { ...newState };
  };

  const toast = useToast();
  const initialState = React.useMemo(() => {
    const newState: stateInterface = { ...(method as any) };
    newState.inputs?.forEach((element: any, index: number) => {
      newState.inputs[index]["meta"] = {
        placeholder:
          (argumentFields && argumentFields[element.name]?.placeholder) ??
          element.name,
        value:
          (argumentFields && argumentFields[element.name]?.initialValue) ?? "",
        hide: hide?.includes(element.name) ?? false,
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
        value:
          (argumentFields && argumentFields[inputElement.name]?.initialValue) ??
          undefined,
        index,
      });
    });
    if (onCancel) {
      onCancel();
    }
  }, [state, argumentFields, onCancel]);

  const web3call = async ({ args }: { args: any }) => {
    const contract = new web3ctx.web3.eth.Contract([method]);
    contract.options.address = contractAddress;
    const response =
      method.name &&
      (await contract.methods[method.name](...args).send({
        from: web3ctx.account,
      }));
    return response;
  };
  const tx = useMutation(({ args }: { args: any }) => web3call({ args }), {
    onSuccess: () => {
      toast("Transaction went to the moon!", "success");
    },
    onError: () => {
      toast("Transaction failed >.<", "error");
    },
  });

  const handleSubmit = () => {
    const returnedObject: any = [];
    state.inputs.forEach((inputElement: any, index: number) => {
      returnedObject[index] =
        inputElement.type === "address"
          ? web3ctx.web3.utils.toChecksumAddress(inputElement.meta.value)
          : inputElement.meta.value;
    });

    tx.mutate({ args: returnedObject });
    onClick && onClick(returnedObject);
  };

  React.useEffect(() => {
    if (!tx.isLoading && wasSent) {
      setWasSent(false);
      handleClose();
    }
    if (!wasSent && tx.isLoading) {
      setWasSent(true);
    }
  }, [tx.isLoading, state, argumentFields, onCancel, wasSent, handleClose]);

  const handleKeypress = (e: any) => {
    //it triggers by pressing the enter key
    if (e.charCode === 13) {
      handleSubmit();
    }
  };

  const web3ctx = useContext(Web3Context);

  if (!rendered) return <></>;
  return (
    <Fade in={rendered}>
      <Stack justifyContent="center" px={2} alignItems="center" {...props}>
        <Heading
          wordBreak={"break-all"}
          fontSize={
            method?.name?.length && method?.name?.length > 12 ? "xl" : "3xl"
          }
        >
          {method.name}
        </Heading>
        {state.inputs.map((inputItem: any, index: any) => {
          if (!inputItem.hide) {
            return (
              <Box key={`${inputItem.name}-${index}-abiitems`} w="100%">
                <Text mb="8px" wordBreak={"break-all"}>
                  {inputItem.name}
                  {` [${inputItem.type}]`}
                </Text>
                {(inputItem.type === "string" ||
                  inputItem.type === "bytes" ||
                  inputItem.type === "uint256" ||
                  inputItem.type === "uint256[]") && (
                  <Input
                    onKeyPress={handleKeypress}
                    type="search"
                    key={`argument-string-${inputItem.name}${inputItem.type}`}
                    value={inputItem.meta.value}
                    onChange={(event) =>
                      dispatchArguments({
                        value: event.target.value,
                        index,
                      })
                    }
                    placeholder={
                      inputItem.meta.placeholder ||
                      inputItem.name ||
                      inputItem.type
                    }
                    size="sm"
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                  />
                )}
                {inputItem.type === "address" && (
                  <Input
                    onKeyPress={handleKeypress}
                    type="search"
                    placeholder={
                      inputItem.meta.placeholder ||
                      inputItem.name ||
                      inputItem.type
                    }
                    key={`argument-address-${inputItem.name}`}
                    value={inputItem.meta.value}
                    onChange={(event) =>
                      dispatchArguments({
                        value: event.target.value,
                        index,
                      })
                    }
                    size="sm"
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                  />
                )}
              </Box>
            );
          }
        })}
        <Flex direction={"row"} flexWrap="wrap">
          <Button
            variant={"solid"}
            colorScheme={"orange"}
            size="sm"
            onClick={handleSubmit}
            isLoading={tx.isLoading}
          >
            Submit
          </Button>
          {onCancel && (
            <Button
              variant={"solid"}
              colorScheme={"orange"}
              size="sm"
              onClick={() => handleClose()}
            >
              Cancel
            </Button>
          )}
        </Flex>
      </Stack>
    </Fade>
  );
};

export default chakra(Web3MethodForm);
