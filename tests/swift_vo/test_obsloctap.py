import pytest
from fastapi.testclient import TestClient

from swift_vo.obsloctap.api import app, parse_pos, parse_time
from swift_vo.obsloctap.schema import ObsLocTAPPosition

client = TestClient(app)


class TestParsePos:
    """Tests for the parse_pos function."""

    def test_valid_ra_dec(self):
        """Test the parsing of a valid RA,DEC value."""
        pos = parse_pos("10.5,20.3")
        assert pos.s_ra == 10.5
        assert pos.s_dec == 20.3
        assert pos.s_radius == 0.197  # Default radius

    def test_valid_ra_dec_radius(self):
        """Test the parsing of a valid RA,DEC,RADIUS value."""
        pos = parse_pos("10.5,20.3,1.0")
        assert pos.s_ra == 10.5
        assert pos.s_dec == 20.3
        assert pos.s_radius == 1.0

    def test_invalid(self):
        """Test the parsing of an invalid position value."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            parse_pos("invalid")


class TestParseTime:
    """Tests for the parse_time function."""

    def test_valid_time(self):
        """Test the parsing of a valid time range."""
        time = parse_time("60000/60001")
        assert time.t_min == 60000.0
        assert time.t_max == 60001.0

    def test_default_time(self):
        """Test the parsing with default time (None)."""
        time = parse_time(None)
        assert time.t_min is not None
        assert time.t_max is not None
        assert time.t_max > time.t_min

    def test_invalid(self):
        """Test the parsing of an invalid time value."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            parse_time("invalid")


class TestObsLocTAP:
    """Tests for the ObsLocTAP endpoint."""

    def test_endpoint_status(self, obsloctap_query_params):
        """Test the status of the ObsLocTAP endpoint."""
        response = client.get("/obsloctap/query", params=obsloctap_query_params)
        assert response.status_code == 200

    def test_endpoint_content_type(self, obsloctap_query_params):
        """Test the content type of the ObsLocTAP endpoint response."""
        response = client.get("/obsloctap/query", params=obsloctap_query_params)
        assert response.headers["content-type"] == "application/x-votable+xml"

    def test_endpoint_content_length(self, obsloctap_query_params):
        """Test the content length of the ObsLocTAP endpoint response."""
        response = client.get("/obsloctap/query", params=obsloctap_query_params)
        assert len(response.content) > 0

    def test_invalid_pos(self):
        """Test the response for an invalid position value."""
        response = client.get(
            "/obsloctap/query",
            params={"POS": "invalid", "TIME": "60000/60001"},
        )
        assert response.status_code == 422

    def test_invalid_time(self):
        """Test the response for an invalid time value."""
        response = client.get(
            "/obsloctap/query",
            params={"POS": "10.5,20.3", "TIME": "invalid"},
        )
        assert response.status_code == 422

    def test_default_time(self):
        """Test that the endpoint doesn't require TIME."""
        response = client.get("/obsloctap/query", params={"pos": "10.5,20.3"})
        assert response.status_code == 200

    def test_with_radius(self):
        """Test query with explicit radius."""
        response = client.get("/obsloctap/query", params={"pos": "10.5,20.3,1.0", "time": "60000/60001"})
        assert response.status_code == 200

    def test_with_maxrec(self):
        """Test query with maxrec parameter."""
        response = client.get(
            "/obsloctap/query", params={"pos": "10.5,20.3", "time": "60000/60001", "maxrec": 5}
        )
        assert response.status_code == 200


class TestObsLocTAPSchema:
    """Tests for ObsLocTAP schema classes."""

    def test_position_from_string_two_parts(self):
        """Test creating position from RA,DEC string."""
        pos = ObsLocTAPPosition.from_string("10.5,20.3")
        assert pos.s_ra == 10.5
        assert pos.s_dec == 20.3
        assert pos.s_radius == 0.197

    def test_position_from_string_three_parts(self):
        """Test creating position from RA,DEC,RADIUS string."""
        pos = ObsLocTAPPosition.from_string("10.5,20.3,1.0")
        assert pos.s_ra == 10.5
        assert pos.s_dec == 20.3
        assert pos.s_radius == 1.0
