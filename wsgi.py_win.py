# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

activate_this = os.path.join(os.path.join(os.path.dirname(__file__), '..'), 'venv', 'Scripts', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from application.app import app as application

if __name__ == '__main__':
    application.run()