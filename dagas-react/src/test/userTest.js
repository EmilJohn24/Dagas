//api/users/current_user/
import '../App.css';
import { Component } from 'react';
import axios from "axios";


class UserTest extends Component{
  //retrieves the attributes of the tag and initializes the object
  constructor(props){
    super(props);
    this.state = {
        user: {}
    }
  };
  getCurrentUser = () => {
    axios
      .get("/relief/api/users/current_user/")
      .then((result) => this.setState({user: result.data}))
      .catch((error) => console.log(error));
  }
  renderUser = () => {
    return this.state.user.username;
  }
  //runs when component works
  componentDidMount(){
    this.getCurrentUser();
  }

  //runs when class tag is called elsewhere
  render(){
    return (
      <main className="container">
        <h1>Current User</h1>
        <p>{this.renderUser()}</p>
      </main>
    )
  }


}
export default UserTest;
