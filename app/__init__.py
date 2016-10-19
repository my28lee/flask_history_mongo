#!/usr/bin/python
# -*- coding:utf-8 -*-
import re

from flask import Flask, Markup, escape
from flask.ext.pymongo import PyMongo
from jinja2.filters import evalcontextfilter

from app_middleware import HTTPMethodOverrideMiddleware

app = Flask(__name__)
app.config['MONGO_HISTORY_DBNAME'] = 'dbHistory'
app.config['MONGO_HISTORY_HOST'] = '127.0.0.1'
app.config['MONGO_HISTORY_PORT'] = 27017

mongo = PyMongo(app,config_prefix='MONGO_HISTORY')

#app.jinja_env.autoescape = False
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

def create_app():
    from history import historyApp
    app.register_blueprint(historyApp)

    # method overwrite
    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    return app

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'%s<br>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(value))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result