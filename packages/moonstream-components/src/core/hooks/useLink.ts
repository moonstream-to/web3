import { useQuery } from "react-query";
import { queryPublic } from "../utils/http";
import { hookCommon } from ".";

const useURI = ({ link }: { link: string | undefined }) => {
  const contents = useQuery(
    ["link", link],
    (query: any) => {
      return queryPublic(query.queryKey[1]).then((r: any) => r.data);
    },
    {
      ...hookCommon,
      enabled: !!link,
    }
  );
  return contents;
};

export default useURI;
