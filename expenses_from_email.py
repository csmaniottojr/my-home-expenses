import click

import date_utils
import google_apis
from config import EMAILS
from expense import create_despesa_row


def format_message_filter():
    after_date = date_utils.format_date_filter(days=30)
    from_emails = [f"from:{email}" for email in EMAILS]
    query_emails = " OR ".join(from_emails)
    return f"after:{after_date} AND ({query_emails})"


def list_emails_to_fetch_attachments(credentials):
    emails_ids = google_apis.get_emails_ids_from_sheet(credentials)
    query = format_message_filter()

    messages_ids = google_apis.list_gmail_messages(query, credentials)
    return [msg_id for msg_id in messages_ids if msg_id not in emails_ids]


def get_value_from_message_header(headers, header_name):
    return next(header["value"] for header in headers if header["name"] == header_name)


def get_email_date(headers):
    received_date = get_value_from_message_header(headers, "Date")
    return date_utils.format_received_date(received_date)


def format_from(from_email):
    *_, email = from_email.split(" ")
    return email[1:-1]


def get_email_remetent(headers):
    from_email = get_value_from_message_header(headers, "From")
    return format_from(from_email)


def filter_attachments(attachments):
    mime_types = ("application/octet-stream", "application/pdf")
    for attachment in attachments:
        filename = attachment["filename"]
        mimetype = attachment["mimeType"]
        if filename and mimetype in mime_types:
            attachment_id = attachment["body"]["attachmentId"]
            yield filename, attachment_id, mimetype


@click.command()
def get_expenses_from_email():
    credentials = google_apis.get_credentials()
    messages = list_emails_to_fetch_attachments(credentials)

    rows = []

    for message_id in messages:
        msg_detail = google_apis.get_message(message_id, credentials)

        headers = msg_detail["payload"]["headers"]
        received_date = get_email_date(headers)
        from_email = get_email_remetent(headers)

        attachments = msg_detail["payload"]["parts"]

        for filename, attachment_id, mimetype in filter_attachments(attachments):
            file_content = google_apis.download_attachment(
                message_id, attachment_id, credentials
            )
            pdf_filename = f"{message_id} - {filename}"

            url_file = google_apis.upload_file_to_drive(
                filename=pdf_filename,
                mimetype=mimetype,
                file_buffer=file_content,
                credentials=credentials,
            )

            row = create_despesa_row(
                tipo=from_email,
                link_pdf=url_file,
                recebimento=received_date,
                email_id=message_id,
            )

            rows.append(tuple(row))

    google_apis.update_sheet(rows, credentials)


if __name__ == '__main__':
    get_expenses_from_email()
