# -*- coding: utf-8 -*-

__author__ = 'viruzzz-kun'

from application.app import app
from caesar.blueprints.print_subsystem.app import module as ps_module

app.register_blueprint(ps_module, url_prefix='/print_subsystem')


if __name__ == '__main__':
    app.run(port=app.config['SERVER_PORT'])