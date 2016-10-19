#!/usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask.ext.pymongo import PyMongo

historyApp = Blueprint('historyApp', __name__)

from . import views