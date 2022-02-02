# Bookmark-server
## A simple server using Python http.server

### Aim
* Create a simple server to serve up a basic HTML form
* Uses localhost.
* Responds to GET and POST requests.
* Stores the information from POST in very simple local memory
* Serves up that information
* Uses the following packages / concepts:
  * Python's http.server
  * requests package for handling HTTP info
  * Sending of correct response codes
  * Sending of header information
  * Use of wfile and rfile to send and receive body information
  * Use of re-direct (303 code plus new location info)
  * Use of .encode().
    * This is an in-built method of str, used to convert string format to binary
required when sending over HTML.

### Setup
* This project used Python3
* Packages required are noted in requirements.txt
* Install using   
`pip3 install -r requirements.txt`

### Running
* At commandline enter the following:
`python BookmarkServer.py`
* The command line should then tell you that the HTTPServer is listening on port:8000
* Swap to a browser and enter:
`locahhost:8000/`

### Usage
* This is a very basic server!
* But it should be able to do the following:
* Store pairs of long URL / short-names, as long as the long URL is valid
* Display the list of long URL / short-name pairs
* On entering `localhost:8000/short-name`, it should then re-direct you
to the correct longURL (as long as that short-name is in the memory)
* The memory is not permanent - it will wipe each time you stop the server.

### History
* Code originally developed on Udacithy Full Stack Web Developer Nanodegree.

### Heroko
* There are files included that are related to Heroko - need to check that these still work
  * Procfile
  * Runtime.txt


