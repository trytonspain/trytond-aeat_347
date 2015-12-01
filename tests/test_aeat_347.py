# This file is part of the aeat_347 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class Aeat347TestCase(ModuleTestCase):
    'Test Aeat 347 module'
    module = 'aeat_347'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        Aeat347TestCase))
    return suite