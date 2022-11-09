/**
=========================================================
* Material Dashboard 2 PRO React - v2.1.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-pro-react
* Copyright 2022 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

/** 
  All of the routes for the Material Dashboard 2 PRO React are added here,
  You can add a new route, customize the routes and delete the routes here.

  Once you add a new route on this file it will be visible automatically on
  the Sidenav.

  For adding a new route you can follow the existing routes in the routes array.
  1. The `type` key with the `collapse` value is used for a route.
  2. The `type` key with the `title` value is used for a title inside the Sidenav. 
  3. The `type` key with the `divider` value is used for a divider between Sidenav items.
  4. The `name` key is used for the name of the route on the Sidenav.
  5. The `key` key is used for the key of the route (It will help you with the key prop inside a loop).
  6. The `icon` key is used for the icon of the route on the Sidenav, you have to add a node.
  7. The `collapse` key is used for making a collapsible item on the Sidenav that contains other routes
  inside (nested routes), you need to pass the nested routes inside an array as a value for the `collapse` key.
  8. The `route` key is used to store the route location which is used for the react router.
  9. The `href` key is used to store the external links location.
  10. The `title` key is only for the item with the type of `title` and its used for the title text on the Sidenav.
  10. The `component` key is used to store the component of its route.
*/

// Material Dashboard 2 PRO React layouts
import ProfileOverview from "layouts/pages/profile/profile-overview";
import AllProjects from "layouts/pages/profile/all-projects";
import NewUser from "layouts/pages/users/new-user";
import Settings from "layouts/pages/account/settings";
import DataTables from "layouts/applications/data-tables";

//Dagas Imports
import Login from './components/Login';
import TransactionList from "layouts/transactions/transaction-list";
import SupplyList from "layouts/supply/supply-list";
import AcceptRequest from "layouts/request/accept-request";
import BarangayRequest from "layouts/barangay/request";
import RequestList from "layouts/barangay/request-list";
import Calamities from "layouts/calamity/select-calamity";
import Suggestions from "layouts/suggestions";

// Material Dashboard 2 PRO React components
import MDAvatar from "components/MDAvatar";

// @mui icons
import Icon from "@mui/material/Icon";

// Images
import profilePicture from "assets/images/team-3.jpg";
import Registration from "components/Registration";
import EvacuationMap from "layouts/evacuation-map";
// const currentUser = getCurrentUser();
if (!currentUser){
  currentUser = {
    first_name: "AAA",
    last_name: "AAA"
  } 
}
var currentUser = {
  first_name: "AAA",
  last_name: "AAA"
}
// const currentUser = null;
const routes = [
  // {
  //   type: "collapse",
  //   name: "Login",
  //   key: "login",
  //   route: "/login",
  //   component: <Login/>,
  //   noCollapse: true

  // },
  // {
  //   type: "collapse",
  //   name: "Registration",
  //   key: "register",
  //   route: "/register",
  //   component: <Registration/>,
  //   noCollapse: true
  // },
  {
    type: "collapse",
    name: "Select Calamity",
    key: "calamity",
    roles: ["Donor"],
    route: "/calamity",
    component: <Calamities/>,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "View/Add Supply",
    key: "supply-list",
    roles: ["Donor"],
    route: "/supplies",
    component: <SupplyList />,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "View Barangay Requests",
    key: "request-list",
    route: "/requests",
    component: <RequestList />,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "Suggestions",
    key: "suggestions",
    roles: ["Donor"],
    route: "/suggestions",
    component: <Suggestions/>,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "Barangay Request",
    key: "barangay-request",
    roles: ["Barangay"],
    route: "/request",
    component: <BarangayRequest/>,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "Evacuation Map",
    key: "evacuation-map",
    route: "/evacuationmap",
    component: <EvacuationMap/>,
    noCollapse: true
  },
  // {
  //   type: "collapse",
  //   name: "Accept Request",
  //   key: "accept-request",
  //   route: "/AcceptRequest",
  //   component: <AcceptRequest/>,
  //   noCollapse: true
  // },
  {
    type: "collapse",
    name: "Transaction List",
    key: "transaction-list",
    route: "/transactions",
    component: <TransactionList />,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "My Profile",
    key: "my-profile",
    route: "/pages/profile/profile-overview",
    component: <ProfileOverview />,
    icon: <MDAvatar src={currentUser.profile_picture} alt="my-profile" size="sm" />,
    noCollapse: true
  },
  {
    type: "collapse",
    name: "Logout",
    key: "logout",
    route: "/login",
    component: <Login/>,
    noCollapse: true
  },
  { type: "divider", key: "divider-0" },
];

export default routes;
