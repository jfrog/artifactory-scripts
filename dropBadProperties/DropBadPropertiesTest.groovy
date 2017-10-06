#!/usr/bin/env groovy

@Grab('org.jfrog.artifactory.client:artifactory-java-client-services:2.5.2')
@GrabExclude("org.codehaus.groovy:groovy-xml")

import org.jfrog.artifactory.client.ArtifactoryClientBuilder
import org.jfrog.artifactory.client.model.repository.settings.impl.GenericRepositorySettingsImpl

def url = 'http://localhost:8088/artifactory/'

println 'Connecting to Artifactory ...'
def builder = ArtifactoryClientBuilder.create()
builder.url = url
builder.username = 'admin'
builder.password = 'password'
def artifactory = builder.build()

println 'Creating repository ...'
def repobuild = artifactory.repositories().builders().localRepositoryBuilder()
repobuild.key('bad-props-test-local')
repobuild.repositorySettings(new GenericRepositorySettingsImpl())
artifactory.repositories().create(0, repobuild.build())
def repo = artifactory.repository('bad-props-test-local')

try {
    def rootprops = ['good.prop': 'value', 'bad prop': 'value']
    def l1props = ['good.prop': 'value', 'bad:prop': 'value']
    def l2props = ['good.prop': 'value', 'bad/prop': 'value']
    def content = new ByteArrayInputStream('content'.bytes)
    println 'Adding files ...'
    repo.upload('l1file', content).doUpload()
    repo.upload('dir/l2file', content).doUpload()
    println 'Adding properties ...'
    repo.folder('.').properties().addProperties(rootprops).doSet()
    repo.file('l1file').properties().addProperties(l1props).doSet()
    repo.file('dir/l2file').properties().addProperties(l2props).doSet()

    println 'Running script ...'
    def output = new StringBuilder()
    def proc = ['groovy', 'dropBadProperties.groovy', url, 'admin:password'].execute()
    proc.consumeProcessErrorStream(System.err)
    proc.consumeProcessOutputStream(output)
    assert proc.waitFor() == 0

    println 'Checking logs ...'
    for (log in [output.toString(), new File('dropBadProperties.log').text]) {
        assert log.contains('bad prop')
        assert log.contains('bad:prop')
        assert log.contains('bad/prop')
        assert !log.contains('good.prop')
        assert log.contains('Deleted 3 total properties')
    }

    println 'Checking properties ...'
    def getrootprops = repo.folder('.').getProperties('good.prop', 'bad prop')
    def getl1props = repo.file('l1file').getProperties('good.prop', 'bad:prop')
    def getl2props = repo.file('dir/l2file').getProperties('good.prop', 'bad/prop')
    assert 'good.prop' in getrootprops
    assert 'good.prop' in getl1props
    assert 'good.prop' in getl2props
    assert !('bad prop' in getrootprops)
    assert !('bad:prop' in getl1props)
    assert !('bad/prop' in getl2props)

    println 'Success'
} finally {
    println 'Cleaning up ...'
    repo?.delete()
    new File('dropBadProperties.log').delete()
}
