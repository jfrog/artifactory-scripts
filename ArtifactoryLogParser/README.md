# Artifactory Log Parser
A script that allows to parse Artifactory logs and output them in a
readable and organized way.


## Installation and Configuration
No external dependencies are necessary. <p>
Code has been tested and optimized for Pyhton 2.7 or Python 3.6 running
on Unix systems. Coloring might not work on Windows machines.


## Usage
To run the script you must simply pass the file path along with options
and search filters. The filters\options available are the following: <p>
`WARN`, `ERROR`, `INFO`, `nocolor` <p>


Example commands:

`python artifactory.py /path/to/artifactory.log WARN` <p>
`python artifactory.py /path/to/artifactory.log ERROR WARN` <p>
`python artifactory.py /path/to/artifactory.log ERROR nocolor` <p>

Under construction (only functional with Python 2.7.
No advanced options):

`python access.py /path/to/access.log` <p>
`python request.py /path/to/request.log` <p>
