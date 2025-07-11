"""Smoke test for Docker image build verification."""


def test_smoke():
    """Basic smoke test to verify pytest runs in Docker."""
    assert True


def test_python_version():
    """Verify we're running Python 3.12."""
    import sys
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 12
