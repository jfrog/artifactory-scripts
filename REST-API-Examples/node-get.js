var unirest = require('unirest'); //npm install unirest
var ARTIFACTORY = "http://127.0.0.1:8081/artifactory/"; //artifactory URL
var API = "api/security/users/admin"; //API URL
var URL = ARTIFACTORY + API;
var Request = unirest.get(URL); //this script is ONLY for GET commands

Request.auth({
  user: 'admin',
  pass: 'password',
  sendImmediately: true
})
.end(function(response){
    console.log(response.body)
  });