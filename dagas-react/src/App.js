import logo from './logo.svg';
import './App.css';
import { Component } from 'react';
import EvacuationCenter from './components/EvacuationCenter';
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";

function App() {
  return (
    <Router>
      <div className='flex flex-col min-h-screen overflow-hidden'>
        
      </div>
    </Router>
  );
}

// class App extends Component{
//   //retrieves the attributes of the tag and initializes the object
//   constructor(props){
//     super(props);
//   };
  
//   //runs when class tag is called elsewhere
//   render(){
//     return (
//       <EvacuationCenter/>
//     )
//   }


// }
export default App;
