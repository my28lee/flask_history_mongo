#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask.ext.pymongo import PyMongo
from flask.ext.script import Manager

# from werkzeug.contrib.fixers import ProxyFix

from app import create_app

import sys
reload(sys)
sys.setdefaultencoding('UTF8')

app = create_app()
app.config.from_object({"DEBUG":"True","SECRET_KEY":"hellogit00"})

# app.wsgi_app = ProxyFix(app.wsgi_app)
manager = Manager(app)


@manager.command
def run():
    app.run(host='0.0.0.0',port=80)

if __name__ == "__main__":
    manager.run()