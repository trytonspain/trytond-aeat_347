# This file is part of the aeat_347 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import doctest_setup, doctest_teardown
from trytond.tests.test_tryton import doctest_checker
from trytond.pool import Pool
from trytond.modules.company.tests import create_company, set_company
from trytond.modules.account.tests import create_chart


class Aeat347TestCase(ModuleTestCase):
    'Test Aeat 347 module'
    module = 'aeat_347'

    @with_transaction()
    def test_include_347(self):
        "Test include 347"
        pool = Pool()
        Party = pool.get('party.party')
        Journal = pool.get('account.journal')
        Account = pool.get('account.account')
        PaymentTerm = pool.get('account.invoice.payment_term')
        Invoice = pool.get('account.invoice')

        company = create_company()
        currency = company.currency
        with set_company(company):
            _ = create_chart(company)
            revenue, = Account.search([('kind', '=', 'revenue')])
            payable, = Account.search([('kind', '=', 'payable')])
            receivable, = Account.search([('kind', '=', 'receivable')])
            journal_cash, = Journal.search([('type', '=', 'cash')])

            term, = PaymentTerm.create([{
                        'name': 'Term',
                        'lines': [
                            ('create', [{
                                        'sequence': 1,
                                        'type': 'remainder',
                                        'relativedeltas': [('create', [{
                                                        'months': 2,
                                                        'days': 30,
                                                        'day': 15,
                                                        },
                                                    ]),
                                            ],
                                        }])]
                        }])

            party1, party2 = Party.create([{
                        'name': 'Party 1',
                        'include_347': True,
                        'addresses': [
                            ('create', [{
                                        'name': 'John',
                                        }])]
                        }, {
                        'name': 'Party 2',
                        'addresses': [
                            ('create', [{
                                        'name': 'Maria',
                                        }])]
                        }])

            invoice = Invoice()
            invoice.party = party1
            invoice.invoice_address = party1.addresses[0]
            invoice.type = 'out'
            invoice.currency = currency
            invoice.journal = journal_cash
            invoice.account = receivable
            invoice.payment_term = term
            invoice.save()
            self.assertEqual(bool(invoice.include_347), True)

            invoice = Invoice()
            invoice.party = party2
            invoice.invoice_address = party2.addresses[0]
            invoice.type = 'out'
            invoice.currency = currency
            invoice.journal = journal_cash
            invoice.account = receivable
            invoice.payment_term = term
            invoice.save()
            self.assertEqual(bool(invoice.include_347), False)

def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        Aeat347TestCase))
    suite.addTests(doctest.DocFileSuite('scenario_aeat347.rst',
            setUp=doctest_setup, tearDown=doctest_teardown, encoding='utf-8',
            checker=doctest_checker,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
