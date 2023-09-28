"""
Huti Exceptions Module
"""
__all__ = (
    "PpipBaseError",
    "CommandNotFound",
    "InvalidArgument",
)


class PpipBaseError(Exception):
    """
    Base Exception from which all other custom Exceptions defined in semantic_release
    inherit
    """


class CommandNotFound(PpipBaseError):
    """
    Raised when function is called with invalid argument
    """


class InvalidArgument(PpipBaseError):
    """
    Raised when function is called with invalid argument
    """

