import React, {
  useState,
  useContext,
  useEffect,
  useCallback,
  useLayoutEffect,
} from "react";
import { useBreakpointValue } from "@chakra-ui/react";
import { useStorage, useQuery, useRouter } from "../../hooks";
import UIContext from "./context";
import UserContext from "../UserProvider/context";
import { v4 as uuid4 } from "uuid";

//TODO: onboardingSteps must be made either generic for any APP, or removed at all for now
const onboardingSteps = [
  {
    step: "welcome",
    description: "Basics of how Moonstream works",
  },
  {
    step: "subscriptions",
    description: "Learn how to subscribe to blockchain events",
  },
  {
    step: "stream",
    description: "Learn how to use your Moonstream to analyze blah blah blah",
  },
];

const UIProvider = ({ children }) => {
  const router = useRouter();
  const { user, isInit } = useContext(UserContext);
  const isMobileView = useBreakpointValue({
    base: true,
    sm: true,
    md: false,
    lg: false,
    xl: false,
    "2xl": false,
  });
  // const isMobileView = true;

  const [searchTerm, setSearchTerm] = useQuery("q", "", true, false);

  const [searchBarActive, setSearchBarActive] = useState(false);

  // ****** Session state *****
  // Whether sidebar should be toggled in mobile view
  const [sessionId] = useStorage(window.sessionStorage, "sessionID", uuid4());

  // ******* APP state ********
  const [isLoggedIn, setLoggedIn] = useState(user && user.username);
  const [isLoggingOut, setLoggingOut] = useState(false);
  const [isLoggingIn, setLoggingIn] = useState(false);
  const [isAppReady, setAppReady] = useState(false);
  const [isAppView, setAppView] = useState(false);

  useEffect(() => {
    if (isLoggingOut && !isAppView && user) {
      setLoggingOut(false);
    }
  }, [isAppView, user, isLoggingOut]);

  useEffect(() => {
    if (user && user.username) {
      setLoggedIn(true);
    } else {
      setLoggedIn(false);
    }
  }, [user]);

  useLayoutEffect(() => {
    if (
      isLoggingOut &&
      router.nextRouter.pathname === "/" &&
      !user &&
      !localStorage.getItem("APP_ACCESS_TOKEN")
    ) {
      setLoggingOut(false);
    }
  }, [isLoggingOut, router.nextRouter.pathname, user]);

  // *********** Sidebar states **********************

  // Whether sidebar should be visible at all or hidden
  const [sidebarVisible, setSidebarVisible] = useStorage(
    window.sessionStorage,
    "sidebarVisible",
    true
  );
  // Whether sidebar should be smaller state
  const [sidebarCollapsed, setSidebarCollapsed] = useStorage(
    window.sessionStorage,
    "sidebarCollapsed",
    false
  );

  // Whether sidebar should be toggled in mobile view
  const [sidebarToggled, setSidebarToggled] = useStorage(
    window.sessionStorage,
    "sidebarToggled",
    false
  );

  //Sidebar is visible at all times in mobile view
  useEffect(() => {
    if (isMobileView) {
      setSidebarVisible(true);
      setSidebarCollapsed(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMobileView]);

  //Sidebar is visible at at breakpoint value less then 2
  //Sidebar is visible always in appView
  useEffect(() => {
    if (isMobileView) {
      setSidebarVisible(true);
      setSidebarCollapsed(false);
    } else {
      if (!isAppView) {
        setSidebarVisible(false);
      } else {
        setSidebarVisible(true);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMobileView, isAppView]);

  // *********** Entries layout states **********************

  //
  // const [entryId, setEntryId] = useState();
  // Current transaction to show in sideview
  const [currentTransaction, _setCurrentTransaction] = useState(undefined);
  const [isEntryDetailView, setEntryDetailView] = useState(false);

  const setCurrentTransaction = (tx) => {
    _setCurrentTransaction(tx);
    setEntryDetailView(!!tx);
  };

  /**
   * States that entries list box should be expanded
   * Default true in mobile mode and false in desktop mode
   */
  const [entriesViewMode, setEntriesViewMode] = useState(
    isMobileView ? "list" : "split"
  );

  useEffect(() => {
    setEntriesViewMode(
      isMobileView ? (isEntryDetailView ? "entry" : "list") : "split"
    );
  }, [isEntryDetailView, isMobileView]);

  useEffect(() => {
    if (isInit && router.nextRouter.isReady && !isLoggingOut && !isLoggingIn) {
      setAppReady(true);
    } else {
      setAppReady(false);
    }
  }, [isInit, router, isLoggingOut, isLoggingIn]);

  //***************Overlay's states  ************************/
  // const [newDashboardForm, setNewDashboardForm] = useStorage(
  //   window.sessionStorage,
  //   "newDashboardForm",
  //   null
  // );
  const [newDashboardForm, setNewDashboardForm] = useState();

  return (
    <UIContext.Provider
      value={{
        sidebarVisible,
        setSidebarVisible,
        searchBarActive,
        setSearchBarActive,
        isMobileView,
        sidebarCollapsed,
        setSidebarCollapsed,
        sidebarToggled,
        setSidebarToggled,
        searchTerm,
        setSearchTerm,
        isAppView,
        setAppView,
        setLoggingOut,
        isLoggedIn,
        isAppReady,
        entriesViewMode,
        setEntryDetailView,
        sessionId,
        currentTransaction,
        setCurrentTransaction,
        isEntryDetailView,
        isLoggingOut,
        isLoggingIn,
        setLoggingIn,
        newDashboardForm,
        setNewDashboardForm,
      }}
    >
      {children}
    </UIContext.Provider>
  );
};

export default UIProvider;
