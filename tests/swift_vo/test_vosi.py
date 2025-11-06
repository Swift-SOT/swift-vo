"""Tests for VOSI-availability endpoint."""

from fastapi.testclient import TestClient

from swift_vo.vosi.api import app

client = TestClient(app)


class TestVOSIAvailability:
    """Tests for the VOSI availability endpoint."""

    def test_availability_endpoint_exists(self):
        """Test that the availability endpoint exists and returns 200."""
        response = client.get("/objobssap/availability")
        assert response.status_code == 200

    def test_availability_content_type(self):
        """Test that the availability endpoint returns XML content type."""
        response = client.get("/objobssap/availability")
        assert response.headers["content-type"] == "application/xml"

    def test_availability_xml_declaration(self):
        """Test that the availability endpoint returns XML declaration."""
        response = client.get("/objobssap/availability")
        content = response.content.decode("utf-8")
        assert "<?xml version='1.0' encoding='UTF-8'" in content

    def test_availability_namespace(self):
        """Test that the availability endpoint returns correct namespace."""
        response = client.get("/objobssap/availability")
        content = response.content.decode("utf-8")
        assert 'xmlns="http://www.ivoa.net/xml/VOSIAvailability/v1.0"' in content

    def test_availability_available_element(self):
        """Test that the availability endpoint returns available element."""
        response = client.get("/objobssap/availability")
        content = response.content.decode("utf-8")
        assert "<available>true</available>" in content

    def test_availability_upsince_element(self):
        """Test that the availability endpoint returns upSince element."""
        response = client.get("/objobssap/availability")
        content = response.content.decode("utf-8")
        assert "<upSince>" in content
        assert "</upSince>" in content

    def test_availability_case_insensitive(self):
        """Test that the availability endpoint is case-insensitive."""
        response = client.get("/objobssap/AVAILABILITY")
        assert response.status_code == 200

    def test_availability_with_trailing_slash(self):
        """Test that the availability endpoint works with trailing slash."""
        response = client.get("/objobssap/availability/")
        assert response.status_code in [200, 307]  # 307 is redirect


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

    def test_capabilities_xml_declaration(self):
        """Test that the capabilities response contains XML declaration."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "<?xml version='1.0' encoding='UTF-8'" in content

    def test_capabilities_namespace(self):
        """Test that the capabilities response contains VOSI capabilities namespace."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert 'xmlns:vosi="http://www.ivoa.net/xml/VOSICapabilities/v1.0"' in content

    def test_capabilities_has_capabilities_capability(self):
        """Test that the capabilities capability is present."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "ivo://ivoa.net/std/VOSI#capabilities" in content

    def test_capabilities_has_availability_capability(self):
        """Test that the availability capability is present."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "ivo://ivoa.net/std/VOSI#availability" in content

    def test_capabilities_has_query_capability(self):
        """Test that the query capability is present."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "ivo://ivoa.net/std/ObjObsSAP#query-1" in content

    def test_capabilities_has_capabilities_url(self):
        """Test that the capabilities access URL is present."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "capabilities" in content

    def test_capabilities_has_availability_url(self):
        """Test that the availability access URL is present."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "availability" in content

    def test_capabilities_has_query_url(self):
        """Test that the query access URL is present."""
        response = client.get("/objobssap/capabilities")
        content = response.text
        assert "query" in content
