import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from swift_vo.objobssap.api import app, parse_min_obs, parse_pos, parse_time

client = TestClient(app)


class TestParsePos:
    """Tests for the parse_pos function."""

    def test_valid_ra(self, valid_pos):
        """Test the parsing of a valid RA value."""
        pos = parse_pos(valid_pos)
        assert pos.s_ra == 10.5

    def test_valid_dec(self, valid_pos):
        """Test the parsing of a valid DEC value."""
        pos = parse_pos(valid_pos)
        assert pos.s_dec == 20.3

    def test_invalid(self):
        """Test the parsing of an invalid position value."""
        with pytest.raises(HTTPException):
            parse_pos("invalid")


class TestParseTime:
    """Tests for the parse_time function."""

    def test_valid_min(self, valid_time):
        """Test the parsing of a valid minimum time value."""
        time = parse_time(valid_time)
        assert time.t_min == 60000.0

    def test_valid_max(self, valid_time):
        """Test the parsing of a valid maximum time value."""
        time = parse_time(valid_time)
        assert time.t_max == 60001.0

    def test_invalid(self):
        """Test the parsing of an invalid time value."""
        with pytest.raises(HTTPException):
            parse_time("invalid")


class TestParseMinObs:
    """Tests for the parse_min_obs function."""

    def test_positive(self):
        """Test the parsing of a positive minimum observation value."""
        assert parse_min_obs(1500) == 1500.0

    def test_zero(self):
        """Test the parsing of a zero minimum observation value."""
        assert parse_min_obs(0) == 0.0


class TestObjObsSAP:
    """Tests for the ObjObsSAP endpoint."""

    def test_endpoint_status(self, query_params):
        """Test the status of the ObjObsSAP endpoint."""
        response = client.get("/ObjObsSAP/query", params=query_params)
        assert response.status_code == 200

    def test_endpoint_content_type(self, query_params):
        """Test the content type of the ObjObsSAP endpoint response."""
        response = client.get("/ObjObsSAP/query", params=query_params)
        assert response.headers["content-type"] == "application/x-votable+xml"

    def test_endpoint_content_length(self, query_params):
        """Test the content length of the ObjObsSAP endpoint response."""
        response = client.get("/ObjObsSAP/query", params=query_params)
        assert len(response.content) > 0

    def test_invalid_pos(self, valid_time, valid_min_obs):
        """Test the response for an invalid position value."""
        response = client.get(
            "/ObjObsSAP/query",
            params={"POS": "invalid", "TIME": valid_time, "MIN_OBS": valid_min_obs},
        )
        assert response.status_code == 422

    def test_invalid_time(self, valid_pos, valid_min_obs):
        """Test the response for an invalid time value."""
        response = client.get(
            "/ObjObsSAP/query",
            params={"POS": valid_pos, "TIME": "invalid", "MIN_OBS": valid_min_obs},
        )
        assert response.status_code == 422

    def test_default_time(self, valid_pos, valid_min_obs):
        """Test the that endpoint doesn't require TIME."""
        response = client.get("/ObjObsSAP/query", params={"POS": valid_pos, "MIN_OBS": valid_min_obs})
        assert response.status_code == 200


class TestVOSICapabilities:
    """Tests for the VOSI capabilities endpoint."""

    def test_capabilities_status(self):
        """Test the status of the capabilities endpoint."""
        response = client.get("/objobssap/capabilities")
        assert response.status_code == 200

    def test_capabilities_content_type(self):
        """Test the content type of the capabilities endpoint response."""
        response = client.get("/objobssap/capabilities")
        assert response.headers["content-type"] == "application/xml"

    def test_capabilities_content(self):
        """Test that the capabilities response contains required elements."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        # Verify XML declaration
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        # Verify VOSI capabilities namespace
        assert 'xmlns:vosi="http://www.ivoa.net/xml/VOSICapabilities/v1.0"' in content
        # Verify all three capabilities are present
        assert 'ivo://ivoa.net/std/VOSI#capabilities' in content
        assert 'ivo://ivoa.net/std/VOSI#availability' in content
        assert 'ivo://ivoa.net/std/ObjObsSAP#query-0.3' in content
        # Verify access URLs are present
        assert 'capabilities' in content
        assert 'availability' in content
        assert 'query' in content


class TestVOSIAvailability:
    """Tests for the VOSI availability endpoint."""

    def test_availability_status(self):
        """Test the status of the availability endpoint."""
        response = client.get("/objobssap/availability")
        assert response.status_code == 200

    def test_availability_content_type(self):
        """Test the content type of the availability endpoint response."""
        response = client.get("/objobssap/availability")
        assert response.headers["content-type"] == "application/xml"

    def test_availability_content(self):
        """Test that the availability response contains required elements."""
        response = client.get("/objobssap/availability")
        content = response.text
        # Verify XML declaration
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        # Verify VOSI availability namespace
        assert 'xmlns:vosi="http://www.ivoa.net/xml/VOSIAvailability/v1.0"' in content
        # Verify availability status
        assert '<vosi:available>true</vosi:available>' in content
