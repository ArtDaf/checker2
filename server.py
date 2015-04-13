#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for, session, abort
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
    category = db.relationship('Category', backref=db.backref('files', lazy='dynamic'))

    def __init__(self, name, url, hash, category, date=None):
        self.name = name
        self.url = url
        self.hash = hash
        if date is None:
            date = datetime.utcnow()
        self.category = category
        self.date = date

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
    __tablename__ = 'event_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<EventType %r>' % self.name


class ResultType(db.Model):
    __tablename__ = 'result_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<ResultType %r>' % self.name


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'))
    event_type = db.relationship('EventType', backref=db.backref('events', lazy='dynamic'))
    result_type_id = db.Column(db.Integer, db.ForeignKey('result_type.id'))
    result_type = db.relationship('ResultType', backref=db.backref('events', lazy='dynamic'))

    def __init__(self, event_type, result_type, date=None):

        self.event_type = event_type
        self.result_type = result_type

        if date is None:
            date = datetime.utcnow()
        self.date = date

    def __repr__(self):
        return '<Event %d>' % (self.id)


@app.route('/')
def hello():
    return 'Index page'


@app.route('/et')
def all_event_types():
    return render_template('all_evt_types.html',
                           event_types=EventType.query.all())


@app.route('/newet', methods=['GET', 'POST'])
def new_event_type():
    if request.method == 'POST':
        if not request.form['name']:
            #flash('Name is required', 'error')
            pass
        else:
            pass
            # TODO: strin tags, etc. || re.sub('<[^<]+?>', '', text)
            name = request.form['name']
            event_type = EventType(name)
            print event_type
            db.session.add(event_type)
            db.session.commit()
            #flash('Created!')
            return redirect(url_for('all_event_types'))
    return render_template('new_evt_type.html')



if __name__ == '__main__':
    app.run()

