import React, { Fragment } from "react";
import {
  useClipboard,
  IconButton,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverHeader,
  PopoverArrow,
  useDisclosure,
} from "@chakra-ui/react";
import { BiCopy } from "react-icons/bi";

/**
 * @dev if children is text then just wrap it, otherwise pass string as
 * @param text string to put in buffer, overrrides children
 */
const CopyButton = (props) => {
  const children = props.children ? props.children : "";
  const copyString = props.prefix
    ? props.prefix + props.text ?? children
    : props.text ?? children;

  const { onOpen, onClose, isOpen } = useDisclosure();
  const { onCopy } = useClipboard(copyString);
  React.useEffect(() => {
    let timer;
    if (isOpen) {
      timer = setTimeout(() => onClose(), 1000);
    }
    return () => clearTimeout(timer);
  }, [isOpen, onClose]);
  return (
    <Fragment>
      <Popover
        placement="bottom-start"
        returnFocusOnClose={false}
        isOpen={isOpen}
        onClose={onClose}
        onOpen={onOpen}
      >
        <Fragment>
          <PopoverTrigger>
            <IconButton
              onClick={onCopy}
              icon={<BiCopy />}
              colorScheme="orange"
              variant="ghost"
              size="sm"
            />
          </PopoverTrigger>
          <PopoverContent border="none" bgColor="teal.500" width="min-content">
            <PopoverHeader border="none" color="white.100">
              Copied!
            </PopoverHeader>
            <PopoverArrow borderWidth="0" border="none" bgColor="teal.500" />
          </PopoverContent>
        </Fragment>
      </Popover>
      {props.children}
    </Fragment>
  );
};

export default React.memo(CopyButton);
