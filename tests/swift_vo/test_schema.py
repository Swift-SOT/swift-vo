import pytest
from fastapi import HTTPException

from swift_vo.objobssap.schema import ObjObsSAPQueryParameters, VOPosition, VOTimeRange, mjdnow


class TestMjdnow:
    """Tests for the mjdnow function."""

    def test_mjdnow(self):
        """Test that mjdnow returns a float."""
        result = mjdnow()
        assert isinstance(result, float)
        assert result > 0


class TestVOTimeRange:
    """Tests for the VOTimeRange class."""

    def test_votime_range_creation(self, valid_time_range):
        """Test creating VOTimeRange with valid values."""
        assert valid_time_range.t_min == 50000.0
        assert valid_time_range.t_max == 60000.0

    def test_votime_range_from_string_valid(self):
        """Test parsing valid time range string."""
        time_range = VOTimeRange.from_string("50000/60000")
        assert time_range.t_min == 50000.0
        assert time_range.t_max == 60000.0

    def test_votime_range_from_string_invalid(self):
        """Test parsing invalid time range string."""
        with pytest.raises(HTTPException):
            VOTimeRange.from_string("invalid")


class TestVOPosition:
    """Tests for the VOPosition class."""

    def test_voposition_creation(self, valid_position):
        """Test creating VOPosition with valid values."""
        assert valid_position.s_ra == 10.5
        assert valid_position.s_dec == 20.3

    def test_voposition_from_string_valid(self):
        """Test parsing valid position string."""
        position = VOPosition.from_string("10.5,20.3")
        assert position.s_ra == 10.5
        assert position.s_dec == 20.3

    def test_voposition_from_string_invalid(self):
        """Test parsing invalid position string."""
        with pytest.raises(HTTPException):
            VOPosition.from_string("invalid")


class TestObjObsSAPQueryParameters:
    """Tests for the ObjObsSAPQueryParameters class."""

    def test_query_parameters(self, valid_position, valid_time_range):
        """Test creating query parameters."""
        params = ObjObsSAPQueryParameters(pos=valid_position, time=valid_time_range, min_obs=1500.0)
        assert params.pos == valid_position
        assert params.time == valid_time_range
        assert params.min_obs == 1500.0
