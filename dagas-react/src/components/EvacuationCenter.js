import '../App.css';
import { Component } from 'react';
import axios from "axios";


class EvacuationCenter extends Component{
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
export default EvacuationCenter;
