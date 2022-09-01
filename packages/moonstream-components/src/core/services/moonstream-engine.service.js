import { http } from "../utils";
const API =
  process.env.NEXT_PUBLIC_ENGINE_API_URL ??
  process.env.NEXT_PUBLIC_PLAY_API_URL;

const PLAY_API = `${API}/play`;
const ADMIN_API = `${API}/admin`;

export const getAdminList =
  (terminusAddress, chainName, poolId, offset, limit, dropperAddress) =>
  async () => {
    return http({
      method: "GET",
      url: `${ADMIN_API}/drops`,
      params: {
        blockchain: chainName,
        contract_address: dropperAddress,
        terminus_address: encodeURIComponent(terminusAddress),
        terminus_pool_id: poolId,
        limit: limit,
        offset: offset,
      },
    });
  };

export const getClaimSignature = ({ claimId, address }) => {
  return http({
    method: "GET",
    url: `${PLAY_API}/claims/${claimId}`,
    params: { address: address },
  });
};

export const createDropperClaim =
  ({ dropperContractAddress }) =>
  async ({ title, description, deadline, terminusAddress, terminusPoolId }) => {
    const data = new FormData();
    data.append("dropper_contract_address", dropperContractAddress);
    data.append("title", title);
    data.append("description", description);
    data.append("claim_block_deadline", deadline);
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
      url: `${ADMIN_API}/drops/${encodeURIComponent(dropperClaimId)}/claimants`,
      params: {
        offset: encodeURIComponent(offset),
        limit: encodeURIComponent(limit),
      },
    }).then((response) => {
      response.data.claimants.map((claimant) => {
        claimant.amount = claimant.raw_amount || claimant.amount;
      });
      return response;
    });
  };

export const setClaimants = ({ dropperClaimId, claimants }) => {
  const data = { claimants: claimants };

  return http({
    method: "POST",
    url: `${ADMIN_API}/drops/${dropperClaimId}/claimants/batch`,
    data: data,
  });
};

export const deleteClaimants =
  ({ dropperClaimId }) =>
  ({ list }) => {
    return http({
      method: "DELETE",
      url: `${ADMIN_API}/drops/${dropperClaimId}/claimants`,
      data: { claimants: list },
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
    url: `${PLAY_API}/terminus`,
    params: { blockchain: chainName },
  });
};

export const deactivate = ({ dropperClaimId }) => {
  return http({
    method: "PUT",
    url: `${ADMIN_API}/drops/${dropperClaimId}/deactivate`,
  });
};

export const activate = ({ dropperClaimId }) => {
  return http({
    method: "PUT",
    url: `${ADMIN_API}/drops/${dropperClaimId}/activate`,
  });
};
