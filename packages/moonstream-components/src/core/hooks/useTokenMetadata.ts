import { useQuery } from "react-query";

const useTokenMetadata = ({ tokenURI }: { tokenURI: string }) => {
  const metadata = useQuery(
    ["TokenMetadata", tokenURI],
    () => fetch(tokenURI).then((res) => res.json()),
    {
      onSuccess: () => {},
    }
  );

  return {
    metadata,
  };
};

export default useTokenMetadata;
