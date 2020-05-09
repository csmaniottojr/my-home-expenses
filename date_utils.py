from datetime import date, datetime, timedelta


def format_date_filter(days):
    after_date = date.today() - timedelta(days=days)
    return after_date.isoformat().replace("-", "/")


def format_received_date(date_str):
    formats = (
        "%d/%m/%Y",
        "%a, %d %b %Y %H:%M:%S %z (%Z)",
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z",
    )
    for format in formats:
        try:
            return datetime.strptime(date_str, format).date().isoformat()
        except ValueError:
            pass
    return date_str


def get_current_date():
    return date.today().isoformat()
