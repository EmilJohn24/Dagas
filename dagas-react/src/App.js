import logo from './logo.svg';
import './App.css';
import { Component } from 'react';
import axios from "axios";

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <img src={logo} className="App-logo" alt="logo" />
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }

class App extends Component{
  //retrieves the attributes of the tag and initializes the object
  constructor(props){
    super(props);
    this.state = {
      viewCompleted: false,
      evacuationCenters: [],
    }
  };
  refreshEvacuationCenters = () => {
    axios
      .get("/relief/api/evacuation-center/")
      .then((result) => this.setState({evacuationCenters: result.data}))
      .catch((error) => console.log(error));
  }
  renderEvacuationCenter = () => {
    return this.state.evacuationCenters.map((item) => (
      <li>{item.name}</li>
    ))
  }
  //runs when component works
  componentDidMount(){
    this.refreshEvacuationCenters();
  }

  //runs when class tag is called elsewhere
  render(){
    return (
      <main className="container">
        <h1>Evacuation Centers</h1>
        <ul className="list-group">{this.renderEvacuationCenter()}</ul>
      </main>
    )
  }


}
export default App;
