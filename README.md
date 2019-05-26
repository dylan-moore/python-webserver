DSWS (Dylan's simple web server) - This name is not final and may change, same with everything on this project. 
ALPHA v0.2

DSWS is a simple python web server designed to be deployed within seconds of being downloaded.

How to configure:
    
    DSWS has been designed to be as user friendly to use as possible.
        1) Clone this git repository into a directory.
        2) Make sure your machine has atleast python 3.6 installed (due to fstrings being introduced in 3.6)
        3) Configure the server to your needs (how to use the config file documentation down below)
        4) Run the server using python.

Config file:
The config file is in the same directory as server.py by default, you can also load a different config file by adding it as a console argument when starting the script.
The config file uses the JSON format.

    Data in parenthesis is the datatype and default that will be used if not set in config file.
        - port (integer : 80)
            This is the port the server will listen on.
        - localonly (boolean : false):
            If this is true then the server will only listen for localhost connections.
        - debug (boolean : false)
            If this is true then the server will output debug information that would be useful in congunction with the scripting.
        - fileslocation (string : 'www')
            This is the folder the webserver will look for files to serve.
        - scripting (boolean : false)
            If this is true then scripting will be enabled.
        - buffersize (in kb)(integer : 128)
            This is the buffer size that the server will use for network communications, its best to leave it at its default.
        - redirects (dict : none)
            This is a dictionary of redirects the server will serve, so '/':'index.html' would redirect the '/' route to 'index.html'. This also supports error codes, so '404':'404.html' would redirect 404 errors to '404.html'
        - cache_enabled (boolean : false)
            If this is enabled then (all) files will be cached in memory.
        - cache_specific (dict : none)
            This is a dictionary that specifies all specific files / formats to be cached. supports wildcards.
        - logging_enabled (boolean : true)
            If this is enabled then the server will log its actions.
        - logging_onlyfatal (boolean : false)
            If this is enabled then the server will only log fatal errors.
        - logging_file (string : 'server.log')
            This is the file the server will log into.

Current features:
    
    - Fast, stable webserver.
    - Decent scripting support.

Feature roadmap:
    
    - Sessions and post / get variables accessible by scripting.
    - Caching system
    - Ability to serve other filetypes (images etc...)
    - Better error logging / handling
    - Clean up code alot more!

Update notes:
    
    - ALPHA v0.1 (~ September 2018)
        - The simple webserver is now working.
        - Webpages are being loaded from file.

    - ALPHA v0.2 (26th May 2019)
        - Resumed development after huge initial break.
        - Cleaned up code massively.
        - Switched to being single threaded (too many reasons to list...)
        - Added scripting support.
        - Added config file.
        - Started working on logging.