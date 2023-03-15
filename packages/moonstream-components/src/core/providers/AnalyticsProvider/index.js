import React, { useContext, useEffect, useState } from "react";
import mixpanel from "mixpanel-browser";
import AnalyticsContext from "./context";
import { useClientID, useRouter } from "../../hooks";
import { MIXPANEL_EVENTS, MIXPANEL_PROPS } from "./constants";
import UIContext from "../UIProvider/context";

const AnalyticsProvider = ({ children, mixpanelToken }) => {
  const clientID = useClientID();
  const [isMixpanelReady, setIsLoaded] = useState(false);
  const router = useRouter();
  const ui = useContext(UIContext);

  // ********** OBOARDING STATE **************
  useEffect(() => {
    if (ui.onboardingState && isMixpanelReady) {
      mixpanel.people.set(MIXPANEL_EVENTS.ONBOARDING_STATE, {
        state: { ...ui.onboardingState },
      });
    }
  }, [ui.onboardingState, isMixpanelReady]);

  // ********** ONBOARDING STEP and TIMING **************
  const [previousOnboardingStep, setPreviousOnboardingStep] = useState(false);

  useEffect(() => {
    if (isMixpanelReady && router.nextRouter.pathname === "/welcome") {
      if (!previousOnboardingStep) {
        mixpanel.time_event(MIXPANEL_EVENTS.ONBOARDING_STEP);
        setPreviousOnboardingStep(ui.onboardingStep);
      }
      if (
        previousOnboardingStep &&
        previousOnboardingStep !== ui.onboardingStep
      ) {
        mixpanel.track(MIXPANEL_EVENTS.ONBOARDING_STEP, {
          step: previousOnboardingStep,
          isBeforeUnload: false,
        });
        setPreviousOnboardingStep(false);
      }
    } else if (previousOnboardingStep) {
      mixpanel.track(MIXPANEL_EVENTS.ONBOARDING_STEP, {
        step: previousOnboardingStep,
        isBeforeUnload: false,
      });
      setPreviousOnboardingStep(false);
    }
  }, [
    previousOnboardingStep,
    ui.onboardingStep,
    isMixpanelReady,
    router.nextRouter.pathname,
  ]);

  // ********** PING_PONG **************
  useEffect(() => {
    let durationSeconds = 0;

    const intervalId =
      isMixpanelReady &&
      setInterval(() => {
        durationSeconds = durationSeconds + 30;
        mixpanel.track(
          MIXPANEL_EVENTS.BEACON,
          {
            duration_seconds: durationSeconds,
            url: router.nextRouter.pathname,
          },
          { transport: "sendBeacon" }
        );
      }, 30000);

    return () => clearInterval(intervalId);
  }, [isMixpanelReady, router.nextRouter.pathname]);

  // ********** TIME SPENT ON PATH**************

  const [previousPathname, setPreviousPathname] = useState(false);

  useEffect(() => {
    if (isMixpanelReady) {
      if (!previousPathname) {
        mixpanel.time_event(MIXPANEL_EVENTS.PAGEVIEW_DURATION);
        setPreviousPathname(router.nextRouter.pathname);
      }
      if (previousPathname && previousPathname !== router.nextRouter.pathname) {
        mixpanel.track(MIXPANEL_EVENTS.PAGEVIEW_DURATION, {
          url: previousPathname,
          isBeforeUnload: false,
        });
        setPreviousPathname(false);
      }
    }
  }, [router.nextRouter.pathname, previousPathname, isMixpanelReady]);

  // ********** PAGES VIEW  **************
  useEffect(() => {
    if (isMixpanelReady && ui.sessionId && router.nextRouter.pathname) {
      mixpanel.track(MIXPANEL_EVENTS.PAGEVIEW, {
        url: router.nextRouter.pathname,
        sessionID: ui.sessionId,
      });

      mixpanel.people.increment([
        `${MIXPANEL_EVENTS.TIMES_VISITED} ${router.nextRouter.pathname}`,
      ]);
    }
    const urlForUnmount = router.nextRouter.pathname;
    const closeListener = () => {
      try {
        mixpanel?.track(MIXPANEL_EVENTS.PAGEVIEW_DURATION, {
          url: urlForUnmount,
          isBeforeUnload: true,
        });
      } catch (error) {
        console.log("mixpanel track failed:", error);
      }
    };
    window.addEventListener("beforeunload", closeListener);
    //cleanup function fires on useEffect unmount
    //https://reactjs.org/docs/hooks-effect.html
    return () => {
      window.removeEventListener("beforeunload", closeListener);
    };
  }, [router.nextRouter.pathname, isMixpanelReady, ui.sessionId]);

  // ********** SESSION STATE **************
  useEffect(() => {
    if (clientID) {
      try {
        mixpanel.init(mixpanelToken, {
          api_host: "https://api.mixpanel.com",
          loaded: () => {
            setIsLoaded(true);
            mixpanel.identify(clientID);
          },
        });
      } catch (error) {
        console.warn("loading mixpanel failed:", error);
      }
    }
  }, [mixpanelToken, clientID]);

  useEffect(() => {
    isMixpanelReady && mixpanel.register("sessionId", ui.sessionId);
  }, [ui.sessionId, isMixpanelReady]);

  useEffect(() => {
    if (isMixpanelReady && ui.isLoggingOut) {
      mixpanel.track(`${MIXPANEL_EVENTS.USER_LOGS_OUT}`, {});
    }
  }, [ui.isLoggingOut, isMixpanelReady]);

  return (
    <AnalyticsContext.Provider
      value={{ mixpanel, isMixpanelReady, MIXPANEL_EVENTS, MIXPANEL_PROPS }}
    >
      {children}
    </AnalyticsContext.Provider>
  );
};

export default AnalyticsProvider;
