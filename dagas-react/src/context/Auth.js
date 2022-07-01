import {createContext, useState, useEffect} from "react";
import jwt_decode from "jwt-decode";
import {useHistory} from "react-router-dom";

const UserAuthContext = createContext();

export default UserAuthContext;

// export const UserAuthProvider = ({c}) => {
//     const [authTokens, setAuthTokens] = useState(() => 
//     )
// }