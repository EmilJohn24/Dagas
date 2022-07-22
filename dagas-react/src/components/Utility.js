// General purpose functions

import axios from "axios";

const getItemTypes = () => {
    const url = "/relief/api/item-type/"
    console.log("HTTP GET on Item Type...");
    return axios
      .get(url)
      .then(result => result.data)
      .catch((error) => console.log(error));
  }

  const getCurrentUser = () => {
    const url = "/relief/api/users/current_user/";
    console.log("HTTP GET on current user");
    return axios
        .get(url, {
            "credentials": "include",
            "withCredentials": true
        })
        .then(result => result.data)
        .catch((error) => console.log(error));
  }