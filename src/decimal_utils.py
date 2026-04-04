"""Decimal helpers shared across the project."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import Any

from .exceptions import ValidationError

getcontext().prec = 50

DECIMAL_ZERO = Decimal("0")
DECIMAL_ONE = Decimal("1")
DISPLAY_QUANT = Decimal("0.000001")


def to_decimal(value: Any, *, field_name: str = "value") -> Decimal:
    """Convert config or runtime input into Decimal safely."""
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool):
        raise ValidationError(f"{field_name} must not be a boolean.")
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            raise ValidationError(f"{field_name} must not be empty.")
        return Decimal(cleaned)
    raise ValidationError(f"Unsupported type for {field_name}: {type(value)!r}")


def require_positive(value: Decimal, *, field_name: str) -> Decimal:
    if value <= DECIMAL_ZERO:
        raise ValidationError(f"{field_name} must be positive, got {value}.")
    return value


def require_non_negative(value: Decimal, *, field_name: str) -> Decimal:
    if value < DECIMAL_ZERO:
        raise ValidationError(f"{field_name} must be non-negative, got {value}.")
    return value


def decimal_sqrt(value: Decimal) -> Decimal:
    require_non_negative(value, field_name="sqrt input")
    return value.sqrt()


def format_decimal(value: Decimal, quant: Decimal = DISPLAY_QUANT) -> str:
    """Format Decimal for terminal output without exposing raw context precision."""
    normalized = value.quantize(quant, rounding=ROUND_HALF_UP)
    return format(normalized, "f")


def format_percent(value: Decimal) -> str:
    return f"{format_decimal(value * Decimal('100'))}%"
