# -*- coding: utf-8 -*-
from flask import render_template
from ..app import module

__author__ = 'viruzzz-kun'


@module.route('/')
def index_html():
    return render_template('misconfig/index.html')


@module.route('/htmc/')
def htmc_html():
    return render_template('misconfig/htmc.html')


@module.route('/rb/')
def rb_html():
    return render_template('misconfig/rb.html')