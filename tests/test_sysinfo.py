import datetime
import sys
from pathlib import Path
from unittest.mock import patch

from core_utils import sysinfo

sys.path.insert(0, str(Path(__file__).parent.parent))


# -----get_date Tests----------------------------------------------------------


class TestGetDate:
    @patch("core_utils.sysinfo.datetime")
    def test_get_date_format(self, mock_datetime):
        mock_datetime.date.today.return_value = datetime.date(2024, 3, 15)
        result = sysinfo.get_date()
        assert result == "03-15-2024"

    @patch("core_utils.sysinfo.datetime")
    def test_get_date_single_digit_month(self, mock_datetime):
        mock_datetime.date.today.return_value = datetime.date(2024, 1, 5)
        result = sysinfo.get_date()
        assert result == "01-05-2024"

    @patch("core_utils.sysinfo.datetime")
    def test_get_date_december(self, mock_datetime):
        mock_datetime.date.today.return_value = datetime.date(2024, 12, 31)
        result = sysinfo.get_date()
        assert result == "12-31-2024"

    def test_get_date_returns_string(self):
        result = sysinfo.get_date()
        assert isinstance(result, str)

    def test_get_date_format_pattern(self):
        result = sysinfo.get_date()
        # Should match MM-DD-YYYY pattern
        parts = result.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 2  # Month
        assert len(parts[1]) == 2  # Day
        assert len(parts[2]) == 4  # Year


# -----get_time Tests----------------------------------------------------------


class TestGetTime:
    @patch("core_utils.sysinfo.datetime.datetime")
    def test_get_time_format(self, mock_datetime):
        mock_time = datetime.time(14, 30, 45, 123456)
        mock_datetime.now.return_value.time.return_value = mock_time
        result = sysinfo.get_time()
        assert result == "14:30:45.12"

    @patch("core_utils.sysinfo.datetime.datetime")
    def test_get_time_morning(self, mock_datetime):
        mock_time = datetime.time(9, 5, 3, 500000)
        mock_datetime.now.return_value.time.return_value = mock_time
        result = sysinfo.get_time()
        assert result == "09:05:03.50"

    @patch("core_utils.sysinfo.datetime.datetime")
    def test_get_time_midnight(self, mock_datetime):
        mock_time = datetime.time(0, 0, 0, 100000)
        mock_datetime.now.return_value.time.return_value = mock_time
        result = sysinfo.get_time()
        assert result == "00:00:00.10"

    @patch("core_utils.sysinfo.datetime.datetime")
    def test_get_time_truncates_microseconds(self, mock_datetime):
        mock_time = datetime.time(12, 0, 0, 999999)
        mock_datetime.now.return_value.time.return_value = mock_time
        result = sysinfo.get_time()
        # Should truncate to 2 decimal places (centiseconds)
        assert result == "12:00:00.99"

    def test_get_time_returns_string(self):
        result = sysinfo.get_time()
        assert isinstance(result, str)

    def test_get_time_format_pattern(self):
        result = sysinfo.get_time()
        # Should match HH:MM:SS.XX pattern
        parts = result.split(":")
        assert len(parts) == 3
        assert len(parts[0]) == 2  # Hours
        assert len(parts[1]) == 2  # Minutes
        # Seconds part should be SS.XX
        assert "." in parts[2]
        seconds_parts = parts[2].split(".")
        assert len(seconds_parts[0]) == 2  # Seconds
        assert len(seconds_parts[1]) == 2  # Centiseconds


# -----get_os_info Tests-------------------------------------------------------


class TestGetOSInfo:
    @patch("core_utils.sysinfo.platform.system")
    @patch("core_utils.sysinfo.platform.release")
    @patch("core_utils.sysinfo.platform.version")
    def test_get_os_info_windows(self, mock_version, mock_release, mock_system):
        mock_system.return_value = "Windows"
        mock_release.return_value = "10"
        mock_version.return_value = "10.0.19041"

        result = sysinfo.get_os_info()

        assert result == ("Windows", "10", "10.0.19041")

    @patch("core_utils.sysinfo.platform.system")
    @patch("core_utils.sysinfo.platform.release")
    @patch("core_utils.sysinfo.platform.version")
    def test_get_os_info_linux(self, mock_version, mock_release, mock_system):
        mock_system.return_value = "Linux"
        mock_release.return_value = "5.15.0"
        mock_version.return_value = "#1 SMP"

        result = sysinfo.get_os_info()

        assert result == ("Linux", "5.15.0", "#1 SMP")

    @patch("core_utils.sysinfo.platform.system")
    @patch("core_utils.sysinfo.platform.release")
    @patch("core_utils.sysinfo.platform.version")
    def test_get_os_info_macos(self, mock_version, mock_release, mock_system):
        mock_system.return_value = "Darwin"
        mock_release.return_value = "21.6.0"
        mock_version.return_value = "Darwin Kernel Version 21.6.0"

        result = sysinfo.get_os_info()

        assert result == ("Darwin", "21.6.0", "Darwin Kernel Version 21.6.0")

    def test_get_os_info_returns_tuple(self):
        result = sysinfo.get_os_info()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_get_os_info_returns_strings(self):
        result = sysinfo.get_os_info()
        assert all(isinstance(item, str) for item in result)

    @patch("core_utils.sysinfo.platform.system")
    @patch("core_utils.sysinfo.platform.release")
    @patch("core_utils.sysinfo.platform.version")
    def test_get_os_info_calls_platform_functions(
        self, mock_version, mock_release, mock_system
    ):
        mock_system.return_value = "TestOS"
        mock_release.return_value = "1.0"
        mock_version.return_value = "Test Version"

        sysinfo.get_os_info()

        mock_system.assert_called_once()
        mock_release.assert_called_once()
        mock_version.assert_called_once()
