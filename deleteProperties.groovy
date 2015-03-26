/*
 * Copyright (C) 2011 JFrog Ltd.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 *
*This plugin will delete all of the desired properties from a repository according to a list that you will provide in a seperate file.
*Note that this will delete by default all of the desrid properties recursivll.
*/

@GrabResolver(name = 'jcenter', root = 'http://jcenter.bintray.com/')
@Grab(group = 'org.codehaus.groovy.modules.http-builder', module = 'http-builder', version = '0.6')
import groovyx.net.http.RESTClient

String url='https://localhost:8081/' //Please replace this one with your Artifactory server address.
def repository = "libs-release-local/" //Please write the desired repository name and add a '/' at the end as in this example.
new File('propertiesToDelete.txt').eachLine { line, nb ->  //Please replace the file name with the correct file name that includes the properties list
    def restClient = new RESTClient(url)
    restClient.auth.basic 'username', 'password'  // Enter your credentials, can be encrypted password.
    println "Starting to delete property:" + line  
    def response = restClient.delete(path: "api/storage/"+ repository, params:['properties': line, 'recursive': 1 ]) // Pay attention that currently it will delete the properties recursivlly, if this is not desride delete the proeprty 'recursive'
    println "Property " + line +" was deleted"
}
