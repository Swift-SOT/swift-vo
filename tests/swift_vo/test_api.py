import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from swift_vo.objobssap.api import app, parse_min_obs, parse_pos, parse_time

client = TestClient(app)


def test_parse_pos_valid_ra():
    """Test the parsing of a valid RA value."""
    pos = parse_pos("10.5,20.3")
    assert pos.s_ra == 10.5


def test_parse_pos_valid_dec():
    """Test the parsing of a valid DEC value."""
    pos = parse_pos("10.5,20.3")
    assert pos.s_dec == 20.3


def test_parse_pos_invalid():
    """Test the parsing of an invalid position value."""
    with pytest.raises(HTTPException):
        parse_pos("invalid")


def test_parse_time_valid_min():
    """Test the parsing of a valid minimum time value."""
    time = parse_time("60000/60001")
    assert time.t_min == 60000.0


def test_parse_time_valid_max():
    """Test the parsing of a valid maximum time value."""
    time = parse_time("60000/60001")
    assert time.t_max == 60001.0


def test_parse_time_invalid():
    """Test the parsing of an invalid time value."""
    with pytest.raises(HTTPException):
        parse_time("invalid")


def test_parse_min_obs_positive():
    """Test the parsing of a positive minimum observation value."""
    assert parse_min_obs(1500) == 1500.0


def test_parse_min_obs_zero():
    """Test the parsing of a zero minimum observation value."""
    assert parse_min_obs(0) == 0.0


def test_objvissap_endpoint_status():
    """Test the status of the ObjObsSAP endpoint."""
    response = client.get(
        "/objobssap/query",
        params={"POS": "10.5,20.3", "TIME": "60000/60001", "MIN_OBS": "1500", "MAX_REC": "100"},
    )
    assert response.status_code == 200


def test_objvissap_endpoint_content_type():
    """Test the content type of the ObjObsSAP endpoint response."""
    response = client.get(
        "/objobssap/query",
        params={"POS": "10.5,20.3", "TIME": "60000/60001", "MIN_OBS": "1500", "MAX_REC": "100"},
    )
    assert response.headers["content-type"] == "application/xml"


def test_objvissap_endpoint_content_length():
    """Test the content length of the ObjObsSAP endpoint response."""
    response = client.get(
        "/objobssap/query",
        params={"POS": "10.5,20.3", "TIME": "60000/60001", "MIN_OBS": "1500", "MAX_REC": "100"},
    )
    assert len(response.content) > 0


def test_objvissap_invalid_pos():
    """Test the response for an invalid position value."""
    response = client.get(
        "/objobssap/query", params={"POS": "invalid", "TIME": "60000/60001", "MIN_OBS": "1.5"}
    )
    assert response.status_code == 422


def test_objvissap_invalid_time():
    """Test the response for an invalid time value."""
    response = client.get(
        "/objobssap/query", params={"POS": "10.5,20.3", "TIME": "invalid", "MIN_OBS": "1.5"}
    )
    assert response.status_code == 422
