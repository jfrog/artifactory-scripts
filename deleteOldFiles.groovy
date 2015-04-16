@Grab(group = 'org.codehaus.groovy.modules.http-builder', module = 'http-builder', version = '0.6')
import groovy.time.TimeCategory
import groovyx.net.http.RESTClient

/**
 * Created by shaybagants on 4/16/15.
 * This groovy script searches for 20 files and delete items which answered the below creteria:
 * 1. Items which are files only
 * 2. Created mora than 1 year ago
 * 3. Not been downloaded for 6 month's
 *
 * By default, script will only return the biggest 20 files (can be configured to a different number of files to return)
 *
 */

String query = generateAQLquery()

def artifactoryURL = 'http://localhost:8081/artifactory/'
def restClient = new RESTClient(artifactoryURL)
restClient.setHeaders(['Authorization': 'Basic ' + "admin:password".getBytes('iso-8859-1').encodeBase64()])

def itemsToDelete = getAqlQueryResult(restClient, query)
if (itemsToDelete != null && itemsToDelete.size() + 0) {
    delete(restClient, itemsToDelete)
} else {
    println('Nothing to delete')
}

/**
 * Sent POST request to Artifactory and return the files which match our conditions
 */
public List getAqlQueryResult(RESTClient restClient, String query) {
    def response = restClient.post(path: 'api/search/aql',
            body: query,
            requestContentType: 'text/plain'
    )
    if (response.getData()) {
        def results = [];
        response.getData().results.each {
            results.add(constructPath(it))
        }
        return results;
    } else return null
}

/**
 * Sent DELETE request to Artifactory for each one of the returned items
 */
public delete(RESTClient restClient, List itemsToDelete) {
    itemsToDelete.each {
        restClient.delete(path: it)
        println(it+" has been deleted")
    }
}

/**
 * Generate the AQL query.
 */
public String generateAQLquery() {
    def currentDate = new Date()
    def created;
    def lastDownloaded
    use(TimeCategory) {
        created = (currentDate - 1.year).format("yyyy-MM-dd'T'")
        lastDownloaded = (currentDate - 6.months).format("yyyy-MM-dd'T'")
    }

    def numberOfFilesToReturn = 20
    def query = 'items.find({"type":"file","created":{"$lt":"' + created + '"},"stat.downloaded":{"$lt":"' + lastDownloaded + '"}})' +
            '.include("name","path","repo","size","stat.downloaded")' +
            '.sort({"$desc":["size","name"]})' +
            '.limit(' + numberOfFilesToReturn + ')'
    println("Sending query: '$query'")
    query
}

/**
 * Construct the full path form the returned items.
 * If the path is '.' (file is on the root) we ignores it and construct the full path from the repo and the file name only
 */
public constructPath(HashMap item) {
    if (item.path.toString().equals(".")) {
        return item.repo + "/" + item.name
    }
    return item.repo + "/" + item.path + "/" + item.name
}

