import axiosConfig from '../axiosConfig';
function ListRequests(props){

    const [requests, setRequests] = useState([]);
    searchQuery = ""
    //Standard GET format
    const listRequests = (query) => {
        var url = "/relief/api/requests/"
        if (query != "" && query){
            url += "?search=" + query;
        }
        console.log("HTTP GET on Requests...");
        axiosConfig
          .get(url)
          .then((result) => {
            setRequests(result.data);
          })
          .catch((error) => console.log(error));
      }

      // This causes the request loader to rerun when search query is altered
      useEffect(() => {
        listRequests(searchQuery);
      }, [searchQuery])  
      
      const renderRequestList = () => {
        return  requests.map((item) => {
          // TODO: Format for loading a single Request
          return null;
        })
      }
      //END Standard GET format

      // TODO: Return the list request component template. 
      // Use renderRequestList on container/table to put in a single entry
      return null;
      
}

function AddRequest(props){
    // Standard POST formats
    [requestID, setRequestID] = useState(-1);
    const postItemRequest = (item_request_json) => {
        /*
        Format:
            {
                "type": ##,
                "pax": ##,
                "barangay_request", id,
            }
        */
       // This might go on a Formik onSubmit prop
       axiosConfig
            .post('/relief/api/item-request/', JSON.stringify(item_request_json), {
                "headers": {'Content-Type': 'application/json'},
                "credentials": "include",
                "withCredentials": true
            })
            .catch((error) => console.log(error));
    }
    const postRequest = (evacuation_center_id) => {
        console.log(values);
        const request_body = {"evacuation_center": evacuation_center_id};
        axiosConfig
            .post('/relief/api/requests/', JSON.stringify(request_body), {
                "headers": {'Content-Type': 'application/json'},
                "credentials": "include",
                "withCredentials": true
            })
            .then((result) => {
                setRequestID(result.data.id);
            })
            .catch((error) => console.log(error));
        
    }
    // END Standard POST formats
}