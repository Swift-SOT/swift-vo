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
    async def test_vo_format_hard_coded_xml_version(self, basic_service):
        """Test if vo_format_hard_coded includes XML version."""
        result = await basic_service.vo_format_hard_coded()
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_votable_tag(self, basic_service):
        """Test if vo_format_hard_coded includes VOTABLE tag."""
        result = await basic_service.vo_format_hard_coded()
        assert "<VOTABLE" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_schema_location(self, basic_service):
        """Test if vo_format_hard_coded includes schema location."""
        result = await basic_service.vo_format_hard_coded()
        assert "xsi:noNamespaceSchemaLocation" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_version(self, basic_service):
        """Test if vo_format_hard_coded includes version."""
        result = await basic_service.vo_format_hard_coded()
        assert 'version="1.0">' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_description_tag(self, basic_service):
        """Test if vo_format_hard_coded includes description tag."""
        result = await basic_service.vo_format_hard_coded()
        assert "<DESCRIPTION>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_nasa_text(self, basic_service):
        """Test if vo_format_hard_coded includes NASA text."""
        result = await basic_service.vo_format_hard_coded()
        assert "NASA Neil Gehrels Swift Observatory Science Operations Center" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_protocol_text(self, basic_service):
        """Test if vo_format_hard_coded includes protocol text."""
        result = await basic_service.vo_format_hard_coded()
        assert "Object Observability Simple Access Protocol (ObjObsSAP)" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_query_status(self, basic_service):
        """Test if vo_format_hard_coded includes query status."""
        result = await basic_service.vo_format_hard_coded()
        assert '<INFO name="QUERY_STATUS" value="OK"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_service_protocol(self, basic_service):
        """Test if vo_format_hard_coded includes service protocol."""
        result = await basic_service.vo_format_hard_coded()
        assert '<INFO name="SERVICE PROTOCOL" value="1.0">' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_pos_info(self, basic_service):
        """Test if vo_format_hard_coded includes position info."""
        result = await basic_service.vo_format_hard_coded()
        assert '<INFO name="POS" value="10.5,20.3"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_time_info(self, basic_service):
        """Test if vo_format_hard_coded includes time info."""
        result = await basic_service.vo_format_hard_coded()
        assert '<INFO name="TIME" value="60000.0/60001.0"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_table_tag(self, basic_service):
        """Test if vo_format_hard_coded includes table tag."""
        result = await basic_service.vo_format_hard_coded()
        assert "<TABLE>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_t_start_field(self, basic_service):
        """Test if vo_format_hard_coded includes t_start field."""
        result = await basic_service.vo_format_hard_coded()
        assert '<FIELD name="t_start"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_t_stop_field(self, basic_service):
        """Test if vo_format_hard_coded includes t_stop field."""
        result = await basic_service.vo_format_hard_coded()
        assert '<FIELD name="t_stop"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_t_observability_field(self, basic_service):
        """Test if vo_format_hard_coded includes t_observability field."""
        result = await basic_service.vo_format_hard_coded()
        assert '<FIELD name="t_observability"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_no_data_empty_windows(self, service_with_maxrec_zero):
        """Test if vo_format_hard_coded has no DATA tag with empty windows."""
        result = await service_with_maxrec_zero.vo_format_hard_coded()
        assert "<DATA>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_no_tabledata_empty_windows(self, service_with_maxrec_zero):
        """Test if vo_format_hard_coded has no TABLEDATA tag with empty windows."""
        result = await service_with_maxrec_zero.vo_format_hard_coded()
        assert "<TABLEDATA>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_no_tr_empty_windows(self, service_with_maxrec_zero):
        """Test if vo_format_hard_coded has no TR tag with empty windows."""
        result = await service_with_maxrec_zero.vo_format_hard_coded()
        assert "<TR>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_data_tag_with_windows(self, service_with_windows):
        """Test if vo_format_hard_coded includes DATA tag with windows."""
        result = await service_with_windows.vo_format_hard_coded()
        assert "<DATA>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_tabledata_tag_with_windows(self, service_with_windows):
        """Test if vo_format_hard_coded includes TABLEDATA tag with windows."""
        result = await service_with_windows.vo_format_hard_coded()
        assert "<TABLEDATA>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_tr_tag_with_windows(self, service_with_windows):
        """Test if vo_format_hard_coded includes TR tag with windows."""
        result = await service_with_windows.vo_format_hard_coded()
        assert "<TR>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_start_time_with_windows(self, service_with_windows):
        """Test if vo_format_hard_coded includes correct start time with windows."""
        result = await service_with_windows.vo_format_hard_coded()
        assert "<TD>60000.00000</TD>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_stop_time_with_windows(self, service_with_windows):
        """Test if vo_format_hard_coded includes correct stop time with windows."""
        result = await service_with_windows.vo_format_hard_coded()
        assert "<TD>60001.00000</TD>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_observability_with_windows(self, service_with_windows):
        """Test if vo_format_hard_coded includes correct observability with windows."""
        result = await service_with_windows.vo_format_hard_coded()
        assert "<TD>86400</TD>" in result

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
