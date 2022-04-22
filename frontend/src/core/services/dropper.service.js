import { http } from "../utils";
const API = process.env.NEXT_PUBLIC_APP_API_URL;

export const getDropList =
  (dropper_contract_id, blockchain, address) => async () =>
    http({
      method: "GET",
      url: `${API}/drops/claims`,
      params: {
        dropper_contract_id: dropper_contract_id,
        blockchain: blockchain,
        address: address,
      },
    });

export const getDropMessage = (dropperClaimId) => async (address) =>
  http({
    method: "GET",
    url: `${API}/drops/`,
    params: { address: address, dropper_claim_id: dropperClaimId },
  });
