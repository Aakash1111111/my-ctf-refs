import pytest
from shell_manager import util


@pytest.mark.parametrize(
    "problem_name, expected_name",
    [
        ("Test Problem", "test-problem"),
        ("01234", "p01234"),
        ("1 2  spaces", "p1-2--spaces"),
    ],
)
def test_problem_name_sanitization(problem_name, expected_name):
    """Test valid problem names are correctly sanitized."""
    sanitized_name = util.sanitize_name(problem_name)
    assert expected_name == sanitized_name


@pytest.mark.parametrize("problem_name", ["", None,])
def test_invalid_prob_name_sanitization(problem_name):
    """Test invalid problem names raise an exception during sanitization."""
    with pytest.raises(Exception) as excep_info:
        util.sanitize_name(problem_name)
        assert "Can not sanitize an empty field" in str(excep_info.value)
