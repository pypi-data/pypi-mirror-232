
import pytest
from adock.security import is_destructive

def test_is_destructive():
    # Test a non-destructive command
    result, reason = is_destructive("docker ps")
    assert not result
    assert reason == "non destructive."

    # Test a potentially destructive command
    result, reason = is_destructive("docker rmi")
    assert result
