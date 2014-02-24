#This file is part of aeat_347 module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.

from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Party']
__metaclass__ = PoolMeta

class Party:
    __name__ = 'party.party'

    include_347 = fields.Function(fields.Boolean('Include on 347',
        on_change_with=['vat_country'], depends=['vat_country']),
        'on_change_with_include_347')

    def on_change_with_include_347(self, name=None):
        if self.vat_country == 'ES':
            return True
        return False

