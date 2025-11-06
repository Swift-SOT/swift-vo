"""Tests for VOSI-availability endpoint."""

from fastapi.testclient import TestClient

from swift_vo.vosi.api import app

client = TestClient(app)


class TestVOSIAvailability:
    """Tests for the VOSI availability endpoint."""

    def test_availability_endpoint_exists(self):
        """Test that the availability endpoint exists and returns 200."""
        response = client.get("/availability")
        assert response.status_code == 200

    def test_availability_content_type(self):
        """Test that the availability endpoint returns XML content type."""
        response = client.get("/availability")
        assert response.headers["content-type"] == "application/xml"

    def test_availability_xml_structure(self):
        """Test that the availability endpoint returns valid XML with required elements."""
        response = client.get("/availability")
        content = response.content.decode("utf-8")

        # Check for XML declaration
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content

        # Check for availability namespace
        assert 'xmlns="http://www.ivoa.net/xml/VOSIAvailability/v1.0"' in content

        # Check for available element
        assert "<available>true</available>" in content

        # Check for upSince element
        assert "<upSince>" in content
        assert "</upSince>" in content

    def test_availability_case_insensitive(self):
        """Test that the availability endpoint is case-insensitive."""
        response = client.get("/AVAILABILITY")
        assert response.status_code == 200

    def test_availability_with_trailing_slash(self):
        """Test that the availability endpoint works with trailing slash."""
        response = client.get("/availability/")
        assert response.status_code in [200, 307]  # 307 is redirect
