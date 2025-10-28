from datetime import datetime

import pytest  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]


class TestObjObsSAPService:
    """Test class for ObjObsSAPService which validates initialization and type conversion of parameters."""

    def test_s_ra_initialization(self, basic_service):
        """Test the initialization of s_ra parameter."""
        assert basic_service.s_ra == 10.5

    def test_s_dec_initialization(self, basic_service):
        """Test the initialization of s_dec parameter."""
        assert basic_service.s_dec == 20.3

    def test_t_min_initialization(self, basic_service):
        """Test the initialization of t_min parameter."""
        assert basic_service.t_min == Time(60000, format="mjd").datetime

    def test_t_max_initialization(self, basic_service):
        """Test the initialization of t_max parameter."""
        assert basic_service.t_max == Time(60001, format="mjd").datetime

    def test_min_obs_initialization(self, basic_service):
        """Test the initialization of min_obs parameter."""
        assert basic_service.min_obs == 1500

    def test_maxrec_default_initialization(self, basic_service):
        """Test the default initialization of maxrec parameter."""
        assert basic_service.maxrec is None

    def test_upload_default_initialization(self, basic_service):
        """Test the default initialization of upload parameter."""
        assert basic_service.upload is None

    def test_windows_default_initialization(self, basic_service):
        """Test the default initialization of windows parameter."""
        assert basic_service.windows == []

    def test_maxrec_optional_initialization(self, service_with_maxrec):
        """Test the optional initialization of maxrec parameter."""
        assert service_with_maxrec.maxrec == 100

    def test_upload_optional_initialization(self, service_with_upload):
        """Test the optional initialization of upload parameter."""
        assert service_with_upload.upload == "test.xml"

    def test_t_min_is_datetime_type(self, basic_service):
        """Test if t_min is of datetime type."""
        assert isinstance(basic_service.t_min, datetime)

    def test_t_max_is_datetime_type(self, basic_service):
        """Test if t_max is of datetime type."""
        assert isinstance(basic_service.t_max, datetime)

    def test_t_min_value(self, basic_service):
        """Test t_min value conversion."""
        assert basic_service.t_min == Time(60000, format="mjd").datetime

    @pytest.mark.asyncio
    async def test_upload_in_xml(self, service_with_upload):
        """Test if upload parameter is included in XML."""
        result = await service_with_upload.vo_format()
        assert '<INFO ID="UPLOAD" name="UPLOAD" value="test.xml"/>' in result

    @pytest.mark.asyncio
    async def test_windows_start_time_in_xml(self, service_with_windows):
        """Test if windows start time is included in XML."""
        result = await service_with_windows.vo_format()
        assert "<TD>60000</TD>" in result

    @pytest.mark.asyncio
    async def test_windows_stop_time_in_xml(self, service_with_windows):
        """Test if windows stop time is included in XML."""
        result = await service_with_windows.vo_format()
        assert "<TD>60001</TD>" in result

    @pytest.mark.asyncio
    async def test_windows_duration_in_xml(self, service_with_windows):
        """Test if windows duration is included in XML."""
        result = await service_with_windows.vo_format()
        assert "<TD>86400</TD>" in result

    @pytest.mark.asyncio
    async def test_t_observability_field_in_xml(self, service_with_windows):
        """Test if t_observability field is defined in XML."""
        result = await service_with_windows.vo_format()
        assert 'name="t_observability"' in result

    @pytest.mark.asyncio
    async def test_t_observability_value_in_xml(self, service_with_windows):
        """Test if t_observability value (duration in days) is included in XML."""
        result = await service_with_windows.vo_format()
        # t_observability should be 1 day (60001 - 60000 = 1)
        assert "<TD>1.0</TD>" in result

    @pytest.mark.asyncio
    async def test_field_count_in_xml(self, service_with_windows):
        """Test if XML has correct number of fields."""
        result = await service_with_windows.vo_format()
        field_count = result.count("<FIELD")
        # Verify we have all expected fields: t_start, t_stop, t_observability
        expected_fields = ["t_start", "t_stop", "t_observability"]
        assert field_count == len(expected_fields)
        for field in expected_fields:
            assert f'name="{field}"' in result
