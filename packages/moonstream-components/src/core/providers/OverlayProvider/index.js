import React, { useState, useLayoutEffect, useContext, Suspense } from "react";
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
import UserContext from "../UserProvider/context";
import UIContext from "../UIProvider/context";
import SignUp from "../../../components/SignUp";
const ForgotPassword = React.lazy(() =>
  import("../../../components/ForgotPassword")
);
const SignIn = React.lazy(() => import("../../../components/SignIn"));
const HubspotForm = React.lazy(() => import("../../../components/HubspotForm"));
const NewSubscription = React.lazy(() =>
  import("../../../components/NewSubscription")
);

const OverlayProvider = ({ children }) => {
  const ui = useContext(UIContext);
  const { user } = useContext(UserContext);
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

  useLayoutEffect(() => {
    if (
      ui.isAppView &&
      ui.isInit &&
      !user?.username &&
      !ui.isLoggingOut &&
      !ui.isLoggingIn &&
      !modal.type
    ) {
      toggleModal({ type: MODAL_TYPES.LOGIN });
    } else if (user && ui.isLoggingOut) {
      toggleModal({ type: MODAL_TYPES.OFF });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ui.isAppView, ui.isAppReady, user, ui.isLoggingOut, modal.type]);

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
      >
        <ModalOverlay />

        <ModalContent borderRadius="48px" bgColor="purple.900">
          <ModalHeader
            bgColor="pink.900"
            textColor="white.300"
            py={2}
            fontSize="lg"
            borderTopRadius="48px"
            h="96px"
            boxShadow={"lg"}
            textAlign={"center"}
          >
            {modal.type === MODAL_TYPES.NEW_SUBSCRIPTON &&
              "Subscribe to a new address"}
            {modal.type === MODAL_TYPES.FORGOT && "Forgot Password"}
            {modal.type === MODAL_TYPES.HUBSPOT && "Join the waitlist"}
            {modal.type === MODAL_TYPES.LOGIN && "Login now"}
            {modal.type === MODAL_TYPES.SIGNUP && "Create an account"}
            {modal.type === MODAL_TYPES.UPLOAD_ABI && "Assign ABI"}
            {modal.type === MODAL_TYPES.FILL_BOTTLE &&
              `Fill ${modal.props.bottle.name} bottles with UNIM`}
            {modal.type === MODAL_TYPES.POUR_BOTTLE &&
              `Open ${modal.props.bottle.name} bottles to extract UNIM`}
          </ModalHeader>
          {modal.type !== MODAL_TYPES.FILL_BOTTLE &&
            modal.type !== MODAL_TYPES.POUR_BOTTLE && <Divider />}
          <ModalCloseButton mr={2} />
          <ModalBody
            zIndex={100002}
            bgColor={
              modal.type === MODAL_TYPES.UPLOAD_ABI ? "white.200" : undefined
            }
            borderRadius="148px"
          >
            <Suspense fallback={<Spinner />}>
              {modal.type === MODAL_TYPES.NEW_SUBSCRIPTON && (
                <NewSubscription
                  onClose={() => toggleModal({ type: MODAL_TYPES.OFF })}
                  isModal={true}
                  {...modal.props}
                />
              )}
              {modal.type === MODAL_TYPES.FORGOT && <ForgotPassword />}
              {modal.type === MODAL_TYPES.HUBSPOT && (
                <HubspotForm
                  toggleModal={toggleModal}
                  title={"Join the waitlist"}
                  formId={"1897f4a1-3a00-475b-9bd5-5ca2725bd720"}
                />
              )}
              {modal.type === MODAL_TYPES.LOGIN && (
                <SignIn toggleModal={toggleModal} />
              )}
              {modal.type === MODAL_TYPES.SIGNUP && (
                <SignUp toggleModal={toggleModal} />
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
