#!/usr/bin/env python3
#
# A *bookmark server* or URI shortener that maintains a mapping (dictionary)
# between short names and long URIs, checking that each new URI added to the
# mapping actually works (i.e. returns a 200 OK).
#
# This server is intended to serve three kinds of requests:
#
#   * A GET request to the / (root) path.  The server returns a form allowing
#     the user to submit a new name/URI pairing.  The form also includes a
#     listing of all the known pairings.
#   * A POST request containing "longuri" and "shortname" fields.  The server
#     checks that the URI is valid (by requesting it), and if so, stores the
#     mapping from shortname to longuri in its dictionary.  The server then
#     redirects back to the root path.
#   * A GET request whose path contains a short name.  The server looks up
#     that short name in its dictionary and redirects to the corresponding
#     long URI.


import os
import http.server
import requests
from urllib.parse import unquote, parse_qs
from socketserver import ThreadingMixIn


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
	"""This is an HTTPServer that supports thread-based concurrency."""

# Create very basic memory dictionary - will not last between sessions.
memory = {}

# Create very basic HTML form to be served to client
form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<h1>Basic Server using Python http.server</h1>
<p>Created by Doug Wight</p>
<h2>Instructions</h2>
<p>You type in the Long URL of a site you want to store</p>
<p>And also the short name for it</p>
<p>Then if you want to go quickly to that URL, just append /short-name</p>

<form method="POST">
	<label>Long URI:
		<input name="longuri">
	</label>
	<br>
	<label>Short name:
		<input name="shortname">
	</label>
	<br>
	<button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''


def checkURI(uri, timeout=5):
	"""Check whether this URI is reachable, i.e. does it return a 200 OK?

    This function returns True if a GET request to uri returns a 200 OK, and
    False if that GET request returns any other response, or doesn't return
    (i.e. times out).
    """

	try:
		r = requests.get(uri, timeout=timeout)
		print('r.status_code: ' + str(r.status_code))
		return r.status_code == 200

	except requests.RequestException:
		print("could not check URI")
		return False


class Shortener(http.server.BaseHTTPRequestHandler):
	def do_GET(self):
		# A GET request will either be for / (the root path) or for /some-short name.

		name = unquote(self.path[1:])

		if name:
			if name in memory:
				# Send a 303 redirect to the long URI in memory[name].
				self.send_response(303)
				self.send_header('Location', memory[name])  # this is where to redirect the browser to.
				self.end_headers()

			else:
				# We don't know that name! Send a 404 error.
				self.send_response(404)
				self.send_header('Content-type', 'text/plain; charset=utf-8')
				self.end_headers()
				self.wfile.write("I don't know '{}'./nPerhaps you forgot to include"
								 "the 'https://' at the start?".format(name).encode())
		else:
			# Root path. Send the form.
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			# List the known associations in the form.
			known = "\n".join("{} : {}".format(key, memory[key])
							  for key in sorted(memory.keys()))
			self.wfile.write(form.format(known).encode())

	def do_POST(self):
		# Decode the form data.
		length = int(self.headers.get('Content-length', 0))
		body = self.rfile.read(length).decode()
		params = parse_qs(body)

		# check to see if both the longuri and shorturi have been filled in
		if not ('longuri' in params.keys() and 'shortname' in params.keys()):
			# Form did not have both fields filled in
			# Send a 404 error with a useful message.
			self.send_response(404)
			self.send_header('Content-type', 'text/plain; charset=utf-8')
			self.end_headers()
			self.wfile.write("Please fill in both parts of the form".encode())

		longuri = params["longuri"][0]
		shortname = params["shortname"][0]

		if checkURI(longuri):
			# This URI is good!  Remember it under the specified name.
			memory[shortname] = longuri

			# 3. Serve a redirect to the root page (the form).
			self.send_response(303)
			self.send_header('Location', '/')  # this is where to redirect the browser to.
			self.end_headers()

		else:
			# Didn't successfully fetch the long URI.

			# 4. Send a 404 error with a useful message.
			self.send_response(404)
			self.send_header('Content-type', 'text/plain; charset=utf-8')
			self.end_headers()
			self.wfile.write("We could not find that URI {} - did you check it works first?".format(longuri).encode())


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8000))
	# So the program checks os.environ.get('PORT') - if on Heroku, will be given a port
	# if it's not on Heroku (or other server), then it won't find a port - so give it 8000,
	# which is the local port. So this will
	# check to see if it runs on server - if not, default to local.
	server_address = ('', port)
	httpd = ThreadHTTPServer(server_address, Shortener)
	print('HTTPServer listening on port: ' + str(port))
	httpd.serve_forever()
