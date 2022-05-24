import { useQuery } from "react-query";
import { getClaimSignature } from "../../services/moonstream-engine.service";
import { queryCacheProps } from "../hookCommon";

const useClaimant = ({ dropId, claimantAddress }) => {
  const claim = useQuery(
    ["claim", dropId, claimantAddress],
    async () => {
      const result = await getClaimSignature(dropId, claimantAddress);
      return result.data;
    },
    {
      ...queryCacheProps,
      cacheTime: 0,
      enabled: !!dropId && !!claimantAddress,
    }
  );

  return { claim };
};

export default useClaimant;
