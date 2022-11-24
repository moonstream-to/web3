//Use this page to redirect from s3 error routes to ensure app can be entered from non statically generated routes correctly
import { useRouter } from "next/router";
import { useLayoutEffect } from "react";

import { getLayout } from "../../../packages/moonstream-components/src/layoutsForPlay/EntryPointLayout";

const EntryPoint = () => {
  const router = useRouter();

  useLayoutEffect(() => {
    if (router.isReady && router.asPath !== router.pathname + `/`) {
      if (localStorage.getItem("entry_point")) {
        router.replace("/404", router.asPath);
      } else {
        localStorage.setItem("entry_point", 1);
        router.replace(router.asPath, undefined, {
          shallow: true,
        });
      }
    }
  }, [router]);

  return "";
};

EntryPoint.getLayout = getLayout;

export default EntryPoint;
