from flask import Flask, request, redirect, url_for, send_from_directory
from pycurl import Curl
from io import BytesIO
import certifi
import os
from utils import random_filename
from urllib.parse import urlparse

"""
The World's COOLEST File Upload Service! Allows people to upload files from URLs for the world to see!
Served at www.da_coolest_website.com!
"""
UPLOAD_FOLDER = '/path/to/uploads' # Outside of webroot!
# Really don't want people to be see the content of these pages!
# For extra security, I've configured the server to only allow access to these pages from localhost!
BANNED_ADDRESSES = ["admin.da_coolest_website.com", "config.da_coolest_website.com"]
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['BANNED_ADDRESSES'] = BANNED_ADDRESSES
@app.route('/oops')
def oops():
    return 'Oops! Something went wrong!'

# Process POST request
@app.route('/upload', methods = ['POST'])
def upload_file():
	if request.method == 'POST':
		url = request.form['url']
		if not url.lower().startswith("http"):
			return redirect(url_for('oops'))
		for address in app.config['BANNED_ADDRESSES']:
			if address in urlparse.unquote(url):
				return redirect(url_for('oops'))
		buf = BytesIO()
		c = Curl()
		c.setopt(c.URL, url)
		c.setopt(c.CAINFO, certifi.where())
		c.setopt(c.FOLLOWLOCATION, 1)
		c.setopt(c.WRITEDATA, buf)
		c.perform()
		c.close()
		name = random_filename()
		with open(os.path.join(app.config['UPLOAD_FOLDER'], name), "wb") as f:
			f.write(buf.getbuffer())
		return redirect(url_for('download_file', name=name))
	return redirect(url_for('oops'))
@app.route('/uploads/<name>')
def download_file(name):
	return send_from_directory(app.config["UPLOAD_FOLDER"], name)



