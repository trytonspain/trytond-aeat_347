#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from .aeat import *
from .invoice import *
from .party import *


def register():
    Pool.register(
        Party,
        Report,
        PartyRecord,
        PropertyRecord,
        Record,
        Invoice,
        InvoiceLine,
        Recalculate347RecordStart,
        Recalculate347RecordEnd,
        Reasign347RecordStart,
        Reasign347RecordEnd,
        module='aeat_347', type_='model')
    Pool.register(
        Recalculate347Record,
        Reasign347Record,
        module='aeat_347', type_='wizard')
