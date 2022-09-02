'use strict'

const autocannon = require('autocannon');
//Basic Auth params
const user = {
    username: "FakeDonor0",
    password: "donor123"
}
const basic_auth_header =  'Basic ' + btoa(user.username + ':' + user.password);

// For simplicity, we allow the server to use Basic Auth here
const instance = autocannon({
    workers: 4,
    url: 'https://dagas.herokuapp.com', //NOTE: This should be changed to localhost or a local IP address when doing more query-oriented tests
    connections: 1000,
    // duration: 120,
    amount: 10000,
    timeout: 120,
    headers: {
        "Content-Type": 'application/json',
        "Authorization": basic_auth_header
    },
    requests: [
        {
            method: 'GET',
            path: '/relief/api/requests/?page=1'
        },
        // {
        //     method: 'GET',
        //     path: '/relief/api/supplies/'
        // }, 
        // {
        //     method: 'GET',
        //     path: '/relief/api/user-location/'
        // }
    ]
}, console.log);

instance.on('response', handleResponse);
// instance.on('error', handleError);

function handleResponse (client, statusCode, resBytes, responseTime) {
    console.log(`Got response with code ${statusCode} in ${responseTime} milliseconds`)
    console.log(`response: ${resBytes.toString()}`)
}
process.once('SIGINT', () => {
    instance.stop();
})

autocannon.track(instance, {renderResultsTable: true})
