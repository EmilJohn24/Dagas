import axios from 'axios';

const instance = axios.create({
    // baseURL: 'http://192.168.100.2:8000',
    withCredentials: true,
    credentials: "include",
    headers: {
        'Content-Type': 'application/json',
    }

});

axios.defaults.headers.post['Access-Control-Allow-Origin'] = '*';


// instance.defaults.headers.common['Authorization'] = 'AUTH TOKEN FROM INSTANCE';


export default instance;