import { http } from "../utils";
const API = process.env.NEXT_PUBLIC_APP_API_URL;

export const getContracts = () => async () => {
  return http({
    method: "GET",
    url: `${API}/drops/contracts`,
  });
};

export const getDropList =
  (dropperAddress, chainName, ctx) => async (address) => {
    console.log("getDropList");
    return http({
      method: "GET",
      url: `${API}/drops/claims`,
      params: {
        dropper_contract_address: encodeURIComponent(dropperAddress),
        blockchain: chainName,
        claimant_address: address,
      },
    });
  };

export const getAdminList =
  (terminusAddress, chainName, poolId) => async () => {
    return http({
      method: "GET",
      url: `${API}/drops/terminus/claims`,
      params: {
        terminus_address: encodeURIComponent(terminusAddress),
        blockchain: chainName,
        terminus_pool_id: poolId,
      },
    });
  };

export const getDropMessage = (claimId) => async (address) =>
  http({
    method: "GET",
    url: `${API}/drops/`,
    params: { address: address, dropper_claim_id: claimId },
  });

export const createDropperClaim =
  ({ dropperContractAddress }, ctx) =>
  async ({ title, description, deadline, terminusAddress, terminusPoolId }) => {
    const data = new FormData();
    data.append("dropper_contract_address", dropperContractAddress);
    data.append("chain_id", chain_id);
    data.append("title", title);
    data.append("description", description);
    data.append("claim_block_deadline", deadline);
    data.append("claim_id", claim_id);
    terminusAddress && data.append("terminus_address", terminusAddress);
    terminusPoolId && data.append("terminus_pool_id", terminusPoolId);

    return http({
      method: "POST",
      url: `${API}/drops/claims`,
      data: data,
    });
  };

export const getClaimants =
  ({ dropperClaimId }) =>
  ({ limit, offset }) => {
    return http({
      method: "GET",
      url: `${API}/claimants`,
      params: {
        dropper_claim_id: encodeURIComponent(dropperClaimId),
        offset: encodeURIComponent(offset),
        limit: encodeURIComponent(limit),
      },
    });
  };

export const setClaimants = ({ dropperClaimId, claimants }) => {
  console.log("setClaimants", dropperClaimId, claimants);
  // const data = new FormData();
  // data.append("dropper_claim_id", dropperClaimId);
  // data.append("claimants", claimants);
  const data = { dropper_claim_id: dropperClaimId, claimants: claimants };

  return http({
    method: "POST",
    url: `${API}/drops/claimants`,
    data: data,
  });
};

export const deleteClaimants =
  ({ dropperClaimId }) =>
  async (addresses) => {
    const data = new FormData();
    data.append("dropper_claim_id", dropperClaimId);
    data.append("addresses", addresses);

    return http({
      method: "DELETE",
      url: `${API}/drops/claimants`,
      data: data,
    });
  };

export const getTime = () => async () => {
  return http({
    method: "GET",
    url: `${API}/now`,
  });
};

export const getTerminus = (chainName) => async () => {
  return http({
    method: "GET",
    url: `${API}/drops/terminus`,
    params: { blockchain: chainName },
  });
};
