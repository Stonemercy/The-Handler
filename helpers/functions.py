from datetime import datetime


def get_datetime(date: str):
    """Attempts to get a datetime object from a date string in the following formats:
    `DD/MM/YY HH:MM`
    `DD/MM/YYYY HH:MM`
    :class:`DD/MM/YY`
    :class:`DD/MM/YYYY`
    `YYYY-MM-DD HH:MM:SS`
    :class:`HH:MM`
    `YYYY-MM-DD HH:MM:SS.MS`

    Parameters
    ----------
    date: `str`
        The date you want to convert

    Returns
    ----------
    `datetime` or `False`
    """
    for fmt in [
        "%d/%m/%y %H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%H:%M",
        "%Y-%m-%d %H:%M:%S.%f",
    ]:
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            pass
    return False
