#This file is part of aeat_347 module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from sql import Literal
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond import backend
from trytond.transaction import Transaction

__all__ = ['Party']
__metaclass__ = PoolMeta


class Party:
    __name__ = 'party.party'

    include_347 = fields.Boolean('Include on 347', depends=['vat_country'])

    @fields.depends('vat_country')
    def on_change_with_include_347(self, name=None):
        if self.vat_country == 'ES':
            return True
        return False

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().cursor
        sql_table = cls.__table__()
        table = TableHandler(cursor, cls, module_name)

        created_347 = table.column_exist('include_347')

        super(Party, cls).__register__(module_name)

        #We need to reload table as it may be modified by __register__
        table = TableHandler(cursor, cls, module_name)
        if (not created_347 and table.column_exist('include_347')):
            cursor.execute(*sql_table.update(
                    columns=[sql_table.include_347], values=[True],
                    where=(sql_table.vat_country == Literal('ES'))))
