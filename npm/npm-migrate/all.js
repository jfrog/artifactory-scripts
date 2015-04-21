var request = require('request')
var JSONStream = require('JSONStream')
var es = require('event-stream')

var config = require('./conf/config.json');

data = config.targetRegUrl + '/-/all';

request(data, function (error, response, body) {
  if (!error && response.statusCode == 200) {
	console.log('File downloaded: ', data);
  } else {
	console.log('Error downloading file:',response.statusCode,data);
  }
})  