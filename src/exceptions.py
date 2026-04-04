"""Custom exceptions for the AMM simulator."""


class AMMSimulationError(Exception):
    """Base exception for the project."""


class ConfigError(AMMSimulationError):
    """Raised when configuration content is invalid."""


class PoolError(AMMSimulationError):
    """Raised when a pool action cannot be executed."""


class ValidationError(AMMSimulationError):
    """Raised when a user input or numeric value is invalid."""
