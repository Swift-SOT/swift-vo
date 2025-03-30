from datetime import datetime

import pytest  # type: ignore[import-untyped]
from astropy.time import Time

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

    def test_t_min_is_not_datetime_type(self):
        """Test if t_max is of datetime type."""
        service = ObjObsSAPService(10.5, 20.3, 59000, 59001, 1500)
        assert service.t_min == Time(59000, format="mjd").datetime

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_header(self):
        """Test if vo_format_hard_coded includes correct header information."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()

        assert '<?xml version="1.0" encoding="UTF-8"?>' in result
        assert "<VOTABLE" in result
        assert "xsi:noNamespaceSchemaLocation" in result
        assert 'version="1.0">' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_description(self):
        """Test if vo_format_hard_coded includes correct description."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()

        assert "<DESCRIPTION>" in result
        assert "NASA Neil Gehrels Swift Observatory Science Operations Center" in result
        assert "Object Observability Simple Access Protocol (ObjObsSAP)" in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_info_fields(self):
        """Test if vo_format_hard_coded includes correct INFO fields."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()

        assert '<INFO name="QUERY_STATUS" value="OK"/>' in result
        assert '<INFO name="SERVICE PROTOCOL" value="1.0">' in result
        assert '<INFO name="POS" value="10.5,20.3"/>' in result
        assert '<INFO name="TIME" value="60000.0/60001.0"/>' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_table_structure(self):
        """Test if vo_format_hard_coded includes correct table structure."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        result = await service.vo_format_hard_coded()

        assert "<TABLE>" in result
        assert '<FIELD name="t_start"' in result
        assert '<FIELD name="t_stop"' in result
        assert '<FIELD name="t_observability"' in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_empty_windows(self):
        """Test if vo_format_hard_coded handles empty windows correctly."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, max_rec=0)
        result = await service.vo_format_hard_coded()

        assert "<DATA>" not in result
        assert "<TABLEDATA>" not in result
        assert "<TR>" not in result

    @pytest.mark.asyncio
    async def test_vo_format_hard_coded_with_windows(self):
        """Test if vo_format_hard_coded formats windows correctly."""
        service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
        service.windows = [(60000.0, 60001.0)]
        result = await service.vo_format_hard_coded()

        assert "<DATA>" in result
        assert "<TABLEDATA>" in result
        assert "<TR>" in result
        assert "<TD>60000.00000</TD>" in result
        assert "<TD>60001.00000</TD>" in result
        assert "<TD>86400</TD>" in result
