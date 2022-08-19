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


// Material Dashboard 2 PRO React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

import DefaultCell from "./components/DefaultCell";
import DataTable from "examples/Tables/DataTable";

function OrderSummary({orders}) {
  var dataTableData = {
    columns: [
     
      
      {
          Header: "name",
          accessor: "supply_info.name",
          Cell: ({value}) => (
            <DefaultCell value={value} />
          ),
        },
        {
          Header: "type",
          accessor: "supply_info.type_str",
          Cell: ({value}) => (
            <DefaultCell value={value} />
          ),
        },
        {
          Header: "pax",
          accessor: "pax",
          Cell: ({value}) => (
            <DefaultCell value={value} />
          ),
        },
    
    ],
    rows: orders

  };
  return (
    <DataTable table={dataTableData} entriesPerPage={true} />

  );
}

export default OrderSummary;
