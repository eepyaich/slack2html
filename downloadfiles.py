import re
import requests
import os
import errno
from pathlib import Path
import sys, getopt

def downloadfile( filegroup, basedir, subdir ):
    """
    Download an individual file and store it locally, if it doesn't already exist.

    Parameters:
    filegroup (group): group object containing the full URL from Slack and parsed filename
    basedir (string): base directory for the files
    subdir (string): subdirectory in which to store the files

    Returns:
    string: reference to the downloaded file 
    
    """
    print ( "Processing " + filegroup.group("url"))

    # Set up the URLs
    # abs_url is the full path to the new URL
    # relative_url is the path relative to the basedir (returned to be used in the HTML)
    abs_url = Path(basedir, subdir, filegroup.group("file"))
    relative_url = Path(".", subdir, filegroup.group("file"))
    
    # If the file is not already there, then download it
    if not os.path.exists(abs_url):
        downloadedfile = requests.get(filegroup.group("url"))

        # create the directory for the file
        if not os.path.exists(os.path.dirname(abs_url)):
            try:
                os.makedirs(os.path.dirname(abs_url))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        
        # write the file
        print("Writing file "+str(abs_url))
        open(abs_url, 'wb').write(downloadedfile.content)
    else:
        print(str(abs_url) + " already exists")
    return relative_url


def downloadfiles (inputname, outputname):
    """
    Parse HTML file and download files from  Slack to a local directory and create new HTML with updated references.
    
    Parameters:
    inputname (string): Filename for the input file containing references to files.slack
    outputname (string): Filename for the output, which will have updated references

    """
    print ("Processing " + inputname)
    
    file = open(inputname)
    output = open(outputname, 'w')

    # Work through each line in the input file
    for line in file:
        urls = re.findall(r'https?:\/\/(?:[-\w.]|(?:%[\da-fA-F]{2}))+', line)
        if len(urls) != 0:
            # Found a line with a URL in it, now look for references to private files stored on Slack
            pri = re.search(r"(?P<url>https?:\/\/files.slack.com\/files-pri\/(?P<file>[^\s'\"]+)(\?t=[^\"]+))", line) 
            if pri is not None:
                new_url = downloadfile(pri, os.path.dirname(inputname), "pri_files")
                # Update the URLs in the output to reference the local file
                line = line.replace(pri.group("url"), str(new_url))

            # Now look for references to thumbnail files stored on Slack
            tmb = re.search(r"(?P<url>https?:\/\/files.slack.com\/files-tmb\/(?P<file>[^\s'\"]+)(\?t=[^\"]+))", line) 
            if tmb is not None:
                new_url = downloadfile(tmb, os.path.dirname(inputname), "tmb_files")
                # Update the URLs in the output to reference the local file
                line = line.replace(tmb.group("url"), str(new_url))

        # Write out the local version of the HTML file
        output.write(line)

    return

def walkdirectories(channeldir):
    """
    Takes a directory containing Slack channel exports, downloads files stored in Slack and creates a local channel index

    Parameters:
    channeldir (string): The channel directory of an export (as produced by slack2html.py)

    """    # given a base channel directory
    # go through each subdirectory
    directories = next(os.walk(channeldir))[1]

    for directory in directories:
        inputfile = Path(channeldir, directory, "index.html")
        outputfile = Path(channeldir, directory, "index_local.html")
        downloadfiles(str(inputfile), str(outputfile))

def main(argv):
    """
    Takes a directory containing Slack channel exports, downloads files stored in Slack and creates a local channel index

    Arguments:
    <channeldir> (default = "./"): The channel directory of an export (as produced by slack2html.py)

    """    
    channeldir = './'

    try:
        opts, _args = getopt.getopt(argv, "hc:", ["cdir="])
    except getopt.GetoptError:
        print ('downloadfiles.py -c <channeldir>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ('downloadfiles.py -c <channeldir>')
            sys.exit()
        elif opt in ("-c", "--cdir"):
            channeldir = arg

    walkdirectories(channeldir)

if __name__ == "__main__":
    main(sys.argv[1:])
