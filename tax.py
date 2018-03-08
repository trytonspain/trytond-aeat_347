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

__all__ = ['TaxTemplate', 'Tax']


class TaxTemplate:
    __metaclass__ = PoolMeta
    __name__ = 'account.tax.template'

    include_347 = fields.Boolean('Include 347')

    @staticmethod
    def default_include_347():
        return True

    def _get_tax_value(self, tax=None):
        res = super(TaxTemplate, self)._get_tax_value(tax)

        if not tax or tax.include_347 != self.include_347:
            res['include_347'] = self.include_347
        return res


class Tax:
    __metaclass__ = PoolMeta
    __name__ = 'account.tax'

    include_347 = fields.Boolean('Include 347')

    @staticmethod
    def default_include_347():
        return True
