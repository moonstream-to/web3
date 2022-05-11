import React, { Fragment } from "react";
import {
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverCloseButton,
  PopoverHeader,
  PopoverFooter,
  PopoverBody,
  Button,
} from "@chakra-ui/react";

// title="Please confirm"
//                   confirmLabel="confirm"
//                   cancelLabel="cancel"
//                   description="This will delete claimant form the list"
const ConfirmationRequest = (props) => {
  return (
    <Popover>
      {({ onClose }) => (
        <Fragment>
          <PopoverTrigger>{props.children}</PopoverTrigger>
          <PopoverContent zIndex={100} bg="blue.900">
            <PopoverCloseButton />
            <PopoverHeader fontWeight="bold">{props.header}</PopoverHeader>
            <PopoverBody fontSize="md">{props.bodyMessage}</PopoverBody>
            <PopoverFooter>
              <Button
                onClick={() => {
                  props.onConfirm();
                  onClose();
                }}
                colorScheme="red"
                variant="outline"
                size="sm"
              >
                {props.confirmLabel ?? "Confirm"}
              </Button>
              <Button
                onClick={onClose}
                colorScheme="green"
                variant="solid"
                size="sm"
              >
                {props.cancelLabel ?? "Cancel"}
              </Button>
            </PopoverFooter>
          </PopoverContent>
        </Fragment>
      )}
    </Popover>
  );
};

export default ConfirmationRequest;
