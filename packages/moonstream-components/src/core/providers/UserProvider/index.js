import React, { useState, useEffect, useCallback } from "react";
import http from "axios";
import UserContext from "./context";
import { AUTH_URL } from "../../services/auth.service";
import { IS_AUTHENTICATION_REQUIRED } from "../../constants";
import { v4 } from "uuid";
const UserProvider = ({ children }) => {
  const [user, setUser] = useState();
  const [isInit, setInit] = useState(false);

  const getUser = useCallback(() => {
    const token = localStorage.getItem("APP_ACCESS_TOKEN");
    if (!token) {
      setInit(true);
      return setUser(null);
    }

    if (IS_AUTHENTICATION_REQUIRED) {
      const headers = { Authorization: `Bearer ${token}` };
      http
        .get(`${AUTH_URL}/`, { headers })
        .then((response) => {
          setUser(response.data);
        })
        .catch(() => setUser(null))
        .finally(() => setInit(true));
    } else {
      let user_id = localStorage.getItem("user_id");
      if (!user_id) {
        user_id = v4();
        localStorage.setItem("user_id", user_id);
      }
      setUser({ username: "anonymous", user_id: user_id });
      setInit(true);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    if (isMounted) {
      getUser();
    }
    return () => {
      isMounted = false;
    };
  }, [getUser]);

  return (
    <UserContext.Provider value={{ isInit, user, setUser, getUser }}>
      {children}
    </UserContext.Provider>
  );
};

export default UserProvider;
