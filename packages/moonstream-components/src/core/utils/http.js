import enableMockupRequests from "./mockupRequests";
let axios = require("axios");

process.env.NODE_ENV !== "production" && enableMockupRequests(axios);

const http = (config) => {
  const token = localStorage.getItem("APP_ACCESS_TOKEN");
  const authorization = token ? { Authorization: `Moonstream ${token}` } : {};
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

const API = process.env.NEXT_PUBLIC_ENGINE_API_URL;

export const queryHttp = (query) => {
  const _query = query.queryKey.length >= 1 ? query.queryKey[1] : undefined;
  return http({
    method: "GET",
    url: `${API}${query.queryKey[0]}`,
    params: { ..._query },
  });
};

export { axios };
export default http;
