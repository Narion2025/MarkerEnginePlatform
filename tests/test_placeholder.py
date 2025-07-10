from marker_engine import greet


def test_greet() -> None:
    assert greet("World") == "Hello, World!"
