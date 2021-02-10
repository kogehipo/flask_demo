# coding: utf-8

from flask import Flask, render_template
from pageswitch import pageswitch
from addressbook import addressbook
from mplgraph import mplgraph
from filetransfer import filetransfer
from sensordata import sensordata
import os

app = Flask(__name__)
app.register_blueprint(pageswitch.app, url_prefix='/pageswitch')
app.register_blueprint(addressbook.app, url_prefix='/addressbook')
app.register_blueprint(mplgraph.app, url_prefix='/mplgraph')
app.register_blueprint(filetransfer.app, url_prefix='/filetransfer')
app.register_blueprint(sensordata.app, url_prefix='/sensordata')

@app.route("/")
def index():
    subdir = os.getenv('FLASK_SUBDIR', default='')
    return render_template('index.html', flask_subdir=subdir)
 
if __name__ == "__main__":
    app.run(debug=True)
