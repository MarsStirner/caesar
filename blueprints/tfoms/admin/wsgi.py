# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from blueprints.tfoms.admin.app import app as application

if __name__ == '__main__':
    application.run(host='127.0.0.1', port=5500)