#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
from datetime import datetime
from flask import Flask, render_template, flash, request, redirect, url_for, abort
from wtforms import StringField, SubmitField
from flask.ext.wtf import Form
from wtforms.fields.html5 import URLField
from wtforms.validators import url, DataRequired
from flask.ext.sqlalchemy import SQLAlchemy

from checkercore.checker import UrlUtils


app = Flask(__name__)
app.config.from_pyfile('server.cfg')
db = SQLAlchemy(app)


def get_or_abort(model, object_id, code=404):
    result = model.query.get(object_id)
    return result or abort(code)


class CategoryForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class FileForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    url = URLField("Url", validators=[url()])
    submit = SubmitField('Save')


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=False)
    url = db.Column(db.String(512), unique=False)
    hash = db.Column(db.String(36), unique=False)
    date = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('files', lazy='dynamic'))

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


@app.route('/files')
def files_all():
    files = File.query.all()
    form = FileForm()
    return render_template('files_all.html', files=files, form=form, new=True)


@app.route('/files/new', methods=['POST'])
def files_new():
    if request.method == 'POST':
        form = FileForm()
        if form.validate():
            file = File()
            form.populate_obj(file)
            file.hash = UrlUtils.UrlUtil.get_crc_by_url(form.url.data)
            if file.hash in [-1, -2, -3]:
                flash('Hash calculation failed', 'error')
            else:
                db.session.add(file)
                db.session.commit()
                flash('File was successfully posted!')
        else:
            flash('Error posting file', 'error')
    return redirect(url_for('files_all'))


@app.route('/categories')
def cats_all():
    cats = Category.query.all()
    form = CategoryForm()
    return render_template('cats_all.html', cats=cats, form=form, new=True)


@app.route('/categories/new', methods=['POST'])
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
            flash("Error posting category!", "error")

        return redirect(url_for('cats_all'))


@app.route('/categories/edit/<int:id>', methods=['POST', 'GET'])
def cats_edit(id):
    if request.method == "POST":
        cat = get_or_abort(Category, id)
        form = CategoryForm(obj=cat)
        if form.validate():
            form.populate_obj(cat)
            db.session.add(cat)
            db.session.commit()
            flash("Category was successfully updated!")
        else:
            flash('Error updating category!', 'error')

        return redirect(url_for('cats_all'))

    else:
        cat = get_or_abort(Category, id)
        form = CategoryForm(obj=cat)
        return render_template('cats_all.html', form=form)


if __name__ == '__main__':
    app.run()

