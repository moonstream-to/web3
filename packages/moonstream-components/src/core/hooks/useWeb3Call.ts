import { AbiItem } from "web3-utils";
import { MoonstreamWeb3ProviderInterface } from "../../../../../types/Moonstream";
import useToast from "./useToast";
import { useMutation } from "react-query";

const useWeb3Call = ({
  ctx,

  contractAddress,
}: {
  ctx: MoonstreamWeb3ProviderInterface;

  contractAddress: string;
}) => {
  const toast = useToast();

  const web3call = async ({ method, args }: { method: AbiItem; args: any }) => {
    const contract = new ctx.web3.eth.Contract([method]);

    contract.options.address = contractAddress;
    const response =
      method.name &&
      (await contract.methods[method.name](...args).send({
        from: ctx.account,
        gasPrice: "1",
      }));
    return response;
  };
  const tx = useMutation(
    ({ method, args }: { method: AbiItem; args: any }) =>
      web3call({ method, args }),
    {
      onSuccess: () => {
        toast("Transaction went to the moon!", "success");
      },
      onError: () => {
        toast("Transaction failed >.<", "error");
      },
    }
  );

  return tx;
};

export default useWeb3Call;
