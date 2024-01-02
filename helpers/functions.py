from datetime import datetime


def get_date_format(date):
    for fmt in ["%d/%m/%y %H:%M", "%d/%m/%Y %H:%M"]:
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            pass
    raise ValueError("No valid date format found")
