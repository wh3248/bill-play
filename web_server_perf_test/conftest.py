"""Configuration file to read options for pytests."""


def pytest_addoption(parser):
    """Add supported options"""

    parser.addoption("--wy", action="store", default="2002")
    parser.addoption("--wy_month", action="store", default="02")
    parser.addoption("--servers", action="store", default="gunicorn")
    parser.addoption("--scenarios", action="store", default="sleep")
    parser.addoption("--nparallel", action="store", default="32")
    parser.addoption("--sleep_time", action="store", default="20")

