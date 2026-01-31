import math


def convert_size(size_bytes: int) -> tuple[float, str]:
    """
    Converts pure byte count to commonly named size.
    Will convert to the most concise number, e.g. 1.1 GB, not 1100 MB.

    Args:
        size_bytes (int): How many bytes to rename.
    Returns:
        tuple[float, str]: The new unit size and the new unit label.
    """
    if size_bytes == 0:
        return 0, "B"
    size_name: list[str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return s, size_name[i]


MM = "mm"
CM = "cm"
M = "m"
KM = "km"
IN = "in"
FT = "ft"
YD = "yd"
MI = "mi"


class ScaleHandler(object):
    """
    A scale handling class that can be used to convert any common unit
    to another unit.

    Instead of containing formulas for every possible conversion, the
    class has a conversion from every common unit to centimeter and
    from centimeter to every common unit. Common unit types are
    [MM, CM, M, KM, IN, FT, YD, MI].

    Relevant methods:
        convert_to_unit(unit: str) -> float:
        Will convert the current unit and length to the given
        unit type.

    Example:
        >>> from core_utils import size
        >>> scale = size.ScaleHandler(CM, 100.0)
        >>> scale.convert_to_unit(size.M)
        >>> print(scale.length)
        >>> scale.length = 10.0
        >>> scale.unit = size.IN
        >>> print(scale.length)
        >>> print(scale.unit)
    """

    def __init__(self, unit: str = CM, length: float = 1.0) -> None:
        self.unit = unit
        self.length = length

    def __repr__(self) -> str:
        return f"Unit: {self.unit} - Length: {self.length}"

    def __str__(self) -> str:
        return str(self.unit)

    def convert_to_unit(self, unit: str) -> float:
        """
        Will convert the object's unit and length, in place, to the given unit
        type.

        Args:
            unit (str): One of the following: ['mm', 'cm', 'm', 'km', 'in', 'ft', 'yd', 'mi'].

        Returns:
            float: The converted length.
        """
        if self.unit == MM:
            self._convert_mm_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == M:
            self._convert_m_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == KM:
            self._convert_km_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == IN:
            self._convert_in_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == FT:
            self._convert_ft_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == YD:
            self._convert_yd_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == MI:
            self._convert_mi_to_cm(self.length)
            return self._convert_to_unit(unit)
        elif self.unit == CM:
            return self._convert_to_unit(unit)
        else:
            raise ValueError(f"Unsupported unit {self.unit}")

    def _convert_to_unit(self, unit: str) -> float:
        if unit == MM:
            self._convert_cm_to_mm(self.length)
        elif unit == M:
            self._convert_cm_to_m(self.length)
        elif unit == KM:
            self._convert_cm_to_km(self.length)
        elif unit == IN:
            self._convert_cm_to_in(self.length)
        elif unit == FT:
            self._convert_cm_to_ft(self.length)
        elif unit == YD:
            self._convert_cm_to_yd(self.length)
        elif unit == MI:
            self._convert_cm_to_mi(self.length)
        elif unit == CM:
            # Already in CM, no conversion needed
            pass
        else:
            raise ValueError(f"Unsupported unit {unit}")

        return self.length

    # -- Convert cm to unit --
    # Metric
    def _convert_cm_to_mm(self, num: float) -> float:
        self.length = num * 10.0
        self.unit = MM
        return self.length

    def _convert_cm_to_m(self, num: float) -> float:
        self.length = num / 100.0
        self.unit = M
        return self.length

    def _convert_cm_to_km(self, num: float) -> float:
        self.length = num / 100000.0
        self.unit = KM
        return self.length

    # Customary
    def _convert_cm_to_in(self, num: float) -> float:
        self.length = num / 2.54
        self.unit = IN
        return self.length

    def _convert_cm_to_ft(self, num: float) -> float:
        self.length = num / 30.48
        self.unit = FT
        return self.length

    def _convert_cm_to_yd(self, num: float) -> float:
        self.length = num / 91.44
        self.unit = YD
        return self.length

    def _convert_cm_to_mi(self, num: float) -> float:
        self.length = num / 160900.0
        self.unit = MI
        return self.length

    # -- Convert unit to cm --
    # Metric
    def _convert_mm_to_cm(self, num: float) -> float:
        self.length = num / 10.0
        self.unit = CM
        return self.length

    def _convert_m_to_cm(self, num: float) -> float:
        self.length = num * 100.0
        self.unit = CM
        return self.length

    def _convert_km_to_cm(self, num: float) -> float:
        self.length = num * 100000.0
        self.unit = CM
        return self.length

    # Customary
    def _convert_in_to_cm(self, num: float) -> float:
        self.length = num * 2.54
        self.unit = CM
        return self.length

    def _convert_ft_to_cm(self, num: float) -> float:
        self.length = num * 30.48
        self.unit = CM
        return self.length

    def _convert_yd_to_cm(self, num: float) -> float:
        self.length = num * 91.44
        self.unit = CM
        return self.length

    def _convert_mi_to_cm(self, num: float) -> float:
        self.length = num * 160900.0
        self.unit = CM
        return self.length
