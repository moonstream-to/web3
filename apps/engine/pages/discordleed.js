import React from "react";
import { useRouter } from "moonstream-components/src/core/hooks";

const DiscordLeed = () => {
  console.log("disc");
  const router = useRouter();

  React.useLayoutEffect(() => {
    router.push("https://discord.gg/K56VNUQGvA");
  }, [router]);

  return <></>;
};

export default DiscordLeed;
