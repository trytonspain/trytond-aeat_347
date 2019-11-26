# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['TaxTemplate', 'Tax']

OPERATION_347 = [
    (None, ''),
    ('base_amount', 'Include Base Amount'),
    ('amount_only', 'Amount Only'),
    ('ignore', 'Ignore'),
    ('exclude_invoice', 'Exclude Invoice')]


class TaxTemplate(metaclass=PoolMeta):
    __name__ = 'account.tax.template'

    operation_347 = fields.Selection(OPERATION_347, 'Operation for 347')

    @staticmethod
    def default_operation_347():
        return 'ignore'

    def _get_tax_value(self, tax=None):
        res = super(TaxTemplate, self)._get_tax_value(tax)

        if not tax or tax.operation_347 != self.operation_347:
            res['operation_347'] = self.operation_347
        return res


class Tax(metaclass=PoolMeta):
    __name__ = 'account.tax'

    operation_347 = fields.Selection(OPERATION_347, 'Operation for 347')
