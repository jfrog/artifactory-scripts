# logsIPMasker
The purpose of this shell script is to mask IP addresses from all files in a directory.
It will recursively extract any archive to search in the included files, and finally will pack the masked files back into a Zip archive.

Do not run directly on important directories or log directories of production applications. 

Instead, copy the files/ or provide a support bundle you plan to mask on a dedicated folder which you will provide to the script. 
You will be prompted for a BUNDLE_DIR. You should provide the path to the dedicated folder you wish the script to run on.

The script will replace all patterns matching `\([0-9]\{2,3\}\.\)\{3,3\}[0-9]\{1,3\}` and replace them with `x.x.x.x`.

You are welcome to contribute and enhance the capabilities of this script.


# scrubIPandUserID
Includes the logsIPMasker script as described above and in addition to that it will also scrub the UserID from the logs

PLEASE NOTE: This script has specific 'sed' command that will work on Ubuntu/Redhat but will not work on MacOS. 
