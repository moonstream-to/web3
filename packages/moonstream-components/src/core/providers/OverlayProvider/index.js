import React, { useState, useLayoutEffect, Suspense } from "react";
import OverlayContext from "./context";
import { MODAL_TYPES, DRAWER_TYPES } from "./constants";
import {
  Modal,
  ModalOverlay,
  ModalCloseButton,
  ModalBody,
  ModalContent,
  useDisclosure,
  ModalHeader,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Button,
  Spinner,
  Divider,
} from "@chakra-ui/react";
const HubspotForm = React.lazy(() => import("../../../components/HubspotForm"));
const FileUpload = React.lazy(() => import("../../../components/FileUpload"));
const CSVDiff = React.lazy(() => import("../../../components/CSVDiff"));

const OverlayProvider = ({ children }) => {
  const [modal, toggleModal] = useState({
    type: MODAL_TYPES.OFF,
    props: undefined,
  });
  const [drawer, toggleDrawer] = useState(DRAWER_TYPES.OFF);
  const [alertCallback, setAlertCallback] = useState(null);
  const drawerDisclosure = useDisclosure();
  const modalDisclosure = useDisclosure();
  const alertDisclosure = useDisclosure();

  useLayoutEffect(() => {
    if (modal.type === MODAL_TYPES.OFF && modalDisclosure.isOpen) {
      modalDisclosure.onClose();
    } else if (modal.type !== MODAL_TYPES.OFF && !modalDisclosure.isOpen) {
      modalDisclosure.onOpen();
    }
  }, [modal.type, modalDisclosure]);

  useLayoutEffect(() => {
    if (drawer === DRAWER_TYPES.OFF && drawerDisclosure.isOpen) {
      drawerDisclosure.onClose();
    } else if (drawer !== DRAWER_TYPES.OFF && !drawerDisclosure.isOpen) {
      drawerDisclosure.onOpen();
    }
  }, [drawer, drawerDisclosure]);

  const handleAlertConfirm = () => {
    alertCallback && alertCallback();
    alertDisclosure.onClose();
  };

  const toggleAlert = (callback) => {
    setAlertCallback(() => callback);
    alertDisclosure.onOpen();
  };

  console.assert(
    Object.values(DRAWER_TYPES).some((element) => element === drawer)
  );
  console.assert(
    Object.values(MODAL_TYPES).some((element) => element === modal.type)
  );

  const cancelRef = React.useRef();

  return (
    <OverlayContext.Provider
      value={{ modal, toggleModal, drawer, toggleDrawer, toggleAlert }}
    >
      <AlertDialog
        isOpen={alertDisclosure.isOpen}
        leastDestructiveRef={cancelRef}
        // onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Cancel
            </AlertDialogHeader>

            <AlertDialogBody>Are you sure you want to cancel?</AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={() => alertDisclosure.onClose()}>
                Cancel
              </Button>
              <Button
                colorScheme="red"
                ml={3}
                onClick={() => {
                  handleAlertConfirm();
                }}
              >
                Confirm
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>

      <Modal
        isOpen={modalDisclosure.isOpen}
        onClose={() => toggleModal({ type: MODAL_TYPES.OFF })}
        size="2xl"
        scrollBehavior="outside"
        trapFocus={false}
        bgColor="white.100"
      >
        <ModalOverlay />

        <ModalContent
          borderRadius={modal.type === MODAL_TYPES.CSV_DIFF ? "148px" : "148px"}
          bgColor={
            modal.type === MODAL_TYPES.CSV_DIFF ? "transparent" : "red.100"
          }
          w="full"
          maxW={modal.type === MODAL_TYPES.CSV_DIFF ? "100%" : undefined}
          mx={modal.type === MODAL_TYPES.CSV_DIFF ? "20px" : undefined}
        >
          <ModalHeader
            bgColor="orange.900"
            textColor="white.300"
            py={2}
            fontSize="lg"
            borderTopRadius="48px"
            h="96px"
            boxShadow={"lg"}
            textAlign={"center"}
          >
            {modal.type === MODAL_TYPES.CSV_DIFF && "Review diff"}
            {modal.type === MODAL_TYPES.FILE_UPLOAD && `Upload new csv file`}
          </ModalHeader>
          {modal.type !== MODAL_TYPES.FILL_BOTTLE &&
            modal.type !== MODAL_TYPES.POUR_BOTTLE && <Divider />}
          <ModalCloseButton mr={2} />
          <ModalBody
            zIndex={100002}
            bgColor={"white.300"}
            borderBottomRadius={"48px"}
            maxW={modal.type === MODAL_TYPES.CSV_DIFF ? "100%" : undefined}
            // w="100vw"
            maxH={modal.type === MODAL_TYPES.CSV_DIFF ? "70vh" : "0px"}
            overflowY={"hidden"}
            px={"48px"}
          >
            <Suspense fallback={<Spinner />}>
              {modal.type === MODAL_TYPES.HUBSPOT && (
                <HubspotForm
                  toggleModal={toggleModal}
                  title={"Join the waitlist"}
                  formId={"1897f4a1-3a00-475b-9bd5-5ca2725bd720"}
                />
              )}
              {modal.type === MODAL_TYPES.FILE_UPLOAD && (
                <FileUpload toggleModal={toggleModal} />
              )}
              {modal.type === MODAL_TYPES.CSV_DIFF && (
                <CSVDiff toggleModal={toggleModal} {...modal.props} />
              )}
            </Suspense>
          </ModalBody>
        </ModalContent>
      </Modal>
      {children}
    </OverlayContext.Provider>
  );
};

export default OverlayProvider;
