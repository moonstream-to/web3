import { http } from "../utils";
const API =
  process.env.NEXT_PUBLIC_ENGINE_API_URL ??
  process.env.NEXT_PUBLIC_PLAY_API_URL;

export const getTerminus = (diamondAddress, chainId) => {
  return http({
    method: "GET",
    url: `${API}/terminus/${chainId}/${diamondAddress}`,
  });
};

export const getPoolState = (DiamondAddress, poolId) => (query) =>
  http({
    method: "GET",
    url: `${API}/terminus/${DiamondAddress}/${poolId}/`,
    params: query,
  });

export const setPoolAddress =
  (DiamondAddress, poolId) =>
  ({ address, allowance, kyc, notes }) => {
    const data = new FormData();
    address && data.append("address", address);
    allowance && data.append("allowance", allowance);
    kyc && data.append("kyc", kyc);
    notes && data.append("kyc", notes);
    return http({
      method: "PUT",
      url: `${API}/terminus/${DiamondAddress}/pools/${poolId}/`,
      data,
    });
  };

export const forceChainSync = (DiamondAddress, poolId) =>
  http({
    method: "GET",
    url: `${API}/terminus/${DiamondAddress}/pools/${poolId}/refresh`,
  });

export const newControllerAccessToken =
  (DiamondAddress, poolId) => (signature) => {
    const data = new FormData();
    data.append("signature", signature);
    return http({
      method: "POST",
      url: `${API}/terminus/${DiamondAddress}/pools/${poolId}/token`,
      data,
    });
  };

export const authWithAddress = (DiamondAddress, poolId) =>
  http({
    method: "GET",
    url: `${API}/terminus/${DiamondAddress}/pools/${poolId}/auth/quest`,
  });

export const getweb3Auth = (address, chainId) =>
  http({
    method: "GET",
    url: `${API}/web3auth/${chainId}/${address}/`,
  });

export const postweb3Auth = (address, chainId) => (signature) => {
  const data = new FormData();
  data.append("signature", signature);
  return http({
    method: "POST",
    url: `${API}/web3auth/${chainId}/${address}/`,
    data,
  });
};
