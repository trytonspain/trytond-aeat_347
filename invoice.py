from trytond.model import ModelSQL, ModelView, fields
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from sql.operators import In
from .aeat import OPERATION_KEY

__all__ = ['Record', 'Invoice', 'InvoiceLine',
    'Recalculate347RecordStart', 'Recalculate347RecordEnd',
    'Recalculate347Record', 'Reasign347RecordStart',
    'Reasign347RecordEnd', 'Reasign347Record']

__metaclass__ = PoolMeta


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
            res['party_name'][record.id] = party.rec_name[:39]
            res['party_vat'][record.id] = party.vat_number
            if len(party.addresses) > 0:
                address = party.addresses[0]
                country = None
                province = None
                code = address.zip
                if code:
                    if len(code) > 5 and '' in code:
                        country = code[:2]
                        code = code[2:]
                    province = code[:2]
            res['country_code'][record.id] = party.vat_country or country \
                or ''
            res['province_code'][record.id] = province or code or ''
        for key in res.keys():
            if key not in names:
                del res[key]
        return res


class InvoiceLine:
    __name__ = 'account.invoice.line'
    aeat347_operation_key = fields.Selection([(None, ''), ] + OPERATION_KEY,
        'AEAT 347 Operation Key', on_change_with=['product', 'account',
            '_parent_invoice.type', 'aeat347_operation_key'],
        states={
            'invisible': Eval('type') != 'line',
            'required': Eval('type') == 'line',
            },
        depends=['type'])

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()

    def on_change_with_aeat347_operation_key(self):
        if self.aeat347_operation_key:
            return self.aeat347_operation_key
        if self.invoice and self.invoice.type:
            type_ = self.invoice.type
        elif self.invoice_type:
            type_ = self.invoice_type
        if not type_:
            return
        return self.get_aeat347_operation_key(type_)

    @classmethod
    def get_aeat347_operation_key(cls, invoice_type):
        type_ = 'in' if invoice_type[0:2] == 'in' else 'out'
        return 'A' if type_ == 'in' else 'B'

    @classmethod
    def create(cls, vlist):
        Invoice = Pool().get('account.invoice')
        for vals in vlist:
            if vals.get('type', 'line') != 'line':
                continue
            invoice_type = vals.get('invoice_type')
            if not invoice_type and vals.get('invoice'):
                invoice = Invoice(vals.get('invoice'))
                invoice_type = invoice.type
            vals['aeat347_operation_key'] = cls.get_aeat347_operation_key(
                invoice_type)
        return super(InvoiceLine, cls).create(vlist)


class Invoice:
    __name__ = 'account.invoice'

    def _compute_total_amount(self, line):
        Tax = Pool().get('account.tax')
        context = self.get_tax_context()

        with Transaction().set_context(**context):
            taxes = Tax.compute(line.taxes, line.unit_price, line.quantity)
            tax_amount = 0
            for tax in taxes:
                key, val = self._compute_tax(tax, self.type)
                tax_amount += val['amount']

        return line.get_amount('amount') + tax_amount

    @classmethod
    def create_aeat347_records(cls, invoices):
        Record = Pool().get('aeat.347.record')
        to_create = {}

        for invoice in invoices:
            if not invoice.move:
                continue
            key = None
            for line in invoice.lines:
                if line.type != 'line':
                    continue
                if line.aeat347_operation_key:
                    operation_key = line.aeat347_operation_key
                    key = "%d-%s" % (invoice.id, operation_key)
                    amount = invoice._compute_total_amount(line)

                    if invoice.type in ('out_credit_note', 'in_credit_note'):
                        amount *= -1

                    if key in to_create:
                        to_create[key]['amount'] += amount
                    else:
                        to_create[key] = {
                                'company': invoice.company.id,
                                'fiscalyear': invoice.move.period.fiscalyear,
                                'month': invoice.invoice_date.month,
                                'party': invoice.party.id,
                                'amount': amount,
                                'operation_key': operation_key,
                                'invoice': invoice.id,
                        }

            if key and key in to_create:
                to_create[key]['amount'] = invoice.currency.round(
                    to_create[key]['amount'])

        with Transaction().set_user(0, set_context=True):
            Record.delete(Record.search([('invoice', 'in',
                            [i.id for i in invoices])]))
            Record.create(to_create.values())

    @classmethod
    def post(cls, invoices):
        super(Invoice, cls).post(invoices)
        cls.create_aeat347_records(invoices)


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

    aeat_347_operation_key = fields.Selection(OPERATION_KEY, 'Operation Key',
        required=True)


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
        Line = Pool().get('account.invoice.line')
        cursor = Transaction().cursor
        invoices = Invoice.browse(Transaction().context['active_ids'])

        value = self.start.aeat_347_operation_key
        lines = []
        invoice_ids = set()
        for invoice in invoices:
            for line in invoice.lines:
                lines.append(line.id)
                invoice_ids.add(invoice.id)

        line = Line.__table__()
        #Update to allow to modify key for posted invoices
        cursor.execute(*line.update(columns=[line.aeat347_operation_key],
                values=[value], where=In(line.id, lines)))

        invoices = Invoice.browse(list(invoices))
        Invoice.create_aeat347_records(invoices)

        return 'done'
