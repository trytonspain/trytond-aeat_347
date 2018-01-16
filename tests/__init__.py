# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.aeat_347.tests.test_aeat_347 import suite
except ImportError:
    from .test_aeat_347 import suite

__all__ = ['suite']
