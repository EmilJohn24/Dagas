import axios from 'axios';
import { configure, makeUseAxios } from 'axios-hooks';
import LRU from 'lru-cache';
import { applyAuthTokenInterceptor, resolve } from 'axios-jwt';

const instance = axios.create({
    // baseURL: 'http://192.168.100.2:8000',
    baseURL: 'http://dagas.herokuapp.com',
    withCredentials: true,
    credentials: "include",
    headers: {
        'Content-Type': 'application/json',
    }

});

//TODO: Apply axios JWT here https://www.npmjs.com/package/axios-jwt
// api/token/refresh/
axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';
// instance.defaults.headers.common['Authorization'] = 'AUTH TOKEN FROM INSTANCE';

export const useAxios = makeUseAxios({axios: instance});
// configure({ instance, cache }); 

//Token Refresh Function
const requestRefresh = async (refresh) => {
    const response = await axios.post(`/api/token/refresh/`, { refresh })
      .then(response => response.data.access);
    console.log(response);
    return response;

};

// Apply interceptor
applyAuthTokenInterceptor(instance, { requestRefresh });  // Notice that this uses the axiosInstance instance.  <-- important



export default instance;
