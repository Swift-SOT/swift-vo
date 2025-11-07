import pytest

from swift_vo.objobssap.schema import VOPosition, VOTimeRange
from swift_vo.objobssap.service import ObjObsSAPService


@pytest.fixture
def basic_service():
    """Fixture providing a basic ObjObsSAPService instance."""
    return ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)


@pytest.fixture
def service_with_maxrec():
    """Fixture providing a service with maxrec parameter."""
    return ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, maxrec=100)


@pytest.fixture
def service_with_upload():
    """Fixture providing a service with upload parameter."""
    return ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500, upload="test.xml")


@pytest.fixture
def service_with_windows():
    """Fixture providing a service with windows data."""
    service = ObjObsSAPService(10.5, 20.3, 60000, 60001, 1500)
    service.windows = [(60000.0, 60001.0)]
    return service


@pytest.fixture
def valid_pos():
    """Valid position string."""
    return "10.5,20.3"


@pytest.fixture
def valid_time():
    """Valid time range string."""
    return "60000/60001"


@pytest.fixture
def valid_min_obs():
    """Valid minimum observation value."""
    return "1500"


@pytest.fixture
def valid_maxrec():
    """Valid maximum records value."""
    return "100"


@pytest.fixture
def query_params(valid_pos, valid_time, valid_min_obs, valid_maxrec):
    """Common query parameters for endpoint tests."""
    return {
        "pos": valid_pos,
        "time": valid_time,
        "min_obs": valid_min_obs,
        "maxrec": valid_maxrec,
    }


@pytest.fixture
def valid_position():
    """Fixture for a valid VOPosition."""
    return VOPosition(s_ra=10.5, s_dec=20.3)


@pytest.fixture
def valid_time_range():
    """Fixture for a valid VOTimeRange."""
    return VOTimeRange(t_min=50000.0, t_max=60000.0)


@pytest.fixture
def expected_fields():
    """Expected field names in the VO format XML."""
    return ["t_validity", "t_start", "t_stop", "t_observability"]


@pytest.fixture
def field(request, expected_fields):
    """Fixture to get expected field names by index."""
    return expected_fields[request.param]
