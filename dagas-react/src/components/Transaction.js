import axiosConfig from "../axiosConfig";
import { getItemType } from Utility;

function ListTransactions(props){

    const [transactions, setTransaction] = useState([]);
    searchQuery = ""
    //Standard GET format
    const listTransactions = (query) => {
        var url = "/relief/api/transactions/"
        if (query != "" && query){
            url += "?search=" + query;
        }
        console.log("HTTP GET on Requests...");
        axios
          .get(url)
          .then((result) => {
            setTransaction(result.data);
          })
          .catch((error) => console.log(error));
      }

      // This causes the transaction loader to rerun when search query is altered
      useEffect(() => {
        listTransactions(searchQuery);
      }, [searchQuery])  
      
      const renderTransactionList = () => {
        return  transactions.map((item) => {
          // TODO: Format for loading a single transactions
          return null;
        })
      }
      //END Standard GET format

      // TODO: Return the list transactions component template. 
      // Use renderTransactionList on container/table to put in a single entry
      return null;
}

//to get untransacted items
function getUntransactedItems(props){
  
  untransactedAmount = [];

  for (var i = 0; i < getItemType.length; i++) {
    console.log(getItemType[i]);
    var url = props.getRequestUrl + "not_in_transaction/?type=" + getItemType[i]
    axiosConfig
        .get(url)
        .then((result) => {
          untransactedAmount[i] = result;
        })
        .catch((error) => console.log(error));
  }
  return null;
}

//retrive geolocation of donor
function retriveGeoLocationofDonor(props){

  const [donorLat, setLat] = useState(0);
  const [donorLng, setLng] = useState(0);

  var url = props.getRequestUrl + "/relief/api/users/" + props.donorUserId + "/get_most_recent_location/" 
  axiosConfig
      .get(url)
      .then((result) => {
        setLat(parseFloat(result.geolocation.split(",")[0]));
        setLng(parseFloat(result.geolocation.split(",")[1]));
      })
      .catch((error) => console.log(error));
  return null;
} 