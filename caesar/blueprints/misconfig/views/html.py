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


@module.route('/org/')
def org_html():
    return render_template('misconfig/org.html')


@module.route('/expert/protocol/index/')
def expert_protocol_index_html():
    return render_template('misconfig/expert/protocol/index.html')


@module.route('/expert/protocol/measures/')
def expert_protocol_measures_html():
    return render_template('misconfig/expert/protocol/measure-list.html')


@module.route('/expert/protocol/protocols/')
def expert_protocol_protocols_html():
    return render_template('misconfig/expert/protocol/protocol-list.html')


@module.route('/expert/protocol/protocols/protocol/')
def expert_protocol_protocol_html(protocol_id=None):
    return render_template('misconfig/expert/protocol/protocol-edit.html')