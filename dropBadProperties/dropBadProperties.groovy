#!/usr/bin/env groovy

@Grab('org.jdom:jdom2:2.0.6')

import org.jdom2.Verifier
import java.net.URLEncoder
import groovy.json.*

def getArgs() {
    if (this.args.size() != 2) {
        println "Usage: groovy dropBadProperties.groovy <url> <user>:<pass>"
        System.exit(1)
    }
    def url = this.args[0] - ~'/$'
    def creds = "Basic ${this.args[1].bytes.encodeBase64()}"
    return [url, creds]
}

def dropProperties(url, creds, item, props) {
    props = props.collect { URLEncoder.encode(it.key, 'UTF-8') }.join(',')
    item = item.split('/').collect { URLEncoder.encode(it, 'UTF-8') }.join('/')
    def suffix = (item + '?properties=' + props).replaceAll('\\+', '%20')
    def conn = null
    try {
        conn = new URL(url + '/api/storage/' + suffix).openConnection()
        conn.requestMethod = 'DELETE'
        conn.setRequestProperty('Authorization', creds)
        assert conn.responseCode == 204
    } finally {
        conn?.disconnect()
    }
}

def getPropertiesList(url, creds, cb) {
    def query = 'items.find({"$and":[{"type":"any"},'
    query += '{"repo":{"$ne":"auto-trashcan"}}]})'
    query += '.include("repo","path","name","property")'
    def conn = null
    try {
        conn = new URL(url + '/api/search/aql').openConnection()
        conn.requestMethod = 'POST'
        conn.doOutput = true
        conn.setRequestProperty('Authorization', creds)
        conn.setRequestProperty('Content-Type', 'text/plain')
        conn.outputStream << query
        assert conn.responseCode == 200
        def json = new JsonSlurper().setType(JsonParserType.INDEX_OVERLAY)
        for (result in json.parse(conn.inputStream).results) {
            if (!('properties' in result)) continue
            def item = result.repo + '/'
            if (result.path != '.') item += result.path + '/'
            if (result.name != '.') item += result.name
            def props = []
            for (prop in result.properties) {
                if (prop.key == '.' || prop.key == '..'
                    || prop.key.contains(':')
                    || Verifier.checkXMLName(prop.key) != null) {
                    props << prop
                }
            }
            if (props.size() > 0) cb(item, props)
        }
    } finally {
        conn?.disconnect()
    }
}

def main() {
    def (url, creds) = getArgs()
    def ct = 0, log = new File('./dropBadProperties.log')
    log.withWriterAppend { writer ->
        try {
            writer.writeLine('--- Deleting bad properties ---')
            println '--- Deleting bad properties ---'
            getPropertiesList(url, creds) { item, props ->
                def propsmap = props.collectEntries { [it.key, it.value] }
                def propstxt = new JsonBuilder(propsmap).toString()
                writer.writeLine("Deleting from '$item': $propstxt")
                println "Deleting from '$item': $propstxt"
                try {
                    dropProperties(url, creds, item, props)
                    ct += props.size()
                } catch (Exception ex) {
                    ex.printStackTrace(new PrintWriter(writer))
                    ex.printStackTrace()
                }
            }
        } catch (Exception ex) {
            ex.printStackTrace(new PrintWriter(writer))
            ex.printStackTrace()
        } finally {
            writer.writeLine("Deleted $ct total properties")
            println "Deleted $ct total properties"
        }
    }
}

main()
