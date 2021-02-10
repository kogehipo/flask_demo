# coding: utf-8
 
from flask import Flask, Blueprint, render_template
 
app = Blueprint('pageswitch', __name__, \
        url_prefix='/flask_demo/pageswitch', \
        template_folder='pageswitch_templates')

@app.route("/")
def index():
    return render_template("pageswitch.html", page="menu")
 
@app.route("/page1")
def page1():
    return render_template("pageswitch.html", page="page1")
 
@app.route("/page2")
def page2():
    return render_template("pageswitch.html", page="page2")
 
if __name__ == "__main__":
    app.run(debug=True)
