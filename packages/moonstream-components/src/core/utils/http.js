import enableMockupRequests from "./mockupRequests";
let axios = require("axios");
const API =
  process.env.NEXT_PUBLIC_ENGINE_API_URL ??
  process.env.NEXT_PUBLIC_PLAY_API_URL;
process.env.NODE_ENV !== "production" && enableMockupRequests(axios);

const http = (config, noAuth = false) => {
  const token = localStorage.getItem("APP_ACCESS_TOKEN");
  const authorization = token && !noAuth ? { Authorization: `Moonstream ${token}` } : {};
  const defaultHeaders = config.headers ?? {};
  const options = {
    ...config,
    headers: {
      ...defaultHeaders,
      ...authorization,
    },
  };

  return axios(options);
};

export const queryPublic = (uri) => {
  return axios({ method: "GET", url: uri });
};

export const putHttp = (endpoint, data) => {
  return http({
    method: "PUT",
    url: `${API}${endpoint}`,
    data: data,
  });
};

export const queryHttp = (query) => {
  const _query = query.queryKey.length >= 1 ? query.queryKey[1] : undefined;
  return http({
    method: "GET",
    url: `${API}${query.queryKey[0]}`,
    params: { ..._query },
  });
};

export const patchHttp = (endpoint, data) => {
  return http({
    method: "PATCH",
    url: `${API}${endpoint}`,
    data: data,
  });
};

export { axios };
export default http;
