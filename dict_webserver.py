#!/usr/bin/env python

__version__ = ""
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = ""
__home_page__ = ""

import os
import sys
import posixpath
import BaseHTTPServer
import urllib
import cgi
import shutil
import mimetypes
import re
import time
import subprocess

PORT="8263"

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class SimpleHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    server_version = "DictionaryWebServer/" + __version__
    def get_formatted_result(self, given_word):
	proc=subprocess.Popen("bash",shell=False,
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	(out,err)= proc.communicate("dict "+ given_word)
	if out == "":
		res=err
	else:
		res=out

	res=res.replace("\n","<br/>")
	res=res.replace('\\',"\\\\")
	res=res.replace("\"","\\\"")
	
	#print(res)
	return res

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        f = self.send_head()
        if f:
            f.close()
            
    def send_head(self):
        path = self.translate_path(self.path)
#	print("path="+path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            index = os.path.join(path, "dict_webclient.html")
            if os.path.exists(index):
                    path = index
                    
        
	myword=os.path.basename(path)
	meaning=0
	if myword.find(".json") != -1:
		meaning=myword
		#print(".json found")
		myword=myword.replace(".json", "")
		print("Given word : "+myword)
	else:
		path=path.replace(myword,"dict_webclient.html")

	ctype = self.guess_type(path)
        try:
            if meaning:
            	f = StringIO()
		result=self.get_formatted_result(myword)
		mydata='{"data":"%s" }' % (result)
            	f.write(mydata)
		cont_len=len(mydata)
		last_mod=time.time()
            	f.seek(0)
            else:
                f = open(path, 'rb')
		fs = os.fstat(f.fileno())
		cont_len=str(fs[6])
		last_mod=fs.st_mtime
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
# Following single line converts this server into a CORS server
	self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", cont_len)
        self.send_header("Last-Modified", self.date_time_string(last_mod))
        self.end_headers()
        return f

   
    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()


def test(HandlerClass = SimpleHTTPRequestHandler,
         ServerClass = BaseHTTPServer.HTTPServer):
    BaseHTTPServer.test(HandlerClass, ServerClass)
#This runs the http server at port 8000 or the first command line argument

if __name__ == '__main__':
 sys.argv=["",PORT]
 test()
