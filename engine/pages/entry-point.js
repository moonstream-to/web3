//Use this page to redirect from s3 error routes to ensure app can be entered from non statically generated routes correctly
import { useRouter } from "next/router";
import { useContext, useLayoutEffect } from "react";
import UserContext from "../../packages/moonstream-components/src/core/providers/UserProvider/context";
import { getLayout } from "../../packages/moonstream-components/src/layouts/EntryPointLayout";
const EntryPoint = () => {
  const router = useRouter();
  const { isInit } = useContext(UserContext);
  useLayoutEffect(() => {
    if (router.isReady && isInit && router.asPath !== router.pathname + `/`) {
      if (localStorage.getItem("entry_point")) {
        router.replace("/404", router.asPath);
      } else {
        localStorage.setItem("entry_point", 1);
        router.replace(router.asPath, undefined, {
          shallow: true,
        });
      }
    }
  }, [router, isInit]);

  return "";
};

EntryPoint.getLayout = getLayout;

export default EntryPoint;
