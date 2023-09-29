from flask import Flask, make_response, redirect, session, Response, stream_with_context
import pickle
import os
import platform
import requests

app = Flask(__name__)

dir = "/storage/emulated/0/download/"
if platform.system() == 'Windows':
	dir = "download/"

def make_session(new=False):
	if new:
		sp = open(dir+'.s.pkl','wb')
		try:
			r = requests.get("http://apiserver.alwaysdata.net/new")
		except:
			r = requests.get("http://apiserver.alwaysdata.net/new")
		for i in r.iter_content(1024*1024):
			sp.write(i)
		sp.close()
		with open(dir+'.s.pkl','rb') as f:
			s = pickle.load(f)
			return s
	if not os.path.exists(dir+'.s.pkl'):
		make_session(new=True)
	with open(dir+'.s.pkl','rb') as f:
		s = pickle.load(f)
		return s

@app.route("/<filesize>/<token>/<filename>")
def index(filesize,token,filename):
	session = make_session()
	url = f"https://nube.uo.edu.cu/remote.php/dav/uploads/A875BE09-18E1-4C95-9B84-DD924D2781B7/web-file-upload-{token}/.file"
	resp = session.get(url,stream=True)
	return Response(stream_with_context(resp.iter_content(chunk_size=1024)),
		headers={'Content-Length':str(filesize),'Content-Disposition': f'attachment; filename={filename}'})

if __name__ == "__main__":
	app.run(port=5000)