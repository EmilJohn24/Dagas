import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.css'; //Bootstrap
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
// Good tutorial: https://www.digitalocean.com/community/tutorials/build-a-to-do-application-using-django-and-react#step-3-setting-up-the-frontend
// Official website tutorial: https://reactjs.org/docs/getting-started.html
// Another tutorial: https://blog.logrocket.com/creating-an-app-with-react-and-django/
// Authentication tutorial: https://www.digitalocean.com/community/tutorials/how-to-add-login-authentication-to-react-applications
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
