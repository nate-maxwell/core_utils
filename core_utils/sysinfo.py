import datetime
import platform


def get_date() -> str:
    """Returns str: 'MM-DD-YYYY'"""
    today = datetime.date.today()
    return today.strftime("%m-%d-%Y")


def get_time() -> str:
    """Returns str: 'HH:MM:SS:XX', X is microsecond."""
    now = datetime.datetime.now().time().isoformat()[:-4]
    return now


def get_os_info() -> tuple[str, str, str]:
    """
    Returns tuple[str, str, str]: OS name, release number, and version number.

    Notes:
        On many python versions, Windows 11 is seen as Windows 10.
    """
    system = platform.system()
    release = platform.release()
    version = platform.version()
    return system, release, version
