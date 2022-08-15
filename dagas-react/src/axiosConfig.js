import axios from 'axios';
import { applyAuthTokenInterceptor, resolve } from 'axios-jwt';

const instance = axios.create({
    // baseURL: 'http://192.168.100.2:8000',
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


//Token Refresh Function
const requestRefresh = (refresh) => {
    return axios.post(`/api/token/refresh/`, { refresh })
      .then(response => resolve(response.data.access_token))
};

// Apply interceptor
applyAuthTokenInterceptor(instance, { requestRefresh });  // Notice that this uses the axiosInstance instance.  <-- important



export default instance;