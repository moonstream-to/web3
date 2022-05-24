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

const API = process.env.NEXT_PUBLIC_ENGINE_API_URL;

export const queryHttp = (query) => {
  return http({
    method: "GET",
    url: `${API}${query.queryKey[0]}`,
    params: { ...query.queryKey[1] },
  });
};

export { axios };
export default http;
