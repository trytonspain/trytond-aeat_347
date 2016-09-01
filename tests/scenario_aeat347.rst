================
Invoice Scenario
================

Imports::
    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from operator import attrgetter
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import install_modules
    >>> from trytond.modules.currency.tests.tools import get_currency
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> from trytond.modules.account_invoice.tests.tools import \
    ...     set_fiscalyear_invoice_sequences, create_payment_term
    >>> today = datetime.date.today()

Install account_invoice::

    >>> config = install_modules('aeat_347')

Create company::

    >>> eur = get_currency('EUR')
    >>> _ = create_company(currency=eur)
    >>> company = get_company()

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

    >>> Tax = Model.get('account.tax')
    >>> tax = set_tax_code(create_tax(Decimal('.10')))
    >>> tax.save()

Create party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Party')
    >>> party.include_347 = True
    >>> identifier = party.identifiers.new()
    >>> identifier.type = 'eu_vat'
    >>> identifier.code = 'ES00000000T'
    >>> bool(party.include_347)
    True
    >>> party.save()
    >>> party2 = Party(name='Party 2')
    >>> identifier = party2.identifiers.new()
    >>> identifier.type = 'eu_vat'
    >>> identifier.code = 'ES00000001R'
    >>> bool(party2.include_347)
    True
    >>> party2.save()

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
    >>> template.customer_taxes.append(Tax(tax.id))
    >>> template.supplier_taxes.append(Tax(tax.id))
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create payment term::

    >>> payment_term = create_payment_term()
    >>> payment_term.save()

Create out invoice over limit::

    >>> Record = Model.get('aeat.347.record')
    >>> Invoice = Model.get('account.invoice')
    >>> invoice = Invoice()
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.unit_price = Decimal(40)
    >>> line.quantity = 80
    >>> len(line.taxes)
    1
    >>> bool(line.include_347)
    True
    >>> line.aeat347_operation_key
    'B'
    >>> line.amount
    Decimal('3200.00')
    >>> invoice.click('post')
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name
    u'Party'
    >>> rec1.party_vat
    u'00000000T'
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key
    u'B'
    >>> rec1.amount
    Decimal('3520.00')

Create out invoice not over limit::

    >>> invoice = Invoice()
    >>> invoice.party = party2
    >>> invoice.payment_term = payment_term
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.unit_price = Decimal(40)
    >>> line.quantity = 5
    >>> len(line.taxes)
    1
    >>> bool(line.include_347)
    True
    >>> line.aeat347_operation_key
    'B'
    >>> line.amount
    Decimal('200.00')
    >>> invoice.click('post')
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name
    u'Party 2'
    >>> rec1.party_vat
    u'00000001R'
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key
    u'B'
    >>> rec1.amount
    Decimal('220.00')

Create out credit note::

    >>> invoice = Invoice()
    >>> invoice.type = 'out'
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.unit_price = Decimal(40)
    >>> line.quantity = -2
    >>> len(line.taxes)
    1
    >>> bool(line.include_347)
    True
    >>> line.aeat347_operation_key
    'B'
    >>> line.amount
    Decimal('-80.00')
    >>> invoice.click('post')
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name
    u'Party'
    >>> rec1.party_vat
    u'00000000T'
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key
    u'B'
    >>> rec1.amount
    Decimal('-88.00')

Create in invoice::

    >>> invoice = Invoice()
    >>> invoice.type = 'in'
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = today
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.quantity = 5
    >>> line.unit_price = Decimal('25')
    >>> len(line.taxes)
    1
    >>> line.aeat347_operation_key
    'A'
    >>> line.amount
    Decimal('125.00')
    >>> invoice.click('post')
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name
    u'Party'
    >>> rec1.party_vat
    u'00000000T'
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key
    u'A'
    >>> rec1.amount
    Decimal('137.50')

Create in credit note::

    >>> invoice = Invoice()
    >>> invoice.type = 'in'
    >>> invoice.party = party
    >>> invoice.payment_term = payment_term
    >>> invoice.invoice_date = today
    >>> line = invoice.lines.new()
    >>> line.product = product
    >>> line.unit_price = Decimal('25.00')
    >>> line.quantity = -1
    >>> len(line.taxes)
    1
    >>> line.aeat347_operation_key
    'A'
    >>> line.amount
    Decimal('-25.00')
    >>> invoice.click('post')
    >>> rec1, = Record.find([('invoice', '=', invoice.id)])
    >>> rec1.party_name
    u'Party'
    >>> rec1.party_vat
    u'00000000T'
    >>> rec1.month == today.month
    True
    >>> rec1.operation_key
    u'A'
    >>> rec1.amount
    Decimal('-27.50')

Generate 347 Report::

    >>> Report = Model.get('aeat.347.report')
    >>> report = Report()
    >>> report.fiscalyear = fiscalyear
    >>> report.fiscalyear_code = 2013
    >>> report.company_vat = '123456789'
    >>> report.contact_name = 'Guido van Rosum'
    >>> report.contact_phone = '987654321'
    >>> report.representative_vat = '22334455'
    >>> report.click('calculate')
    >>> report.reload()
    >>> report.property_count
    0
    >>> report.party_count
    1
    >>> report.party_amount
    Decimal('3432.00')
    >>> report.cash_amount
    Decimal('0.0')
    >>> report.property_amount
    Decimal('0.0')

Test report is generated correctly::

    >>> report.file_
    >>> report.click('process')
    >>> bool(report.file_)
    True

Reassign 347 lines::

    >>> reasign = Wizard('aeat.347.reasign.records', models=[invoice])
    >>> reasign.form.include_347 = False
    >>> reasign.execute('reasign')
    >>> line.reload()
    >>> bool(line.include_347)
    False
    >>> line.aeat347_operation_key
