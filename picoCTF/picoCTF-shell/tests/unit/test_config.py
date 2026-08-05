import pytest
from shell_manager import config


@pytest.mark.parametrize(
    "port_range, expected_string",
    [
        ([dict(start=0, end=65535)], "[0-65535]"),
        ([dict(start=1000, end=1000)], "[1000]"),
        (
            [dict(start=1000, end=1000), dict(start=1000, end=10000)],
            "[1000, 1000-10000]",
        ),
    ],
)
def test_port_range_to_str(port_range, expected_string):
    """Test strings are correctly created from port range lists."""
    returned_string = config.banned_ports_to_str(port_range)
    assert expected_string == returned_string
