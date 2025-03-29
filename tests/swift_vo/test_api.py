from email.policy import HTTP
from fastapi import HTTPException
from fastapi.testclient import TestClient
from swift_vo.objobssap.api import app, parse_pos, parse_time, parse_min_obs
import pytest

client = TestClient(app)


def test_parse_pos():
    pos = parse_pos("10.5,20.3")
    assert pos.s_ra == 10.5
    assert pos.s_dec == 20.3

    with pytest.raises(HTTPException):
        parse_pos("invalid")


def test_parse_time():
    time = parse_time("60000/60001")
    assert time.t_min == 60000.0
    assert time.t_max == 60001.0

    with pytest.raises(HTTPException):
        parse_time("invalid")


def test_parse_min_obs():
    assert parse_min_obs(1500) == 1500.0
    assert parse_min_obs(0) == 0.0


def test_objvissap_endpoint():
    response = client.get(
        "/objobssap/query",
        params={"POS": "10.5,20.3", "TIME": "60000/60001", "MIN_OBS": "1500", "MAX_REC": "100"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/xml"
    assert len(response.content) > 0


def test_objvissap_invalid_params():
    response = client.get(
        "/objobssap/query", params={"POS": "invalid", "TIME": "60000/60001", "MIN_OBS": "1.5"}
    )
    assert response.status_code == 422

    response = client.get(
        "/objobssap/query", params={"POS": "10.5,20.3", "TIME": "invalid", "MIN_OBS": "1.5"}
    )
    assert response.status_code == 422
