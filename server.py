#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for, abort
from wtforms import StringField, SubmitField
from flask.ext.wtf import Form
#from wtforms.fields.html5 import URLField
from wtforms.validators import url, DataRequired
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('server.cfg')
db = SQLAlchemy(app)


def get_or_abort(model, object_id, code=404):
    result = model.query.get(object_id)
    return result or abort(code)


class CategoryForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')


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

    #def __init__(self, name):
    #    self.name = name

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
def index():
    return render_template("index.html")


@app.route('/cats')
def cats_all():
    cats = Category.query.all()
    form = CategoryForm()
    return render_template('cats_all.html', cats=cats, form=form, new=True)


@app.route('/cats/new', methods=['POST'])
def cats_new():
    if request.method == 'POST':
        form = CategoryForm()

        if form.validate():
            cat = Category()
            form.populate_obj(cat)
            db.session.add(cat)
            db.session.commit()
            flash("New category was successfully posted!")
        else:
            flash("Error posting category!")

        return redirect(url_for('cats_all'))


@app.route('/cats/edit/<int:id>', methods=['POST', 'GET'])
def cats_edit(id):
    if request.method == "POST":
        cat = get_or_abort(Category, id)
        form = CategoryForm(obj=cat)
        if form.validate():
            form.populate_obj(cat)
            db.session.add(cat)
            db.session.commit()
        return redirect(url_for('cats_all'))

    else:
        cat = get_or_abort(Category, id)
        form = CategoryForm(obj=cat)
        return render_template('cats_all.html', form=form)


@app.route('/event-types')
def event_types_all():
    return render_template('event_types_all.html',
                           event_types=EventType.query.all())


@app.route('/event-types/new', methods=['GET', 'POST'])
def event_types_new():
    if request.method == 'POST':
        if not request.form['name']:
            flash('Name is required', 'error')
        else:
            # TODO: strin tags, etc. || re.sub('<[^<]+?>', '', text)
            name = request.form['name']
            event_type = EventType(name)
            db.session.add(event_type)
            db.session.commit()
            flash('New event created')
            return redirect(url_for('event_types_all'))
    return render_template('event_types_new.html', mode='New')


@app.route('/event-types/edit/<int:evt_id>', methods=['GET', 'POST'])
def event_types_edit(evt_id):
    if request.method == 'POST':
        event_type = get_or_abort(EventType, evt_id)
        name = request.form['name']
        event_type.name = name
        db.session.add(event_type)
        db.session.commit()
    else:
        event_type = get_or_abort(EventType, evt_id)
        request.form.name = event_type.name
        return render_template('event_types_new.html', mode="Edit")

    return redirect(url_for('event_types_all'))


if __name__ == '__main__':
    app.run()

