#!/usr/bin/env groovy

@Grab('org.spockframework:spock-core:1.1-groovy-2.4')

import groovy.json.JsonBuilder
import groovy.json.JsonSlurper
import spock.lang.Specification

class PypicloudMigratorTest extends Specification {
    def auth = "Basic ${'admin:password'.bytes.encodeBase64()}"

    def 'pypicloudMigrator functional test'() {
        setup:
        println("Starting pypicloud docker container")
        startInDocker('stevearc/pypicloud:latest', 'pypi-test-pypicloud', '8080', '8098')
        println("Starting artifactory docker container")
        startInDocker('docker.bintray.io/jfrog/artifactory-pro:latest', 'pypi-test-artifactory', '8081', '8099')
        println("Waiting for artifactory to start")
        waitForArtifactory('pypi-test-artifactory')
        sleep(1000)
        println("Bootstrapping pypicloud admin")
        bootstrapPypicloudUser('8098', 'admin', 'password')
        println("Deploying license to artifactory")
        deployArtifactoryLicense('8099', './test/artifactory.lic')
        println("Creating pypi-local repo in artifactory")
        createArtifactoryPypiRepo('8099', 'pypi-local')
        println("Initializing python virtualenv")
        initVirtualenv('env')

        when: 'deploying to Pypicloud'
        println("Deploying packages to pypicloud")
        uploadToPypicloud('8098', 'testpack1', '1.0.0', './test/testpack1-1.0.0-py2.py3-none-any.whl')
        uploadToPypicloud('8098', 'testpack2', '1.0.0', './test/testpack2-1.0.0-py2.py3-none-any.whl')
        uploadToPypicloud('8098', 'testpack3', '1.0.0', './test/testpack3-1.0.0-py3.6.egg')

        then:
        checkInPypicloud('8098', 'testpack1')
        checkInPypicloud('8098', 'testpack2')
        checkInPypicloud('8098', 'testpack3')

        when: 'running migration'
        println("Running migrator")
        runMigrator('8098', '8099', 'pypi-local')

        then:
        checkInArtifactory('8099', 'pypi-local/testpack1/testpack1-1.0.0-py2.py3-none-any.whl')
        checkInArtifactory('8099', 'pypi-local/testpack2/testpack2-1.0.0-py2.py3-none-any.whl')
        checkInArtifactory('8099', 'pypi-local/testpack3/testpack3-1.0.0-py3.6.egg')

        when: 'installing from Artifactory'
        println("Waiting for artifactory to index packages")
        waitForIndexing('8099', 'pypi-local/testpack3/testpack3-1.0.0-py3.6.egg')
        println("Installing packages from artifactory to python virutalenv")
        installWheelToVirtualenv('env', '8099', 'pypi-local', 'testpack1')
        installEggToVirtualenv('env', '8099', 'pypi-local', 'testpack3')

        then:
        checkInVirtualenv('env', 'testpack1')
        checkInVirtualenv('env', 'testpack2')
        checkInVirtualenv('env', 'testpack3')

        cleanup:
        println("Deleting python virtualenv")
        cleanupVirtualenv('env')
        println("Deleting artifactory docker container")
        cleanupDocker('pypi-test-artifactory')
        println("Deleting pypicloud docker container")
        cleanupDocker('pypi-test-pypicloud')
    }

    void startInDocker(image, name, portfrom, portto) {
        def p = "docker run -d -p$portto:$portfrom --name=$name $image".execute()
        assert p.waitFor() == 0
    }

    void cleanupDocker(name) {
        try {
            "docker stop $name".execute().waitFor()
            "docker rm $name".execute().waitFor()
        } catch (Exception ex) {}
    }

    void initVirtualenv(path) {
        def p = "python3 -m virtualenv $path".execute()
        assert p.waitFor() == 0
    }

    void cleanupVirtualenv(path) {
        def p = "rm -r $path".execute()
        assert p.waitFor() == 0
    }

    void deployArtifactoryLicense(port, path) {
        def conn = new URL("http://localhost:$port/artifactory/api/system/licenses").openConnection()
        conn.doOutput = true
        conn.requestMethod = 'POST'
        conn.setRequestProperty('Authorization', auth)
        conn.setRequestProperty('Content-Type', 'application/json')
        def content = [licenseKey: new File(path).text]
        conn.outputStream << new JsonBuilder(content).toString()
        assert conn.responseCode == 200
        conn.disconnect()
    }

    void createArtifactoryPypiRepo(port, name) {
        def conn = new URL("http://localhost:$port/artifactory/api/repositories/$name").openConnection()
        conn.doOutput = true
        conn.requestMethod = 'PUT'
        conn.setRequestProperty('Authorization', auth)
        conn.setRequestProperty('Content-Type', 'application/json')
        def content = [rclass: 'local', packageType: 'pypi']
        conn.outputStream << new JsonBuilder(content).toString()
        assert conn.responseCode == 200
        conn.disconnect()
    }

    void bootstrapPypicloudUser(port, username, password) {
        def conn = new URL("http://localhost:$port/api/user/admin/").openConnection()
        conn.doOutput = true
        conn.requestMethod = 'PUT'
        conn.setRequestProperty('Content-Type', 'application/x-www-form-urlencoded')
        conn.outputStream << 'password=password'
        assert conn.responseCode == 200
        conn.disconnect()
    }

    void waitForArtifactory(name) {
        def p = "docker logs -f $name".execute()
        p.consumeProcessErrorStream(new File('/dev/null').newOutputStream())
        try {
            p.in.eachLine { line ->
                if (!line.contains('Artifactory successfully started')) return
                throw new RuntimeException('<terminating early>')
            }
        } catch (RuntimeException ex) {
            if (ex.message != '<terminating early>') throw ex
        } finally {
            p.destroy()
        }
    }

    void waitForIndexing(port, path) {
        while (true) {
            def conn = new URL("http://localhost:$port/artifactory/api/storage/$path?properties").openConnection()
            conn.requestMethod = 'GET'
            conn.setRequestProperty('Authorization', auth)
            assert conn.responseCode in [200, 404]
            if (conn.responseCode == 200) {
                def result = new JsonSlurper().parse(conn.inputStream)
                conn.disconnect()
                if ('pypi.name' in result.properties) return
            }
            sleep(1000)
        }
    }

    void uploadToPypicloud(port, name, version, path) {
        def conn = new URL("http://localhost:$port/simple/").openConnection()
        conn.doOutput = true
        conn.requestMethod = 'POST'
        conn.setRequestProperty('Authorization', auth)
        conn.setRequestProperty('Content-Type', 'multipart/form-data; boundary=qwerty')
        def os = conn.outputStream
        os << '--qwerty\r\n'
        os << 'Content-Disposition: form-data; name=":action"\r\n\r\n'
        os << 'file_upload\r\n'
        os << '--qwerty\r\n'
        os << 'Content-Disposition: form-data; name="name"\r\n\r\n'
        os << "$name\r\n"
        os << '--qwerty\r\n'
        os << 'Content-Disposition: form-data; name="version"\r\n\r\n'
        os << "$version\r\n"
        os << '--qwerty\r\n'
        os << 'Content-Disposition: form-data; name="content"; filename="'
        os << new File(path).name
        os << '"\r\n\r\n'
        new File(path).withInputStream { os << it }
        os << '\r\n'
        os << '--qwerty--'
        assert conn.responseCode == 200
        conn.disconnect()
    }

    void runMigrator(pypicloudport, artifactoryport, repo) {
        def p = ["./pypicloudMigrator.groovy",
                 "http://localhost:$pypicloudport/simple/", "admin:password",
                 "http://localhost:$artifactoryport/artifactory/$repo/",
                 "admin:password"].execute()
        assert p.waitFor() == 0
    }

    void installWheelToVirtualenv(path, port, repo, pack) {
        def p = ["bash", "-c", "source $path/bin/activate && pip install" +
                 " -i http://localhost:$port/artifactory/api/pypi/$repo/simple/" +
                 " $pack && deactivate"].execute()
        assert p.waitFor() == 0
    }

    void installEggToVirtualenv(path, port, repo, pack) {
        def p = ["bash", "-c", "source $path/bin/activate && easy_install" +
                 " -i http://localhost:$port/artifactory/api/pypi/$repo/simple/" +
                 " $pack && deactivate"].execute()
        assert p.waitFor() == 0
    }

    boolean checkInPypicloud(port, pack) {
        def conn = new URL("http://localhost:$port/api/package/").openConnection()
        conn.requestMethod = 'GET'
        conn.setRequestProperty('Authorization', auth)
        assert conn.responseCode == 200
        def result = new JsonSlurper().parse(conn.inputStream)
        conn.disconnect()
        return pack in result.packages
    }

    boolean checkInArtifactory(port, path) {
        def conn = new URL("http://localhost:$port/artifactory/$path").openConnection()
        conn.requestMethod = 'HEAD'
        conn.setRequestProperty('Authorization', auth)
        def response = conn.responseCode
        conn.disconnect()
        return response == 200
    }

    boolean checkInVirtualenv(path, pack) {
        def err = new FileWriter(new File('/dev/null'))
        def out = new StringBuilder()
        def p = ["bash", "-c", "source $path/bin/activate &&" +
                 " pip list -l --format json && deactivate"].execute()
        p.consumeProcessOutput(out, err)
        assert p.waitFor() == 0
        def json = new JsonSlurper().parseText(out.toString())
        return json.any { it.name == pack }
    }
}
