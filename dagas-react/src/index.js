import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.css'; //Bootstrap
import './index.css';
import App from './App';
//AXIOS and navigation
import axiosConfig from "axiosConfig";
import LRU from 'lru-cache';
import {configure} from 'axios-hooks';

import { BrowserRouter } from "react-router-dom";
import reportWebVitals from './reportWebVitals';

// Good tutorial: https://www.digitalocean.com/community/tutorials/build-a-to-do-application-using-django-and-react#step-3-setting-up-the-frontend
// Official website tutorial: https://reactjs.org/docs/getting-started.html
// Another tutorial: https://blog.logrocket.com/creating-an-app-with-react-and-django/
// Authentication tutorial: https://www.digitalocean.com/community/tutorials/how-to-add-login-authentication-to-react-applications
//TODO: Study react-bootstrap or reactstrap for design 
//TODO: Consider getting a template (https://reactstrap.github.io/?path=/docs/home-themes--page)

// Material Dashboard 2 PRO React Context Provider
import { MaterialUIControllerProvider } from "context";
// https://stackoverflow.com/questions/51794553/how-do-i-create-configuration-for-axios-for-default-request-headers-in-every-htt
const cache = new LRU({max: 10})
configure({axiosConfig, cache});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <MaterialUIControllerProvider>
      <App />
    </MaterialUIControllerProvider>
  </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
