// General purpose functions

import axiosConfig from "../axiosConfig";

export const getItemTypes = () => {
    const url = "/relief/api/item-type/"
    console.log("HTTP GET on Item Type...");
    return axiosConfig
      .get(url)
      .then(result => result.data)
      .catch((error) => console.log(error));
  }

  export const getCurrentUser = async () => {
    const url = "/relief/api/users/current_user/";
    console.log("HTTP GET on current user");
    const data = axiosConfig.get(url).then((result) => {return result});
    return data;
  }