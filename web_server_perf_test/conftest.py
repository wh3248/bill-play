"""Configuration file to read options for pytests."""


def pytest_addoption(parser):
    """Add supported options"""

    parser.addoption("--wy", action="store", default="2002")
    parser.addoption("--wy_month", action="store", default="02")
    parser.addoption("--server", action="store", default="gunicorn")
    parser.addoption("--scenario", action="store", default="sleep")
    parser.addoption("--parallel", action="store", default="1")
    parser.addoption("--sleep_time", action="store", default="2")
    parser.addoption("--days", action="store", default="2")
    parser.addoption("--grid_size", action="store", default="8")

