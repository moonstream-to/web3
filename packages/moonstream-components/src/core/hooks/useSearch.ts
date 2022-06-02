import { useQuery } from "react-query";
import queryCacheProps from "./hookCommon";
import { queryHttp } from "../utils/http";

interface queryInterface {
  [key: string]: string;
}

const useSearch = ({
  pathname,
  query,
}: {
  pathname: string;
  query: queryInterface;
}) => {
  const search = useQuery(
    [pathname, { ...query }],
    (_query) => queryHttp(_query).then((r: any) => r.data),

    {
      ...queryCacheProps,
      keepPreviousData: true,
      onSuccess: () => {},
    }
  );

  return {
    search,
  };
};

export default useSearch;
