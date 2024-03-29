// import React from 'react';
// import { DirectionsRenderer } from "react-google-maps";
// import { useEffect, useState } from "react";


// export default function MapDirectionsRenderer(props) {
//     const [directions, setDirections] = useState(null);
//     const [error, setError] = useState(null);
  
//     useEffect(() => {
//       const { places, travelMode } = props;
  
//       const waypoints = places.map(p => ({
//         location: { lat: p.latitude, lng: p.longitude },
//         stopover: true
//       }));
//       const origin = waypoints.shift().location;
//       const destination = waypoints.pop().location;
  
//       const directionsService = new window.google.maps.DirectionsService();
//       directionsService.route(
//         {
//           origin: origin,
//           destination: destination,
//           travelMode: travelMode,
//           waypoints: waypoints
//         },
//         (result, status) => {
//           console.log(result)
//           if (status === window.google.maps.DirectionsStatus.OK) {
//             setDirections(result);
//           } else {
//             setError(result);
//           }
//         }
//       );
//     });
  
//     if (error) {
//       return <h1>{error}</h1>;
//     }
//     return (
//       directions && (
//         <DirectionsRenderer directions={directions} />
//       )
//     );
// }