# This file is part aeat_347 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond import backend
from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from sql.operators import In
from .aeat import OPERATION_KEY

__all__ = ['Record', 'Invoice', 'InvoiceTax', 'Recalculate347RecordStart',
    'Recalculate347RecordEnd', 'Recalculate347Record', 'Reasign347RecordStart',
    'Reasign347RecordEnd', 'Reasign347Record']


class Record(ModelSQL, ModelView):
    """
    AEAT 347 Record

    Calculated on invoice creation to generate temporal
    data for reports. Aggregated on aeat347 calculation.
    """
    __name__ = 'aeat.347.record'

    company = fields.Many2One('company.company', 'Company', required=True,
        readonly=True)
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscal Year',
        required=True, readonly=True)
    month = fields.Integer('Month', readonly=True)
    party = fields.Many2One('party.party', 'Party',
        required=True, readonly=True)
    operation_key = fields.Selection(OPERATION_KEY, 'Operation key',
        required=True, readonly=True)
    amount = fields.Numeric('Operation Amount', digits=(16, 2),
        readonly=True)
    invoice = fields.Many2One('account.invoice', 'Invoice', readonly=True)
    party_record = fields.Many2One('aeat.347.report.party', 'Party Record',
        readonly=True)
    party_name = fields.Function(fields.Char('Party Name'), 'get_party_fields')
    party_vat = fields.Function(fields.Char('Party VAT'), 'get_party_fields')
    country_code = fields.Function(fields.Char('Country Code'),
        'get_party_fields')
    province_code = fields.Function(fields.Char('Province Code'),
        'get_party_fields')

    @classmethod
    def get_party_fields(cls, records, names):
        res = {}
        for name in ['party_name', 'party_vat', 'country_code',
                'province_code']:
            res[name] = dict.fromkeys([x.id for x in records], '')
        for record in records:
            party = record.party
            res['party_name'][record.id] = party.name[:39]
            res['party_vat'][record.id] = (party.tax_identifier.code[2:]
                if party.tax_identifier else '')
            res['country_code'][record.id] = (party.tax_identifier.code[:2] if
                party.tax_identifier else '')
            province_code = ''
            address = party.address_get(type='invoice')
            if address and address.zip:
                province_code = address.zip.strip()[:2]
            res['province_code'][record.id] = province_code
        for key in res.keys():
            if key not in names:
                del res[key]
        return res

    @classmethod
    def delete_record(cls, invoices):
        pool = Pool()
        Record = pool.get('aeat.347.record')
        with Transaction().set_user(0, set_context=True):
            Record.delete(Record.search([('invoice', 'in',
                            [i.id for i in invoices])]))


class Invoice:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice'

    include_347 = fields.Boolean('Include 347')
    aeat347_operation_key = fields.Selection([('', ''), ] + OPERATION_KEY,
        'AEAT 347 Operation Key',
        states={
            'invisible': ~Bool(Eval('include_347')),
            'required': Bool(Eval('include_347')),
            },
        depends=['include_347'])

    @classmethod
    def __register__(cls, module_name):
        pool = Pool()
        Record = pool.get('aeat.347.record')
        TableHandler = backend.get('TableHandler')

        cursor = Transaction().connection.cursor()
        table = TableHandler(cls, module_name)
        table_line = TableHandler(cls, 'account.invoice.line')
        sql_table = cls.__table__()
        record_table = Record.__table__()

        exist_347 = table.column_exist('include_347')

        super(Invoice, cls).__register__(module_name)

        # Migration: moved 347 check mark from invoice line to invoice
        if not exist_347:
            cursor.execute(*record_table.select(record_table.invoice,
                    record_table.operation_key))
            for invoice_id, operation_key in cursor.fetchall():
                cursor.execute(*sql_table.update(
                        columns=[sql_table.include_347,
                            sql_table.aeat347_operation_key],
                        values=[True, operation_key],
                        where=sql_table.id == invoice_id))
            table_line.drop_column('include_347')
            table_line.drop_column('aeat347_operation_key')

    def on_change_party(self):
        super(Invoice, self).on_change_party()
        self.include_347 = self.on_change_with_include_347()
        self.aeat347_operation_key = \
            self.on_change_with_aeat347_operation_key()

    @fields.depends('party')
    def on_change_with_include_347(self, name=None):
        return self.party.include_347 if self.party else False

    @fields.depends('type', 'aeat347_operation_key', 'include_347')
    def on_change_with_aeat347_operation_key(self):
        if not self.include_347:
            return ''
        if self.aeat347_operation_key:
            return self.aeat347_operation_key
        if self.type:
            return self.get_aeat347_operation_key(self.type)
        else:
            return ''

    @classmethod
    def get_aeat347_operation_key(cls, invoice_type):
        return 'A' if invoice_type == 'in' else 'B'

    def get_aeat347_total_amount(self):
        amount = 0
        for tax in self.taxes:
            if tax.include_347:
                amount += (tax.base + tax.amount)
        return (amount < self.total_amount and amount or self.total_amount)

    @classmethod
    def create_aeat347_records(cls, invoices):
        pool = Pool()
        Record = pool.get('aeat.347.record')
        Period = pool.get('account.period')

        to_create = {}
        for invoice in invoices:
            if (not invoice.move or invoice.state == 'cancel' or
                    not invoice.include_347):
                continue
            if invoice.aeat347_operation_key:
                operation_key = invoice.aeat347_operation_key
                amount = invoice.get_aeat347_total_amount()

                if invoice.type == 'in':
                    accounting_date = (invoice.accounting_date
                        or invoice.invoice_date)
                    period_id = Period.find(
                        invoice.company.id, date=accounting_date)
                    period = Period(period_id)
                    fiscalyear = period.fiscalyear
                else:
                    fiscalyear = invoice.move.period.fiscalyear

                to_create[invoice.id] = {
                    'company': invoice.company.id,
                    'fiscalyear': fiscalyear,
                    'month': invoice.invoice_date.month,
                    'party': invoice.party.id,
                    'amount': amount,
                    'operation_key': operation_key,
                    'invoice': invoice.id,
                    }

        Record.delete_record(invoices)
        with Transaction().set_user(0, set_context=True):
            Record.create(to_create.values())

    @classmethod
    def create(cls, vlist):
        Party = Pool().get('party.party')

        vlist = [x.copy() for x in vlist]

        party_ids = set()
        for vals in vlist:
            if 'include_347' not in vals:
                party_ids.add(vals['party'])

        if party_ids:
            with Transaction().set_context(active_test=False):
                parties = dict([(x.id, x.include_347) for x in Party.search([
                            ('id', 'in', list(party_ids))])])

        for vals in vlist:
            if 'include_347' not in vals:
                party_id = vals['party']
                vals['include_347'] = parties[party_id]
            if not vals.get('include_347', True):
                continue
            invoice_type = vals.get('type', 'out')
            vals['aeat347_operation_key'] = cls.get_aeat347_operation_key(
                invoice_type)

        return super(Invoice, cls).create(vlist)

    @classmethod
    def draft(cls, invoices):
        pool = Pool()
        Record = pool.get('aeat.347.record')
        super(Invoice, cls).draft(invoices)
        Record.delete_record(invoices)

    @classmethod
    def post(cls, invoices):
        super(Invoice, cls).post(invoices)
        cls.create_aeat347_records(invoices)

    @classmethod
    def cancel(cls, invoices):
        pool = Pool()
        Record = pool.get('aeat.347.record')
        super(Invoice, cls).cancel(invoices)
        Record.delete_record(invoices)


class InvoiceTax:
    __metaclass__ = PoolMeta
    __name__ = 'account.invoice.tax'

    include_347 = fields.Boolean('Include 347', readonly=True)

    @fields.depends('include_347')
    def on_change_tax(self):
        Tax = Pool().get('account.tax')
        super(InvoiceTax, self).on_change_tax()
        if not self.tax:
            return
        if self.invoice:
            context = self.invoice._get_tax_context()
        else:
            context = {}
        with Transaction().set_context(**context):
            tax = Tax(self.tax.id)
        self.include_347 = tax.include_347


class Recalculate347RecordStart(ModelView):
    """
    Recalculate AEAT 347 Records Start
    """
    __name__ = "aeat.347.recalculate.records.start"


class Recalculate347RecordEnd(ModelView):
    """
    Recalculate AEAT 347 Records End
    """
    __name__ = "aeat.347.recalculate.records.end"


class Recalculate347Record(Wizard):
    """
    Recalculate AEAT 347 Records
    """
    __name__ = "aeat.347.recalculate.records"
    start = StateView('aeat.347.recalculate.records.start',
        'aeat_347.aeat_347_recalculate_start_view', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Calculate', 'calculate', 'tryton-ok', default=True),
            ])
    calculate = StateTransition()
    done = StateView('aeat.347.recalculate.records.end',
        'aeat_347.aeat_347_recalculate_end_view', [
            Button('Ok', 'end', 'tryton-ok', default=True),
            ])

    def transition_calculate(self):
        Invoice = Pool().get('account.invoice')
        invoices = Invoice.browse(Transaction().context['active_ids'])
        Invoice.create_aeat347_records(invoices)
        return 'done'


class Reasign347RecordStart(ModelView):
    """
    Reasign AEAT 347 Records Start
    """
    __name__ = "aeat.347.reasign.records.start"

    aeat_347_operation_key = fields.Selection([('none', 'Leave Empty'), ] +
        OPERATION_KEY, 'Operation Key', required=True)
    include_347 = fields.Boolean('Include 347')

    @staticmethod
    def default_aeat_347_operation_key():
        return 'none'


class Reasign347RecordEnd(ModelView):
    """
    Reasign AEAT 347 Records End
    """
    __name__ = "aeat.347.reasign.records.end"


class Reasign347Record(Wizard):
    """
    Reasign AEAT 347 Records
    """
    __name__ = "aeat.347.reasign.records"
    start = StateView('aeat.347.reasign.records.start',
        'aeat_347.aeat_347_reasign_start_view', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Reasign', 'reasign', 'tryton-ok', default=True),
            ])
    reasign = StateTransition()
    done = StateView('aeat.347.reasign.records.end',
        'aeat_347.aeat_347_reasign_end_view', [
            Button('Ok', 'end', 'tryton-ok', default=True),
            ])

    def transition_reasign(self):
        Invoice = Pool().get('account.invoice')
        cursor = Transaction().connection.cursor()
        invoice_ids = Transaction().context['active_ids']
        invoices = Invoice.browse(invoice_ids)

        value = self.start.aeat_347_operation_key
        include = self.start.include_347
        if value == 'none' or not include:
            value = None

        invoice = Invoice.__table__()
        # Update to allow to modify key for posted invoices
        cursor.execute(*invoice.update(columns=[invoice.aeat347_operation_key,
                    invoice.include_347],
                values=[value, include], where=In(invoice.id, invoice_ids)))

        Invoice.create_aeat347_records(invoices)

        return 'done'
