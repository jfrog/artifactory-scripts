var request = require('request')
var JSONStream = require('JSONStream')
var es = require('event-stream')

var config = require('./conf/config.json');

request({url: config.sourceRegUrl})
  .pipe(JSONStream.parse('rows..tarball'))
  .pipe(es.mapSync(function(data) {
  	var n = data.lastIndexOf('/');
	var filename = data.substring(n, data.length);
	var packageName = filename.substring(0, filename.lastIndexOf('-'));
	
	data = config.targetRegUrl + packageName + '/-' + filename;
	
	request(data, function (error, response, body) {
	  if (!error && response.statusCode == 200) {
		console.log('File downloaded: ', data);
	  } else {
		console.log('Error downloading file:',response.statusCode,data);
	  }
	})	
  }))
  
request({url: config.sourceRegUrl})
  .pipe(JSONStream.parse('rows..tarball'))
  .pipe(es.mapSync(function(data) {
  	var n = data.lastIndexOf('/');
	var filename = data.substring(n, data.length);
	var packageName = filename.substring(0, filename.lastIndexOf('-'));
	
	data = config.targetRegUrl + packageName
	
	request(data, function (error, response, body) {
	  if (!error && response.statusCode == 200) {
		console.log('Package meta-data downloaded: ', data);
	  } else {
		console.log('Error downloading Package meta-data :',response.statusCode,data);
	  }
	})
  }))  
