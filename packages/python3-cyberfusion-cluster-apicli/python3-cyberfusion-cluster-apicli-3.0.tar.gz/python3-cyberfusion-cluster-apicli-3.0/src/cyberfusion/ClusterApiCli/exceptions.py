"""Exceptions."""

from dataclasses import dataclass


@dataclass
class ClusterApiCallException(Exception):
    """Exception to be raised in case API call failed."""

    body: str
    status_code: int


class MultipleAuthenticatorsMatchError(Exception):
    """Exception to raise when multiple authenticators match."""
