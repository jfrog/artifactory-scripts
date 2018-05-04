#!/usr/bin/env groovy

@Grab('org.jsoup:jsoup:1.11.3')

import groovy.util.CliBuilder
import java.security.DigestInputStream
import java.security.MessageDigest
import java.util.concurrent.Executors
import org.jsoup.Jsoup

def downloadItem(url, auth) {
    def conn = null, stream = null
    println("Downloading pypi artifact at $url")
    try {
        conn = url.openConnection()
        if (auth) conn.setRequestProperty('Authorization', auth)
        if (conn.responseCode != 200) {
            throw new RuntimeException("Could not download from $url: $conn.responseCode: ${conn.errorStream.text}")
        }
        def file = File.createTempFile('pypicloudMigrator-', '.tmp')
        def digest = MessageDigest.getInstance('SHA-256')
        stream = new DigestInputStream(conn.inputStream, digest)
        file << stream
        return [file, digest.digest().encodeHex().toString()]
    } finally {
        stream?.close()
        conn?.disconnect()
    }
}

def deployItem(url, auth, checksum, path) {
    def conn = null
    if (path == null) {
        println("Deploying pypi artifact by checksum to $url")
    } else {
        println("Deploying pypi artifact to $url")
    }
    try {
        conn = url.openConnection()
        conn.requestMethod = 'PUT'
        conn.setRequestProperty('Authorization', auth)
        conn.setRequestProperty('X-Checksum-Sha256', checksum)
        if (path == null) {
            conn.setRequestProperty('X-Checksum-Deploy', 'true')
        } else {
            conn.doOutput = true
            path.withInputStream { conn.outputStream << it }
        }
        if (conn.responseCode == 201) return true
        else if (path == null && conn.responseCode == 404) return false
        else throw new RuntimeException("Could not upload to $url: $conn.responseCode: ${conn.errorStream.text}")
    } finally {
        conn?.disconnect()
    }
}

def manageItem(arturl, artauth, auth, itempath, itemurl) {
    def file = null
    def url = new URL(arturl, (arturl.path - ~'/$') + itempath)
    try {
        def hash = null
        (file, hash) = downloadItem(itemurl, auth)
        deployItem(url, artauth, hash, null) || deployItem(url, artauth, hash, file)
    } catch (Exception ex) {
        def writer = new StringWriter()
        writer.withPrintWriter { ex.printStackTrace(it) }
        println(writer.toString())
    } finally {
        try {
            file.delete()
        } catch (Exception ex) {}
    }
}

def pullPage(url, auth) {
    println("Downloading pypi listing at $url")
    def connection = Jsoup.connect(url.toExternalForm())
    connection.header('Accept', '*/*')
    if (auth) connection.header('Authorization', auth)
    def response = connection.execute()
    def realurl = response.url()
    def data = response.parse().getElementsByTag('a').collect {
        [path: it.text(), url: it.attributes().get('href')]
    }
    return [realurl, data]
}

def pull(url, auth, pool, cb) {
    def pagefutures = [], futures = []
    def realurl = null, pages = null
    try {
        (realurl, pages) = pullPage(url, auth)
    } catch (Exception ex) {
        def writer = new StringWriter()
        writer.withPrintWriter { ex.printStackTrace(it) }
        println(writer.toString())
        return [[], []]
    }
    pages.each { page ->
        pagefutures << pool.submit {
            def pageurl = new URL(realurl, page.url)
            def realpageurl = null, items = null
            try {
                (realpageurl, items) = pullPage(pageurl, auth)
            } catch (Exception ex) {
                def writer = new StringWriter()
                writer.withPrintWriter { ex.printStackTrace(it) }
                println(writer.toString())
                return
            }
            items.each { item ->
                def future = pool.submit {
                    def itemurl = new URL(realpageurl, item.url)
                    def itempath = "/$page.path/$item.path"
                    cb(itempath, itemurl)
                }
                synchronized (futures) {
                    futures << future
                }
            }
        }
    }
    return [pagefutures, futures]
}

def getargs() {
    def url = null, auth = null, arturl = null, artauth = null, threads = 10
    def use = './pypicloudMigrator.groovy [-t NUM (optional)] [pypicloud url] [pypycloud username:password (optional)] [artifactory repository url] [artifactory username:password]'
    def cli = new CliBuilder(usage: use)
    cli.t(longOpt: 'threads', args: 1, argName: 'thread count', 'The number of threads to use (default 10)')
    cli.h(longOpt: 'help', 'Print this help text and exit')
    def opts = cli.parse(args)
    if (!opts) {
        println('Error parsing command-line arguments.')
        cli.usage()
        System.exit(1)
    } else if (opts.h) {
        cli.usage()
        System.exit(0)
    }
    def arguments = opts.arguments()
    if (arguments.size() == 3) {
        url = new URL(arguments[0])
        arturl = new URL(arguments[1])
        artauth = "Basic ${arguments[2].bytes.encodeBase64()}"
    } else if (arguments.size() == 4) {
        url = new URL(arguments[0])
        auth = "Basic ${arguments[1].bytes.encodeBase64()}"
        arturl = new URL(arguments[2])
        artauth = "Basic ${arguments[3].bytes.encodeBase64()}"
    } else {
        println('Error: Wrong number of arguments.')
        cli.usage()
        System.exit(1)
    }
    if (opts.t) {
        threads = opts.t as int
        if (threads < 1) {
            println('Error: Thread count can not be less than 1.')
            cli.usage()
            System.exit(1)
        }
    }
    return [url, auth, arturl, artauth, threads]
}

def main() {
    def (url, auth, arturl, artauth, threads) = getargs()
    def pool = Executors.newFixedThreadPool(threads)
    def (pagefutures, futures) = pull(url, auth, pool) { itempath, itemurl ->
        manageItem(arturl, artauth, auth, itempath, itemurl)
    }
    pagefutures*.get()
    futures*.get()
    pool.shutdown()
}

main()
