import React, { Fragment, useContext } from "react";
import {
  Flex,
  Button,
  chakra,
  // Fade,
  Input,
  Stack,
  // Text,
  Heading,
  Box,
  Switch,
  FormLabel,
  ThemingProps,
  InputGroup,
} from "@chakra-ui/react";
import { AbiInput, AbiItem } from "web3-utils";
import { useMutation } from "react-query";
import Web3Context from "../core/providers/Web3Provider/context";
import { useToast } from "../core/hooks";
import FileUpload from "./FileUpload";
import Papa from "papaparse";
interface argumentField {
  placeholder?: string;
  initialValue?: string;
  label?: string;
  valueIsEther?: boolean;
  // hide: boolean;
}
interface argumentFields {
  [Key: string]: argumentField;
}

interface extendedInputs extends AbiInput {
  meta?: {
    value: string;
    placeholder: string;
    hide: boolean;
    label: string;
    valueIsEther?: boolean;
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
  key,
  rendered,
  title,
  // onClose,
  onCancel,
  onSuccess,
  beforeSubmit,
  contractAddress,
  BatchInputs,
  className,
  inputsProps,
  ...props
}: {
  title?: string;
  key: string;
  method: AbiItem;
  className?: string;
  argumentFields?: argumentFields;
  hide?: string[];
  BatchInputs?: string[];
  rendered: boolean;
  onClose?: () => void;
  onCancel?: () => void;
  onSuccess?: (resp: any) => void;
  beforeSubmit?: (state: stateInterface) => any;
  contractAddress: string;
  inputsProps?: ThemingProps<"Input">;
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
        label:
          (argumentFields && argumentFields[element.name]?.label) ??
          ` ${element.name}  [${element.type}]`,
        valueIsEther:
          (argumentFields && argumentFields[element.name]?.valueIsEther) ??
          false,
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
    if (onCancel) {
      state.inputs.forEach((inputElement: any, index: any) => {
        dispatchArguments({
          value:
            (argumentFields &&
              argumentFields[inputElement.name]?.initialValue) ??
            "",
          index,
        });
      });
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
        gasPrice:
          process.env.NODE_ENV !== "production" ? "100000000000" : undefined,
      }));
    return response;
  };
  const tx = useMutation(({ args }: { args: any }) => web3call({ args }), {
    onSuccess: (resp) => {
      toast("Transaction went to the moon!", "success");
      onSuccess && onSuccess(resp);
    },
    onError: () => {
      toast("Transaction failed >.<", "error");
    },
  });
  const web3ctx = useContext(Web3Context);
  const handleSubmit = () => {
    const returnedObject: any = [];
    state.inputs.forEach((inputElement: any, index: number) => {
      returnedObject[index] =
        inputElement.type === "address"
          ? web3ctx.web3.utils.isAddress(
              web3ctx.web3.utils.toChecksumAddress(inputElement.meta.value)
            )
            ? web3ctx.web3.utils.toChecksumAddress(inputElement.meta.value)
            : console.error("not an address", returnedObject[index])
          : inputElement.meta.value;
      if (inputElement.type.includes("[]")) {
        returnedObject[index] = JSON.parse(returnedObject[index]);
      }
      if (
        inputElement.type.includes("uint") &&
        inputElement.meta?.valueIsEther
      ) {
        if (inputElement.type.includes("[]")) {
          returnedObject[index] = returnedObject.map((value: string) =>
            web3ctx.web3.utils.toWei(value, "ether")
          );
        } else {
          returnedObject[index] = web3ctx.web3.utils.toWei(
            returnedObject[index],
            "ether"
          );
        }
      }
    });
    beforeSubmit && beforeSubmit(returnedObject);
    console.log("returnedObject", returnedObject);
    tx.mutate({ args: returnedObject });
    // if (onClose) {
    //   onClose();
    // }
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

  const [isUploading, setIsUploading] = React.useState(false);
  const handleParsingError = function (error: string): void {
    setIsUploading(false);
    toast(error, "error", "CSV Parse Error");
    throw error;
  };

  const validateHeader = function (
    headerValue: string,
    column: number
    // expected: string
  ): string {
    const expected = BatchInputs && BatchInputs[column].trim().toLowerCase();
    const header = headerValue.trim().toLowerCase();
    if (column == 0 && header != expected) {
      handleParsingError(
        `First column header must be '${expected}' but got ${headerValue}.`
      );
    }
    if (column == 1 && header != expected) {
      handleParsingError(
        `Second column header must be '${expected}' but got ${headerValue}`
      );
    }
    return header;
  };

  if (!rendered) return <></>;
  return (
    <Stack
      className={className}
      justifyContent="center"
      px={2}
      alignItems="center"
      m={0}
      key={key}
      {...props}
    >
      {/* <Fade in={rendered}> */}
      <Heading
        wordBreak={"break-all"}
        fontSize={
          method?.name?.length && method?.name?.length > 12 ? "xl" : "3xl"
        }
      >
        {title ?? method.name}
      </Heading>
      {state.inputs.map((inputItem: any, index: any) => {
        if (!inputItem.meta.hide && !BatchInputs?.includes(inputItem.name)) {
          return (
            <Box
              key={`${inputItem.name}-${index}-abiitems`}
              w="100%"
              display={inputItem.type === "bool" ? "flex" : "block"}
            >
              {/* <Text mb="8px" wordBreak={"break-all"}>
                {inputItem.name}
                {` [${inputItem.type}]`}
              </Text>*/}
              <FormLabel mb="8px" wordBreak={"break-all"} w="fit-content">
                {inputItem["meta"].label}
              </FormLabel>
              {(inputItem.type === "string" ||
                inputItem.type === "bytes" ||
                inputItem.type === "uint256" ||
                inputItem.type === "uint256[]") && (
                <>
                  {/* <FormLabel mb="8px" wordBreak={"break-all"}>
                    {inputItem.name}
                    {` [${inputItem.type}]`}
                  </FormLabel> */}
                  <InputGroup
                    textColor={"blue.800"}
                    key={`argument-string-${inputItem.name}${inputItem.type}`}
                    size={inputsProps?.size ?? "sm"}
                    fontSize={"sm"}
                    w="100%"
                    variant={"outline"}
                    // colorScheme={"blue"}
                  >
                    <Input
                      type="search"
                      value={inputItem.meta.value}
                      onKeyPress={handleKeypress}
                      placeholder={
                        inputItem.type.includes("[]")
                          ? `[value, value] `
                          : inputItem.meta.placeholder ||
                            inputItem.name ||
                            inputItem.type
                      }
                      onChange={(event) =>
                        dispatchArguments({
                          value: event.target.value,
                          index,
                        })
                      }
                    />
                  </InputGroup>
                </>
              )}
              {(inputItem.type === "address" ||
                inputItem.type === "address[]") && (
                <Input
                  textColor={"blue.800"}
                  onKeyPress={handleKeypress}
                  type="search"
                  placeholder={
                    inputItem.type.includes("[]")
                      ? `[address, address] `
                      : inputItem.meta.placeholder ||
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
                  size={inputsProps?.size ?? "sm"}
                  fontSize={"sm"}
                  w="100%"
                  variant={"outline"}
                />
              )}
              {inputItem.type === "bool" && (
                <Switch
                  display={"inline"}
                  colorScheme="orange"
                  onChange={(e) => {
                    dispatchArguments({
                      value: !e.target.value,
                      index,
                    });
                  }}
                />
              )}
            </Box>
          );
        }
      })}
      {BatchInputs && BatchInputs?.length > 0 && (
        <Flex w="100%" p={0} m={0} flexGrow={1} direction="column">
          <FormLabel mb="8px" wordBreak={"break-all"} w="fit-content">
            Batch:{" "}
            {BatchInputs.map((input, idx) => {
              return `${input}${idx < BatchInputs.length - 1 ? ", " : ""}`;
            })}
          </FormLabel>
          <FileUpload
            w="100%"
            isUploading={isUploading}
            m={0}
            maxW="100%"
            columns={BatchInputs}
            onDrop={(file: any) => {
              Papa.parse(file[0], {
                header: true,
                skipEmptyLines: true,
                fastMode: true,
                transformHeader: validateHeader,
                complete: (result: any) => {
                  BatchInputs.forEach((v) => {
                    const index = state.inputs.findIndex(
                      (item: AbiInput) => item.name === v
                    );
                    dispatchArguments({
                      value: result.data.map(
                        (resultItem: any) =>
                          resultItem[`${v.trim().toLowerCase()}`]
                      ),
                      index,
                    });
                  });
                },
                error: (err: Error) => handleParsingError(err.message),
              });
            }}
          />
        </Flex>
      )}
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
      {/* </Fade> */}
    </Stack>
  );
};

export default chakra(React.memo(Web3MethodForm));
