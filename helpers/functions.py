from datetime import datetime


def get_datetime(date: str):
    """Attempts to get a datetime object from a date string in the following formats:
    :class:`DD/MM/YY HH:MM`
    :class:`DD/MM/YYYY HH:MM`
    :class:`DD/MM/YY`
    :class:`DD/MM/YYYY`
    :class:`YYYY-MM-DD HH:MM:SS`

    Parameters
    ----------
    date: :class:`str`
        The date you want to convert
    """
    for fmt in [
        "%d/%m/%y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
    ]:
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            pass
    return False
