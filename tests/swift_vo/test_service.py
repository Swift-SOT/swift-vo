from datetime import datetime

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

    def test_t_min_is_not_datetime_type(self):
        """Test if t_max is of datetime type."""
        service = ObjObsSAPService(10.5, 20.3, 59000, 59001, 1500)
        assert service.t_min == Time(59000, format="mjd").datetime
