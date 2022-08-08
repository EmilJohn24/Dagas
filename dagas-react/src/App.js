import logo from './logo.svg';
import './App.css';
import { Component } from 'react';
import EvacuationCenter from './components/EvacuationCenter';
import Login from './components/Login';
import Registration from './components/Registration';

import { BrowserRouter, Switch, Route, Link, Routes } from "react-router-dom";
// Bootstrap CSS
import "bootstrap/dist/css/bootstrap.min.css";
// Bootstrap Bundle JS
import "bootstrap/dist/js/bootstrap.bundle.min";
import UserTest from './test/userTest';
import InternalEvacuationCenter from './components/EvacuationCenterRender';
import axios from "axios";

// function App() {
//   return (
//     <Router>
//       <div className='flex flex-col min-h-screen overflow-hidden'>
        
//       </div>
//     </Router>
//   );
// }
axios.defaults.withCredentials = true

class App extends Component{
  //retrieves the attributes of the tag and initializes the object
  constructor(props){
    super(props);
  };
  
  //runs when class tag is called elsewhere
  render(){
    return (
        <div className='App flex flex-col min-h-screen overflow-hidden'>
          <BrowserRouter>
            <UserTest/>
            <Routes>
              <Route path="/login" element={<Login/>}/>
              <Route path="/register" element={<Registration/>}/>
              <Route path="/user_test" element={<UserTest/>}/>
              <Route path="/evacuation_centers" element={<InternalEvacuationCenter/>} />
            </Routes>
          </BrowserRouter>
        </div>
    );
  }


}
export default App;
