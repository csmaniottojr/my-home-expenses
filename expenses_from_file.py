import mimetypes
import os
from datetime import datetime

import click

import google_apis
from expense import create_despesa_row


def read_file(path, expected_mimetype):
    if mimetypes.guess_type(path) == expected_mimetype:
        raise ValueError("You need provide a file in pdf format")

    with open(path, "rb") as pdf_file:
        return pdf_file.read()


def format_file_name(path):
    basename = os.path.basename(path)
    now = datetime.now().isoformat()
    return f"{now} - {basename}"


@click.command()
@click.option("-e", "--expense", help="Identificador da despesa. Ex: Fatura da Claro")
@click.option("-f", "--file", help="Arquivo pdf do boleto", type=click.Path())
def get_expenses_from_file(expense, file):
    expected_mimetype = "application/pdf"
    file_content = read_file(file, expected_mimetype)
    filename = format_file_name(file)

    credentials = google_apis.get_credentials()
    url_file = google_apis.upload_file_to_drive(
        filename=filename,
        mimetype=expected_mimetype,
        file_buffer=file_content,
        credentials=credentials,
    )
    row = create_despesa_row(tipo=expense, link_pdf=url_file)
    google_apis.update_sheet([row], credentials)


if __name__ == "__main__":
    get_expenses_from_file()
