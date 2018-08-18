# This file is part aeat_347 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from sql.functions import Substring
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond import backend
from trytond.transaction import Transaction

__all__ = ['Party', 'PartyIdentifier']


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'
    include_347 = fields.Boolean('Include on 347', depends=['identifiers'])

    @fields.depends('identifiers', 'include_347')
    def on_change_with_include_347(self, name=None):
        if self.include_347:
            return True
        for identifier in self.identifiers:
            if (identifier.type == 'eu_vat'
                    and identifier.code
                    and identifier.code[:2] == 'ES'):
                return True
        return False

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().connection.cursor()
        table = TableHandler(cls, module_name)

        created_347 = table.column_exist('include_347')

        super(Party, cls).__register__(module_name)

        # We need to reload table as it may be modified by __register__
        table = TableHandler(cls, module_name)
        if (not created_347 and table.column_exist('include_347')):
            sql_table = cls.__table__()
            identifier = Pool().get('party.identifier').__table__()
            query = identifier.select(identifier.party, where=Substring(
                    identifier.code, 1, 2) == 'ES')
            cursor.execute(*sql_table.update(
                    columns=[sql_table.include_347], values=[True],
                    where=(sql_table.id.in_(query))))


class PartyIdentifier(metaclass=PoolMeta):
    __name__ = 'party.identifier'

    @classmethod
    def create(cls, vlist):
        Party = Pool().get('party.party')

        to_write = []
        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            if (vals.get('type' == 'eu_vat') and vals['code'][:2] == 'ES'):
                to_write.append(vals['party'])

        if to_write:
            Party.write(to_write, {'include_347': True})

        return super(PartyIdentifier, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)

        to_write = []
        for parties, vals in zip(actions, actions):
            if (vals.get('type' == 'eu_vat') and vals['code'][:2] == 'ES'):
                to_write.append(vals['party'])

        if to_write:
            Party.write(to_write, {'include_347': True})

        return super(PartyIdentifier, cls).write(*args)
