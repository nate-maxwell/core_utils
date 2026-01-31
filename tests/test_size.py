import pytest

from core_utils import size


# -----convert_size Tests------------------------------------------------------


class TestConvertSize(object):
    def test_convert_size_zero_bytes(self) -> None:
        result = size.convert_size(0)
        assert result == (0, "B")

    def test_convert_size_bytes(self) -> None:
        result = size.convert_size(500)
        assert result == (500.0, "B")

    def test_convert_size_kilobytes(self) -> None:
        result = size.convert_size(1024)
        assert result == (1.0, "KB")

    def test_convert_size_megabytes(self) -> None:
        result = size.convert_size(1048576)  # 1024 * 1024
        assert result == (1.0, "MB")

    def test_convert_size_gigabytes(self) -> None:
        result = size.convert_size(1073741824)  # 1024^3
        assert result == (1.0, "GB")

    def test_convert_size_terabytes(self) -> None:
        result = size.convert_size(1099511627776)  # 1024^4
        assert result == (1.0, "TB")

    def test_convert_size_decimal_values(self) -> None:
        result = size.convert_size(1536)  # 1.5 KB
        assert result == (1.5, "KB")

    def test_convert_size_rounds_to_two_decimals(self) -> None:
        result = size.convert_size(1234567)
        s, unit = result
        assert unit == "MB"
        assert s == 1.18

    def test_convert_size_large_value(self) -> None:
        result = size.convert_size(1024**8)  # 1 YB
        assert result == (1.0, "YB")

    def test_convert_size_chooses_most_concise_unit(self) -> None:
        result = size.convert_size(1100000000)  # Should be GB, not MB
        s, unit = result
        assert unit == "GB"


# -----ScaleHandler Tests------------------------------------------------------


class TestScaleHandlerInit(object):
    def test_scale_handler_default_init(self) -> None:
        scale = size.ScaleHandler()
        assert scale.unit == size.CM
        assert scale.length == 1.0

    def test_scale_handler_custom_init(self) -> None:
        scale = size.ScaleHandler(size.M, 5.0)
        assert scale.unit == size.M
        assert scale.length == 5.0

    def test_scale_handler_repr(self) -> None:
        scale = size.ScaleHandler(size.CM, 100.0)
        assert repr(scale) == "Unit: cm - Length: 100.0"

    def test_scale_handler_str(self) -> None:
        scale = size.ScaleHandler(size.M, 10.0)
        assert str(scale) == "m"


class TestScaleHandlerConversions(object):
    # Metric conversions
    def test_convert_mm_to_cm(self) -> None:
        scale = size.ScaleHandler(size.MM, 10.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 1.0
        assert result == 1.0

    def test_convert_cm_to_mm(self) -> None:
        scale = size.ScaleHandler(size.CM, 1.0)
        result = scale.convert_to_unit(size.MM)
        assert scale.unit == size.MM
        assert scale.length == 10.0
        assert result == 10.0

    def test_convert_m_to_cm(self) -> None:
        scale = size.ScaleHandler(size.M, 1.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 100.0
        assert result == 100.0

    def test_convert_cm_to_m(self) -> None:
        scale = size.ScaleHandler(size.CM, 100.0)
        result = scale.convert_to_unit(size.M)
        assert scale.unit == size.M
        assert scale.length == 1.0
        assert result == 1.0

    def test_convert_km_to_cm(self) -> None:
        scale = size.ScaleHandler(size.KM, 1.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 100000.0
        assert result == 100000.0

    def test_convert_cm_to_km(self) -> None:
        scale = size.ScaleHandler(size.CM, 100000.0)
        result = scale.convert_to_unit(size.KM)
        assert scale.unit == size.KM
        assert scale.length == 1.0
        assert result == 1.0

    # Imperial/Customary conversions
    def test_convert_in_to_cm(self) -> None:
        scale = size.ScaleHandler(size.IN, 1.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 2.54
        assert result == 2.54

    def test_convert_cm_to_in(self) -> None:
        scale = size.ScaleHandler(size.CM, 2.54)
        result = scale.convert_to_unit(size.IN)
        assert scale.unit == size.IN
        assert scale.length == 1.0
        assert result == 1.0

    def test_convert_ft_to_cm(self) -> None:
        scale = size.ScaleHandler(size.FT, 1.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 30.48
        assert result == 30.48

    def test_convert_cm_to_ft(self) -> None:
        scale = size.ScaleHandler(size.CM, 30.48)
        result = scale.convert_to_unit(size.FT)
        assert scale.unit == size.FT
        assert scale.length == 1.0
        assert result == 1.0

    def test_convert_yd_to_cm(self) -> None:
        scale = size.ScaleHandler(size.YD, 1.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 91.44
        assert result == 91.44

    def test_convert_cm_to_yd(self) -> None:
        scale = size.ScaleHandler(size.CM, 91.44)
        result = scale.convert_to_unit(size.YD)
        assert scale.unit == size.YD
        assert scale.length == 1.0
        assert result == 1.0

    def test_convert_mi_to_cm(self) -> None:
        scale = size.ScaleHandler(size.MI, 1.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 160900.0
        assert result == 160900.0

    def test_convert_cm_to_mi(self) -> None:
        scale = size.ScaleHandler(size.CM, 160900.0)
        result = scale.convert_to_unit(size.MI)
        assert scale.unit == size.MI
        assert scale.length == 1.0
        assert result == 1.0

    # Cross-system conversions (metric to imperial)
    def test_convert_m_to_ft(self) -> None:
        scale = size.ScaleHandler(size.M, 1.0)
        result = scale.convert_to_unit(size.FT)
        assert scale.unit == size.FT
        assert round(scale.length, 2) == 3.28
        assert round(result, 2) == 3.28

    def test_convert_km_to_mi(self) -> None:
        scale = size.ScaleHandler(size.KM, 1.0)
        result = scale.convert_to_unit(size.MI)
        assert scale.unit == size.MI
        assert round(scale.length, 2) == 0.62
        assert round(result, 2) == 0.62

    def test_convert_in_to_mm(self) -> None:
        scale = size.ScaleHandler(size.IN, 1.0)
        result = scale.convert_to_unit(size.MM)
        assert scale.unit == size.MM
        assert scale.length == 25.4
        assert result == 25.4

    # Same unit conversion
    def test_convert_cm_to_cm(self) -> None:
        scale = size.ScaleHandler(size.CM, 100.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.unit == size.CM
        assert scale.length == 100.0
        assert result == 100.0

    # Error handling
    def test_convert_to_unsupported_unit_raises_error(self) -> None:
        scale = size.ScaleHandler("invalid", 1.0)
        with pytest.raises(ValueError, match="Unsupported unit invalid"):
            scale.convert_to_unit(size.CM)


class TestScaleHandlerStateMutation(object):
    def test_scale_handler_updates_length_and_unit(self) -> None:
        scale = size.ScaleHandler(size.CM, 100.0)
        scale.convert_to_unit(size.M)
        assert scale.length == 1.0
        assert scale.unit == size.M

    def test_scale_handler_allows_manual_property_changes(self) -> None:
        scale = size.ScaleHandler(size.CM, 100.0)
        scale.length = 10.0
        scale.unit = size.IN
        assert scale.length == 10.0
        assert scale.unit == size.IN

    def test_multiple_conversions_in_sequence(self) -> None:
        scale = size.ScaleHandler(size.M, 1.0)
        scale.convert_to_unit(size.CM)
        assert scale.length == 100.0
        scale.convert_to_unit(size.MM)
        assert scale.length == 1000.0
        scale.convert_to_unit(size.M)
        assert scale.length == 1.0


class TestScaleHandlerEdgeCases(object):
    def test_zero_length(self) -> None:
        scale = size.ScaleHandler(size.M, 0.0)
        result = scale.convert_to_unit(size.FT)
        assert scale.length == 0.0
        assert result == 0.0

    def test_very_large_length(self) -> None:
        scale = size.ScaleHandler(size.MM, 1000000.0)
        result = scale.convert_to_unit(size.KM)
        assert scale.length == 1.0
        assert result == 1.0

    def test_very_small_length(self) -> None:
        scale = size.ScaleHandler(size.KM, 0.001)
        result = scale.convert_to_unit(size.M)
        assert scale.length == 1.0
        assert result == 1.0

    def test_negative_length(self) -> None:
        scale = size.ScaleHandler(size.M, -5.0)
        result = scale.convert_to_unit(size.CM)
        assert scale.length == -500.0
        assert result == -500.0


# This isn't strictly necessary, but it lets developers know if the enums have
# changed, creating a non-backwards-compatible update.


class TestScaleHandlerConstants(object):
    def test_unit_constants_exist(self) -> None:
        assert size.MM == "mm"
        assert size.CM == "cm"
        assert size.M == "m"
        assert size.KM == "km"
        assert size.IN == "in"
        assert size.FT == "ft"
        assert size.YD == "yd"
        assert size.MI == "mi"
