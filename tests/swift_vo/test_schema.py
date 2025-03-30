import pytest
from fastapi import HTTPException

from swift_vo.objobssap.schema import ObjObsSAPQueryParameters, VOPosition, VOTimeRange, mjdnow


def test_mjdnow():
    """Test that mjdnow returns a float."""
    result = mjdnow()
    assert isinstance(result, float)
    assert result > 0


def test_votime_range_creation():
    """Test creating VOTimeRange with valid values."""
    time_range = VOTimeRange(t_min=50000.0, t_max=60000.0)
    assert time_range.t_min == 50000.0
    assert time_range.t_max == 60000.0


def test_votime_range_from_string_valid():
    """Test parsing valid time range string."""
    time_range = VOTimeRange.from_string("50000/60000")
    assert time_range.t_min == 50000.0
    assert time_range.t_max == 60000.0


def test_votime_range_from_string_invalid():
    """Test parsing invalid time range string."""
    with pytest.raises(HTTPException):
        VOTimeRange.from_string("invalid")


def test_voposition_creation():
    """Test creating VOPosition with valid values."""
    position = VOPosition(s_ra=10.5, s_dec=20.3)
    assert position.s_ra == 10.5
    assert position.s_dec == 20.3


def test_voposition_from_string_valid():
    """Test parsing valid position string."""
    position = VOPosition.from_string("10.5,20.3")
    assert position.s_ra == 10.5
    assert position.s_dec == 20.3


def test_voposition_from_string_invalid():
    """Test parsing invalid position string."""
    with pytest.raises(HTTPException):
        VOPosition.from_string("invalid")


def test_query_parameters():
    """Test creating query parameters."""
    position = VOPosition(s_ra=10.5, s_dec=20.3)
    time_range = VOTimeRange(t_min=50000.0, t_max=60000.0)
    params = ObjObsSAPQueryParameters(pos=position, time=time_range, min_obs=1500.0)
    assert params.pos == position
    assert params.time == time_range
    assert params.min_obs == 1500.0
