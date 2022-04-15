import { http } from "../utils";
const API = process.env.NEXT_PUBLIC_APP_API_URL;

export const getDropList = (dropper, claimId) => async () =>
  http({
    method: "GET",
    url: `${API}/drops/search`,
    params: { dropper_address: dropper, claimId: claimId },
  });

export const getDropMessage = (claimId) => async (address) =>
  http({
    method: "GET",
    url: `${API}/drops/`,
    params: { address: address, claim_id: claimId },
  });
