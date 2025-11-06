import pytest
from fastapi import HTTPException

from swift_vo.objobssap.schema import ObjObsSAPQueryParameters, VOPosition, VOTimeRange, mjdnow


class TestMjdnow:
    """
    Test suite for the mjdnow function.
    """

    def test_mjdnow_returns_float(self):
        """Test that mjdnow returns a float value."""
        result = mjdnow()
        assert isinstance(result, float)

    def test_mjdnow_is_positive(self):
        """Test that mjdnow returns a positive value."""
        result = mjdnow()
        assert result > 0


class TestVOTimeRange:
    """
    Test suite for VOTimeRange class.

    This class tests the creation, parsing, and validation of VOTimeRange objects,
    which represent time ranges in the VO (Virtual Observatory) format.
    """

    def test_votime_range_creation_t_min(self, valid_time_range):
        """Test that the minimum time value is correctly set during VOTimeRange creation."""
        assert valid_time_range.t_min == 50000.0

    def test_votime_range_creation_t_max(self, valid_time_range):
        """Test that the maximum time value is correctly set during VOTimeRange creation."""
        assert valid_time_range.t_max == 60000.0

    def test_votime_range_from_string_valid_t_min(self):
        """Test that from_string correctly parses the minimum time from a valid time range string."""
        time_range = VOTimeRange.from_string("50000/60000")
        assert time_range.t_min == 50000.0

    def test_votime_range_from_string_valid_t_max(self):
        """Test that from_string correctly parses the maximum time from a valid time range string."""
        time_range = VOTimeRange.from_string("50000/60000")
        assert time_range.t_max == 60000.0

    def test_votime_range_from_string_invalid(self):
        """Test that from_string raises HTTPException when given an invalid time range string."""
        with pytest.raises(HTTPException):
            VOTimeRange.from_string("invalid")


class TestVOPosition:
    """
    Test suite for VOPosition class.
    """

    def test_voposition_creation_s_ra(self, valid_position):
        """Test that the RA value is correctly set during VOPosition creation."""
        assert valid_position.s_ra == 10.5

    def test_voposition_creation_s_dec(self, valid_position):
        """Test that the DEC value is correctly set during VOPosition creation."""
        assert valid_position.s_dec == 20.3

    def test_voposition_from_string_valid_s_ra(self):
        """Test that from_string correctly parses the RA value from a valid position string."""
        position = VOPosition.from_string("10.5,20.3")
        assert position.s_ra == 10.5

    def test_voposition_from_string_valid_s_dec(self):
        """Test that from_string correctly parses the DEC value from a valid position string."""
        position = VOPosition.from_string("10.5,20.3")
        assert position.s_dec == 20.3

    def test_voposition_from_string_invalid(self):
        """Test that from_string raises HTTPException when given an invalid position string."""
        with pytest.raises(HTTPException):
            VOPosition.from_string("invalid")


class TestObjObsSAPQueryParameters:
    """
    Test suite for ObjObsSAPQueryParameters class.
    """

    def test_query_parameters_pos(self, valid_position, valid_time_range):
        """Test the pos parameter of ObjObsSAPQueryParameters."""
        params = ObjObsSAPQueryParameters(pos=valid_position, time=valid_time_range, min_obs=1500.0)
        assert params.pos == valid_position

    def test_query_parameters_time(self, valid_position, valid_time_range):
        """Test the time parameter of ObjObsSAPQueryParameters."""
        params = ObjObsSAPQueryParameters(pos=valid_position, time=valid_time_range, min_obs=1500.0)
        assert params.time == valid_time_range

    def test_query_parameters_min_obs(self, valid_position, valid_time_range):
        """Test the min_obs parameter of ObjObsSAPQueryParameters."""
        params = ObjObsSAPQueryParameters(pos=valid_position, time=valid_time_range, min_obs=1500.0)
        assert params.min_obs == 1500.0
