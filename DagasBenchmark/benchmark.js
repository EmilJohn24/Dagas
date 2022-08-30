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
    url: '192.168.100.2:8000', //NOTE: This should be changed to localhost when doing more query-oriented tests
    connections: 10,
    duration: 120,
    timeout: 30,
    headers: {
        "Content-Type": 'application/json',
        "Authorization": basic_auth_header
    },
    requests: [
        {
            method: 'GET',
            path: '/relief/api/requests/'
        }
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
