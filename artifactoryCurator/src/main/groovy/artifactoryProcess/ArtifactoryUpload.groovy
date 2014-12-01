package artifactoryUpload

import com.xlson.groovycsv.CsvIterator
import groovy.util.logging.Log
import org.jfrog.artifactory.client.Artifactory
import org.jfrog.artifactory.client.Repositories
import org.jfrog.artifactory.client.model.Item
import org.jfrog.artifactory.client.model.impl.RepositoryTypeImpl
import org.jfrog.artifactory.client.DownloadableArtifact;
import org.jfrog.artifactory.client.UploadableArtifact;
import org.jfrog.artifactory.client.ItemHandle;
// import org.jfrog.artifactory.client.model.File; Conflicts with Java File class which we use elsewhere
import org.jfrog.artifactory.client.PropertiesHandler;
import org.jfrog.artifactory.client.model.Folder
import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.ExampleMode;
import org.kohsuke.args4j.Option;
import groovy.transform.stc.ClosureParams;
import groovy.transform.stc.SimpleType;
import org.jfrog.artifactory.client.ArtifactoryClient;
import org.jfrog.artifactory.client.RepositoryHandle;
import com.xlson.groovycsv.CsvParser;

/* Blah!  Comment out the Grapes sections if you want to build a stand alone jar file.  Double Blah!! */
@Grapes([
        @GrabResolver(name='artifactory01.nexus.commercehub.com', root='http://artifactory01.nexus.commercehub.com/artifactory/ext-release-local/', m2Compatible=true),
        @Grab(group='net.sf.json-lib', module='json-lib', version='2.4', classifier='jdk15' ),
        @Grab(group='org.codehaus.groovy.modules.http-builder', module='http-builder', version='0.7'),
        @Grab( group='com.xlson.groovycsv', module='groovycsv', version='1.0' ),
        @GrabExclude(group='org.codehaus.groovy', module='groovy-xml')

])

@Grapes( [
        @Grab(group='org.kohsuke.args4j', module='args4j-maven-plugin', version='2.0.22'),
        @GrabExclude(group='org.codehaus.groovy', module='groovy-xml')
])

@Grapes([
        @Grab(group='org.jfrog.artifactory.client', module='artifactory-java-client-services', version='0.13'),
        @GrabExclude(group='org.codehaus.groovy', module='groovy-xml')
])
/* End of commented out code. */

/**
 * This groovy class is meant to upload artifacts from a specified directory.
 *
 * There are two additional options.  The first is the dry-run option. This way you can get
 * an overview of what will be processed. If specified, no artifacts will be uploaded.
 * The second is full-log option which will display processing information which
 * can be useful if your script is not working quite right.
 *
 * Usage example
 *   groovy src/main/groovy/artifactoryProcess/ArtifactoryUpload.groovy --function upload --sourceDir //ciJenkins/d$/ci/jobs/targetJob/builds/2014-11-17_12-17-07/archive/archived --value 1.0.6 --jarsToUpload OSupload.csv --domain com/yourDomain --web-server http://artifactory/ --repository libs-release-test --userName someUser --password somePassword
 *  
 * @author Brian Carr (snippets from Jettro Coenradie, David Carr and others)
 */

class ArtifactoryUpload {
    public static final Set< String > validFunctions = [ 'upload', 'config' ];
    public static final Set< String > validParameters = [ 'function', 'value', 'sourceDir', 'jarsToUpload', 'webServer', 'repoName', 'domain', 'userName', 'password', 'dry-run', 'full-log' ];

    @Option(name='--dry-run', usage='Don\'t change anything; just list what would be done')
    boolean dryRun;

    @Option(name='--full-log', usage='Display miscellaneous steps for processing artifacts')
    boolean fullLog;

//  eg  --function upload
    @Option(name='--function', metaVar='function', usage="function to perform on artifacts")
    String function;

//  eg  --value production
    @Option(name='--value', metaVar='value', usage="value to use with certain functions, often required")
    String value;

//  eg  --sourceDir d:/temp/bin
    @Option(name='--sourceDir', metaVar='sourceDir', usage="source directory for uploaded artifacts, optional")
    String sourceDir;

//  eg  --jarsToUpload jarsToUpload.csv
    @Option(name='--jarsToUpload', metaVar='jarsToUpload', usage="name of csv file with jar files to upload")
    String jarsToUpload;

//  eg  --web-server 'http://artifactory01/'
    @Option(name='--web-server', metaVar='webServer', usage='URL to use to access Artifactory server')
    String webServer;

//  eg  --repository 'libs-release-prod'
    @Option(name='--repository', metaVar='repoName', usage='Name of the repository to scan.')
    String repoName;

//  eg  --domain 'org/apache'
    @Option(name='--domain', metaVar='domain', usage='Name of the domain to scan.')
    String domain;

//  eg  --userName publish
    @Option(name='--userName', metaVar='userName', usage='userName to use to access Artifactory server')
    String userName;

//  eg  --password Must.Use.Password
    @Option(name='--password', metaVar='password', usage='Password to use to access Artifactory server.')
    String password;

    @Argument
    ArrayList<String> versionsToUse = new ArrayList<String>();

    class Branch{
        String branchName;
        List< PathAndDate > pathAndDate;
    }

    class PathAndDate{
        String path;
        Date dtCreated;
    }
    class JarRecord {
        String jarName;
        String project;
    }

    @SuppressWarnings(["SystemExit", "CatchThrowable"])
    static void main( String[] args ) {
        try {
        new ArtifactoryUpload().doMain( args );
        } catch (Throwable throwable) {
            // Java returns exit code 0 if it terminates because of an uncaught Throwable.
            // That's bad if we have a process like Bamboo depending on errors being non-zero.
            // Thus, we catch all Throwables and explicitly set the exit code.
            println( "Unexpected error: ${throwable}" )
            System.exit(1)
        }
        System.exit(0);
    }

    List< JarRecord > uploadList = [];

    Artifactory srvr;
    RepositoryHandle repo;
    private int numProcessed = 0;
    private long thisSize = 0;
    private long overAllSize = 0;
    String firstFunction;
    String lastConfig;

    void doMain( String[] args ) {
        CmdLineParser parser = new CmdLineParser( this );
        try {
            parser.parseArgument(args);
            if( function == 'config' && value == null ) {
                throw new CmdLineException("You must provide a config.csv file as the value if you specify the config function.");
            }
            firstFunction = function;   // Flag in case we recurse into config files, where did we start
            if( function == 'config' ) {
                processConfig();
                return;
            } else {
                checkParms();
            }

        } catch(CmdLineException ex) {
            System.err.println(ex.getMessage());
            System.err.println();
            System.err.println( "groovy ArtifactoryUpload.groovy [--dry-run] [--full-log] --function <func> --value <val> --web-server http://YourWebServer/ --repository libs-release-local --domain <com/YourOrg> Version1 ..." );
            parser.printUsage(System.err);
            System.err.println();
            System.err.println( "  Example: groovy ArtifactoryUpload.groovy"+parser.printExample(ExampleMode.ALL) );
            System.err.println();
            System.err.println( "  Supported functions include ${validFunctions}" );
            System.err.println();
            System.err.println( "  Columns in config csv files can be ${validParameters}" );
            return;
        }

        println( "Started processing of $function with $value for $jarsToUpload on $webServer in $repoName/$domain with $versionsToUse." );
        
        withClient { newClient ->
            srvr = newClient;
            processRepo();
            if( function == 'size' ) {
                int sizeM = overAllSize / 1000000;
                println "Size on ${ domain } was ${ sizeM } megabtyes."; }

        }
    }

    def processRepo() {
        numProcessed = 0;                      // Reset count from last repo.
        repo = srvr.repository( repoName );
        uploadJars( );
        if( dryRun ) {
            println "$numProcessed folders would have been $function[ed] with $value.";
        } else {
            println "$numProcessed folders were $function[ed] with $value.";
        }

    }

    def processConfig() {
        File configCSV = new File( value );
        lastConfig = value;  // Record which csv file we have last dived into.
        Artifactory mySrvr = srvr; // Each line of config could have a different web server, preserve connection in case recursing
        configCSV.withReader {
            CsvIterator csvIt = CsvParser.parseCsv( it );
            for( csvRec in csvIt ) {
                if (fullLog) println("Step is ${csvRec}");
                Map cols = csvRec.properties.columns;
                if( cols.containsKey( 'function'   ) && !noValue( csvRec.function   ) ) function   = csvRec.function  ;
                if( cols.containsKey( 'value'      ) && !noValue( csvRec.value      ) ) value      = csvRec.value     ;
                if( cols.containsKey( 'sourceDir'  ) && !noValue( csvRec.sourceDir  ) ) sourceDir  = csvRec.sourceDir ;
                if( cols.containsKey( 'jarsToUpload' ) && !noValue( csvRec.jarsToUpload ) ) jarsToUpload = csvRec.jarsToUpload;
                if( cols.containsKey( 'webServer'  ) && !noValue( csvRec.webServer  ) ) webServer  = csvRec.webServer ;
                if( cols.containsKey( 'repoName'   ) && !noValue( csvRec.repoName   ) ) repoName   = csvRec.repoName  ;
                if( cols.containsKey( 'domain'     ) && !noValue( csvRec.domain     ) ) domain     = csvRec.domain    ;
                if( cols.containsKey( 'userName'   ) && !noValue( csvRec.userName   ) ) userName   = csvRec.userName  ;
                if( cols.containsKey( 'password'   ) && !noValue( csvRec.password   ) ) password   = csvRec.password  ;

                checkParms();
                withClient { newClient ->
                    srvr = newClient;
                    processRepo();
                }
                srvr = mySrvr;  // Restore previous web server connection
            }
        }
    }

    def checkParms() {
        readJarCSV();  // Process any jarsToUpload file.
        String prefix;

        if( firstFunction == 'config' && function != 'config' ) {
            prefix = "While processing ${lastConfig} encountered, ";
        } else prefix = '';
        if( !validFunctions.contains( function ) ) {
            throw new CmdLineException( "${prefix}Unrecognized function ${function}, function is required and must be one of ${validFunctions}." );
        }
        if( function == 'upload' && noValue( value ) ) {
            throw new CmdLineException( "${prefix}You must provide a value (version) to upload with if you specify the upload function." );
        }
        if( function != 'repoPrint' && noValue( domain ) ) {
            throw new CmdLineException( "${prefix}You must provide a domain to use with the ${function} function." );
        }
        if( function == 'upload' ) {
            if( noValue( sourceDir ) ) sourceDir = '.';
        }
        if( noValue( webServer ) || noValue( userName ) || noValue( password ) || noValue( repoName ) ) {
            throw new CmdLineException( "${prefix}You must provide the webServer, userName, password and repository name values to use." );
        }
        if( versionsToUse.size() == 0 && uploadList.size() == 0 ) {
            throw new CmdLineException( "${prefix}You must provide jarsToUpload or a list of artifact names to act upon." );
        }

    }
    void readJarCSV() {  // Process any jarsToUpload file.
        if( !noValue( jarsToUpload ) ) {
            uploadList.clear();                         // Throw away any previous states from last step
            if( fullLog ) println( "Parsing ${jarsToUpload}." )
            File jarsCSV = new File( jarsToUpload );
            def RC = jarsCSV.withReader {
                CsvIterator csvFile = CsvParser.parseCsv( it );
                for( csvRec in csvFile ) {

                    /* Set up default values for this new record. */

                    String jarName = "";
                    String project = "";

                    /* Pull out any values provided (templated code). */

                    Map cols = csvRec.properties.columns;
                    if( cols.containsKey( 'jarName'   ) && !noValue( csvRec.jarName   ) ) jarName      = csvRec.jarName     ;
                    if( cols.containsKey( 'project'   ) && !noValue( csvRec.project   ) ) project      = csvRec.project     ;

                    if( fullLog ) println( "Jar ${jarName} into ${project}" );
                    // Iterator lies and claims there is a next when there isn't.  Force break on empty state.
                    uploadList.add(
                            new JarRecord( jarName: jarName, project: project ) );
                }
            }
            if( fullLog ) println( "Read ${uploadList.size()} jar file records." );
        }

    }

    Boolean noValue( var ) {
        return var == null || var == '';
    }

    private boolean uploadJars( ) {
        for( rec in uploadList ) {
            File jarFile = new File( sourceDir + '/' + rec.jarName );
            String dest = domain + '/' + rec.project + '/' + value + '/' + rec.jarName;
            UploadableArtifact uploadHnd = repo.upload( dest, jarFile );

            if( uploadHnd != null ) {
                String result = "Not completed, dryRun";
                if( !dryRun ) {
                    def ret = uploadHnd.doUpload();
                    result = ret.created;
                }
                numProcessed += 1
                if( fullLog ) println("Upload of ${jarFile} to ${dest} gave ${result}.");
            }


        }
        return true;                              // We always process all nodes which are end nodes
    }

   private <T> T withClient( @ClosureParams( value = SimpleType, options = "org.jfrog.artifactory.client.Artifactory" ) Closure<T> closure ) {
        def client = ArtifactoryClient.create( "${webServer}artifactory", userName, password )
        try {
            return closure( client )

        } finally {
            client.close()
        }
    }
}
