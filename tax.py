# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond import backend
from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from sql.operators import In
from .aeat import OPERATION_KEY

__all__ = ['Tax']


class Tax:
    __metaclass__ = PoolMeta
    __name__ = 'account.tax'

    include_347 = fields.Boolean('Include 347')

    @staticmethod
    def default_include_347():
        return True
