# -*- coding: utf-8 -*-

from os import getuid
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from Flask!"


if __name__ == "__main__":
    app.run(port=getuid() + 1000)
