function AddDonation(props){
    // Standard POST formats
    [donationID, setDonationID] = useState(null);
    const createDonation = () => {
        /*
        Format:
            { }
        */
       empty_json = {}
       axios
            .post('/relief/api/donations/', JSON.stringify(empty_json), {
                "headers": {'Content-Type': 'application/json'},
                "credentials": "include",
                "withCredentials": true
            })
            .then((result) => {
                setDonationID(result.data.id);
            })
            .catch((error) => console.log(error));
    }
    const addSupply = (supply_json) => {
         /*
        Format:
            { 
                "name": name,
                "type": type_id,
                "quantity": quantity,
                "pax": pax,
                "donation": donationID
            }
        */
        // This might go on a Formik onSubmit prop

        axios
            .post('/relief/api/supplies/', JSON.stringify(supply_json), {
                "headers": {'Content-Type': 'application/json'},
                "credentials": "include",
                "withCredentials": true
            })
            .catch((error) => console.log(error));
        
    }
    // END Standard POST formats
    
    // TODO: Place "Add Donation" format here
}