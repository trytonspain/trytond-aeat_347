================
Invoice Scenario
================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from.trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_invoice::

    >>> Module = Model.get('ir.module')
    >>> aeat_347_module, = Module.find(
    ...     [('name', '=', 'aeat_347')])
    >>> Module.install([aeat_347_module.id], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> fiscalyear = set_fiscalyear_invoice_sequences(
    ...     create_fiscalyear(company))
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']

Create tax::

    >>> tax = set_tax_code(create_tax(Decimal('.10')))
    >>> tax.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> Identifier = Model.get('party.identifier')
    >>> party = Party(name='Party')
    >>> party.include_347 = True
    >>> party.save()
    >>> identifier = Identifier(party=party, type='eu_vat', code='ES00000000T')
    >>> identifier.save()
    >>> party2 = Party(name='Party 2')
    >>> party.include_347 = True
    >>> party2.save()
    >>> identifier2 = Identifier(party=party2, type='', code='ES00000001R')
    >>> identifier2.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'service'
    >>> template.purchasable = True
    >>> template.salable = True
    >>> template.list_price = Decimal('40')
    >>> template.cost_price = Decimal('25')
    >>> template.cost_price_method = 'fixed'
    >>> template.account_expense = expense
    >>> template.account_revenue = revenue
    >>> template.customer_taxes.append(tax)
    >>> template.supplier_taxes.append(tax)
    >>> template.save()
    >>> product.template = template
    >>> product.save()
    
Create payment term::

    >>> PaymentTerm = Model.get('account.invoice.payment_term')
    >>> payment_term = PaymentTerm(name='Term')
    >>> line = payment_term.lines.new(type='percent', percentage=Decimal(50))
    >>> delta = line.relativedeltas.new(days=20)
    >>> line = payment_term.lines.new(type='remainder')
    >>> delta = line.relativedeltas.new(days=40)
    >>> payment_term.save()

Create out invoice over limit::

    >>> Record = Model.get('aeat.347.record')
    >>> Invoice = Model.get('account.invoice')
    >>> InvoiceLine = Model.get('account.invoice.line')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 80
    >>> len(line.taxes) == 1
    True
    >>> bool(line.include_347)
    True
    >>> line.aeat347_operation_key == 'B'
    True
    >>> line.amount == Decimal(3200)
    True
    >>> invoice.save()
    >>> Invoice.post([invoice.id], config.context)
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name == 'Party'
    True
    >>> rec1.party_vat == '00000000T'
    True
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key == 'B'
    True
    >>> rec1.amount == Decimal(3520)
    True

Create out invoice not over limit::

    >>> invoice = Invoice()
    >>> invoice.party = party2
    >>> invoice.payment_term = payment_term
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 5
    >>> len(line.taxes) == 1
    True
    >>> bool(line.include_347)
    True
    >>> line.aeat347_operation_key == 'B'
    True
    >>> line.amount == Decimal(200)
    True
    >>> invoice.save()
    >>> Invoice.post([invoice.id], config.context)
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name == 'Party 2'
    True
    >>> rec1.party_vat == '00000001R'
    True
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key == 'B'
    True
    >>> rec1.amount == Decimal(220)
    True

Create out credit note::

    >>> invoice = Invoice()
    >>> invoice.type = 'out_credit_note'
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 2
    >>> len(line.taxes) == 1
    True
    >>> bool(line.include_347)
    True
    >>> line.aeat347_operation_key == 'B'
    True
    >>> line.amount == Decimal(80)
    True
    >>> invoice.save()
    >>> Invoice.post([invoice.id], config.context)
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name == 'Party'
    True
    >>> rec1.party_vat == '00000000T'
    True
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key == 'B'
    True
    >>> rec1.amount == Decimal('-88.0')
    True

Create in invoice::

    >>> invoice = Invoice()
    >>> invoice.type = 'in_invoice'
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = today
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 5
    >>> len(line.taxes) == 1
    True
    >>> line.aeat347_operation_key == 'A'
    True
    >>> line.amount == Decimal(125)
    True
    >>> invoice.save()
    >>> Invoice.post([invoice.id], config.context)
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name == 'Party'
    True
    >>> rec1.party_vat == '00000000T'
    True
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key == 'A'
    True
    >>> rec1.amount == Decimal(137.50)
    True

Create in credit note::

    >>> invoice = Invoice()
    >>> invoice.type = 'in_credit_note'
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = today
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 1
    >>> len(line.taxes) == 1
    True
    >>> line.aeat347_operation_key == 'A'
    True
    >>> line.amount == Decimal(25)
    True
    >>> invoice.save()
    >>> Invoice.post([invoice.id], config.context)
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name == 'Party'
    True
    >>> rec1.party_vat == '00000000T'
    True
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key == 'A'
    True
    >>> rec1.amount == Decimal('-27.50')
    True

Generate 347 Report::

    >>> Report = Model.get('aeat.347.report')
    >>> report = Report()
    >>> report.fiscalyear = fiscalyear
    >>> report.fiscalyear_code = 2013
    >>> report.company_vat = '123456789'
    >>> report.contact_name = 'Guido van Rosum'
    >>> report.contact_phone = '987654321'
    >>> report.representative_vat = '22334455'
    >>> report.save()
    >>> Report.calculate([report.id], config.context)
    >>> report.reload()
    >>> report.property_count == 0
    True
    >>> report.party_count == 1
    True
    >>> report.party_amount == Decimal('3432')
    True
    >>> report.cash_amount == Decimal(0)
    True
    >>> report.property_amount == Decimal(0)
    True

Reassign 347 lines::

    >>> reasign = Wizard('aeat.347.reasign.records', models=[invoice])
    >>> reasign.form.include_347 = False
    >>> reasign.execute('reasign')
    >>> line.reload()
    >>> bool(line.include_347)
    False
    >>> line.aeat347_operation_key == None
    True
