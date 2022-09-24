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

// Material Dashboard 2 PRO React examples
import TimelineItem from "examples/Timeline/TimelineItem";

function OrdersOverview({transactionId, status}) {
  console.log(transactionId);
  const orderTimelineItems = [
    (
      <TimelineItem
            color="secondary"
            icon="shopping_cart"
            title="Order packaged"
            // dateTime="22 DEC 8:10 AM"
          />
    ), 
    (
      <TimelineItem
            color="secondary"
            icon="local_shipping"
            title="Order in transit"
            // dateTime="22 DEC 8:10 AM"
      />
    ), 
    (
      <TimelineItem
          color="success"
          icon="done"
          title="Order delivered"
          // dateTime="22 DEC 4:54 PM"
          lastItem
        />
    )
  ]
    
  
  var timeline = (
    <MDBox mt={2}>

      <TimelineItem
                color="secondary"
                icon="notifications"
                title="Request Accepted"
                // dateTime="22 DEC 7:20 PM"
            />
        <TimelineItem
          color="secondary"
          icon="inventory_2"
          title={`Generated id ${transactionId}`}
          // dateTime="22 DEC 7:21 AM"
        />
        {status > 1?orderTimelineItems[0]:""}
        {status > 2?orderTimelineItems[1]:""}
        {status == 3?orderTimelineItems[2]:""}        
        
    </MDBox>

  )
  return (
    <>
      <MDTypography variant="h6" fontWeight="medium">
        Track order
      </MDTypography>
        {timeline}
        
        
    </>
  );
}

export default OrdersOverview;
