from collections import namedtuple

import date_utils

DespesaRow = namedtuple("DespesaRow", "tipo data_recebimento link_pdf email_id")


def create_despesa_row(tipo, link_pdf, recebimento=None, email_id=""):
    current_date = date_utils.get_current_date()
    return DespesaRow(
        tipo=tipo,
        data_recebimento=recebimento if recebimento else current_date,
        link_pdf=link_pdf,
        email_id=email_id,
    )
