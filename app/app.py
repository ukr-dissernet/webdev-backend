# -*- coding: utf-8 -*-
from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4
import app.project as project
import sys

#reload(sys)
#sys.setdefaultencoding("utf-8")

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/index_contacts')
def contacts():
    return  render_template("index_contacts.html")

@app.route('/index_blog')
def blog():
    return  render_template("index_blog.html")

@app.route('/index_about')
def about():
    return  render_template("index_about.html")

@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "app/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    print("=== Form Data ===")
    for key, value in form.items():
        print(key, "=>", value)

    # upload = request.files['file_ukr']
    # filename = 'file_ukr'
    # destination = "/".join([target, filename])
    # print "Accept incoming file:", filename
    # print "Save it to:", destination
    # upload.save(destination)
    #
    # upload = request.files['file_source']
    # filename = 'file_source'
    # destination = "/".join([target, filename])
    # print "Accept incoming file:", filename
    # print "Save it to:", destination
    # upload.save(destination)
    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)
        
    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))

@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "app/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    #try:
    return render_template("files.html",
        uuid=uuid,
        files=project.project(os.path.join(root, files[0]), os.path.join(root, files[1]))
    )
    #except:
        #return redirect(url_for("index"))

def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))
