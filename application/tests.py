# -*- coding: utf-8 -*-
import unittest
from application.app import app
from application.autoload import import_tests


def run_tests():
    tests = import_tests(app.config['BLUEPRINTS_DIR'])
    if tests:
        for module_test in tests:
            suite = unittest.TestLoader().loadTestsFromModule(module_test)
            unittest.TextTestRunner(verbosity=2).run(suite)