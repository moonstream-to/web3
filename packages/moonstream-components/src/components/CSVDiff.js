import { Button, ButtonGroup, Spinner, Flex } from "@chakra-ui/react";
import React, { useContext, useState } from "react";
import ReactDiffViewer, { DiffMethod } from "react-diff-viewer";
import useDrop from "../core/hooks/dropper/useDrop";
import useDrops from "../core/hooks/dropper/useDrops";
import Web3Context from "../core/providers/Web3Provider/context";
import { MODAL_TYPES } from "../core/providers/OverlayProvider/constants";

const CSVDiff = ({ toggleModal, dropId, newValue }) => {
  const web3ctx = useContext(Web3Context);
  const { AllClaimants } = useDrop({
    ctx: web3ctx,
    claimId: dropId,
    initialPageSize: 500,
    getAll: true,
  });

  const { uploadFile } = useDrops({
    ctx: web3ctx,
    claimId: dropId,
  });

  React.useEffect(() => {
    if (uploadFile.isSuccess) {
      toggleModal({ type: MODAL_TYPES.OFF });
    }
  }, [uploadFile.isSuccess, toggleModal]);

  const [_newValue, _setNewValue] = useState("");
  const [_oldValue, _setOldValue] = useState("");
  React.useEffect(() => {
    if (AllClaimants.data && !AllClaimants.isLoading) {
      let _value = "";
      AllClaimants?.data?.forEach(
        (element) => (_value += element.address + "," + element.amount + `\n `)
      );
      _setOldValue(_value);
    }
  }, [AllClaimants.isLoading, AllClaimants.data]);

  React.useEffect(() => {
    if (newValue) {
      let _value = "";
      newValue.forEach(
        (element) => (_value += element.address + "," + element.amount + `\n `)
      );
      _setNewValue(_value);
    }
  }, [newValue]);

  if (AllClaimants.isLoading) return <Spinner />;

  return (
    <>
      <Flex
        maxH="50vh"
        overflowY={"scroll"}
        css={{
          "&::-webkit-scrollbar": {
            width: "40px",
          },
          "&::-webkit-scrollbar-track": {
            width: "60px",
          },
          "&::-webkit-scrollbar-thumb": {
            background: 0x1d12ff,
            borderRadius: "24px",
          },
        }}
      >
        <ReactDiffViewer
          oldValue={_oldValue}
          newValue={_newValue}
          splitView={true}
          showDiffOnly={true}
          compareMethod={DiffMethod.LINES}
          styles={{ contentText: { fontSize: "12px" }, scrollY: "scroll" }}
        />
      </Flex>
      <ButtonGroup>
        <Button
          variant={"solid"}
          colorScheme="green"
          isLoading={uploadFile.isLoading}
          onClick={() => {
            uploadFile.mutate({
              dropperClaimId: dropId,
              claimants: newValue,
            });
          }}
        >
          Confirm
        </Button>
        <Button
          variant={"outline"}
          colorScheme="red"
          isLoading={uploadFile.isLoading}
          onClick={() => toggleModal({ type: MODAL_TYPES.OFF })}
        >
          Cancel
        </Button>
      </ButtonGroup>
    </>
  );
};

export default CSVDiff;
