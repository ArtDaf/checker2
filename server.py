#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False)
    url = db.Column(db.String(512), unique=False)
    hash = db.Column(db.String(36), unique=False)
    date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                backref=db.backref('files', lazy='dynamic'))

    def __init__(self, name, url, hash, category, date=None):
        self.name = name
        self.url = url
        self.hash = hash
        if date is None:
            date = datetime.utcnow()
        self.category = category

    def __repr__(self):
        return '<File %d %r>' % (self.id, self._name)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name


class EventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name  = name

    def __repr__(self):
        return '<EventType %r>' % self.name


class ResultType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ResultType %r>' % self.name


@app.route('/')
def hello():
    return 'Index page'


if __name__ == '__main__':
    app.run()

