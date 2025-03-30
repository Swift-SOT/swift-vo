from datetime import datetime

import pytest  # type: ignore[import-untyped]
from astropy.time import Time  # type: ignore[import-untyped]

from swift_vo.objobssap.service import ObjObsSAPService


class TestObjObsSAPService:
    """Test class for ObjObsSAPService which validates initialization and type conversion of parameters."""

    def test_s_ra_initialization(self):
        """Test the initialization of s_ra parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.s_ra == 10.5

    def test_s_dec_initialization(self):
        """Test the initialization of s_dec parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.s_dec == 20.3

    def test_t_min_initialization(self):
        """Test the initialization of t_min parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.t_min == Time(60000, format="mjd").datetime

    def test_t_max_initialization(self):
        """Test the initialization of t_max parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.t_max == Time(60001, format="mjd").datetime

    def test_min_obs_initialization(self):
        """Test the initialization of min_obs parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.min_obs == 1500

    def test_max_rec_default_initialization(self):
        """Test the default initialization of max_rec parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.max_rec is None

    def test_upload_default_initialization(self):
        """Test the default initialization of upload parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.upload is None

    def test_windows_default_initialization(self):
        """Test the default initialization of windows parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        assert service.windows == []

    def test_max_rec_optional_initialization(self):
        """Test the optional initialization of max_rec parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, max_rec=100)
        assert service.max_rec == 100

    def test_upload_optional_initialization(self):
        """Test the optional initialization of upload parameter."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, upload="test.xml")
        assert service.upload == "test.xml"

    def test_t_min_is_datetime_type(self):
        """Test if t_min is of datetime type."""
        service = ObjObsSAPService(10.5, 20.3, 59000, 59001, 1500)
        assert isinstance(service.t_min, datetime)

    def test_t_max_is_datetime_type(self):
        """Test if t_max is of datetime type."""
        service = ObjObsSAPService(10.5, 20.3, 59000, 59001, 1500)
        assert isinstance(service.t_max, datetime)

    def test_t_min_value(self):
        """Test t_min value conversion."""
        service = ObjObsSAPService(10.5, 20.3, 59000, 59001, 1500)
        assert service.t_min == Time(59000, format="mjd").datetime

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_xml_version(self):
        """Test if vo_format_hard_coded includes XML version."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<?xml version="1.0" encoding="UTF-8"?>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_votable_tag(self):
        """Test if vo_format_hard_coded includes VOTABLE tag."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert "<VOTABLE" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_schema_location(self):
        """Test if vo_format_hard_coded includes schema location."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert "xsi:noNamespaceSchemaLocation" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_version(self):
        """Test if vo_format_hard_coded includes version."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert 'version="1.0">' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_description_tag(self):
        """Test if vo_format_hard_coded includes description tag."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert "<DESCRIPTION>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_nasa_text(self):
        """Test if vo_format_hard_coded includes NASA text."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert "NASA Neil Gehrels Swift Observatory Science Operations Center" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_protocol_text(self):
        """Test if vo_format_hard_coded includes protocol text."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert "Object Observability Simple Access Protocol (ObjObsSAP)" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_query_status(self):
        """Test if vo_format_hard_coded includes query status."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<INFO name="QUERY_STATUS" value="OK"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_service_protocol(self):
        """Test if vo_format_hard_coded includes service protocol."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<INFO name="SERVICE PROTOCOL" value="1.0">' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_pos_info(self):
        """Test if vo_format_hard_coded includes position info."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<INFO name="POS" value="10.5,20.3"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_time_info(self):
        """Test if vo_format_hard_coded includes time info."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<INFO name="TIME" value="60000.0/60001.0"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_table_tag(self):
        """Test if vo_format_hard_coded includes table tag."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert "<TABLE>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_t_start_field(self):
        """Test if vo_format_hard_coded includes t_start field."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<FIELD name="t_start"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_t_stop_field(self):
        """Test if vo_format_hard_coded includes t_stop field."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<FIELD name="t_stop"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_t_observability_field(self):
        """Test if vo_format_hard_coded includes t_observability field."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()
        assert '<FIELD name="t_observability"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_no_data_empty_windows(self):
        """Test if vo_format_hard_coded has no DATA tag with empty windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, max_rec=0)
        result = await service.vo_format_hard_coded()
        assert "<DATA>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_no_tabledata_empty_windows(self):
        """Test if vo_format_hard_coded has no TABLEDATA tag with empty windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, max_rec=0)
        result = await service.vo_format_hard_coded()
        assert "<TABLEDATA>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_no_tr_empty_windows(self):
        """Test if vo_format_hard_coded has no TR tag with empty windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, max_rec=0)
        result = await service.vo_format_hard_coded()
        assert "<TR>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_data_tag_with_windows(self):
        """Test if vo_format_hard_coded includes DATA tag with windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()
        assert "<DATA>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_tabledata_tag_with_windows(self):
        """Test if vo_format_hard_coded includes TABLEDATA tag with windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()
        assert "<TABLEDATA>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_tr_tag_with_windows(self):
        """Test if vo_format_hard_coded includes TR tag with windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()
        assert "<TR>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_start_time_with_windows(self):
        """Test if vo_format_hard_coded includes correct start time with windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()
        assert "<TD>60000.00000</TD>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_stop_time_with_windows(self):
        """Test if vo_format_hard_coded includes correct stop time with windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()
        assert "<TD>60001.00000</TD>" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_observability_with_windows(self):
        """Test if vo_format_hard_coded includes correct observability with windows."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()
        assert "<TD>86400</TD>" in result

    @pytest.mark.asyncio
    async def test_upload_in_xml(self):
        """Test if upload parameter is included in XML."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, upload="test.xml")
        result = await service.vo_format()
        assert '<INFO ID="UPLOAD" name="UPLOAD" value="test.xml"/>' in result

    @pytest.mark.asyncio
    async def test_windows_start_time_in_xml(self):
        """Test if windows start time is included in XML."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format()
        assert "<TD>60000</TD>" in result

    @pytest.mark.asyncio
    async def test_windows_stop_time_in_xml(self):
        """Test if windows stop time is included in XML."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format()
        assert "<TD>60001</TD>" in result

    @pytest.mark.asyncio
    async def test_windows_duration_in_xml(self):
        """Test if windows duration is included in XML."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format()
        assert "<TD>86400</TD>" in result
