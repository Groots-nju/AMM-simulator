from decimal import Decimal
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.exceptions import PoolError
from src.exceptions import ValidationError
from src.pool import Pool
from src.models import Token


def build_pool() -> Pool:
    pool = Pool(
        token0=Token(symbol="ETH", name="Ether"),
        token1=Token(symbol="USDC", name="USD Coin"),
        fee_rate=Decimal("0.003"),
    )
    pool.initialize_pool("alice", Decimal("100"), Decimal("200000"))
    return pool


def test_swap_formula_and_fee_are_correct() -> None:
    pool = build_pool()
    result = pool.swap_exact_in("trader", "ETH", Decimal("10"))

    expected_fee = Decimal("10") * Decimal("0.003")
    expected_effective_in = Decimal("10") - expected_fee
    expected_amount_out = Decimal("200000") * expected_effective_in / (Decimal("100") + expected_effective_in)

    assert result.fee_amount == expected_fee
    assert result.effective_amount_in == expected_effective_in
    assert result.amount_out == expected_amount_out
    assert pool.reserve0 == Decimal("110")
    assert pool.reserve1 == Decimal("200000") - expected_amount_out


def test_slippage_is_negative_for_large_exact_in_trade() -> None:
    pool = build_pool()
    result = pool.swap_exact_in("trader", "ETH", Decimal("10"))

    assert result.pre_trade_price_quote == Decimal("2000")
    assert result.execution_price_quote < result.pre_trade_price_quote
    assert result.slippage < Decimal("0")


def test_add_liquidity_requires_pool_ratio() -> None:
    pool = build_pool()

    with pytest.raises(PoolError, match="Liquidity must be added proportionally"):
        pool.add_liquidity("bob", Decimal("20"), Decimal("30000"))


def test_swap_rejects_zero_input() -> None:
    pool = build_pool()

    with pytest.raises(ValidationError, match="amount_in must be positive"):
        pool.swap_exact_in("trader", "ETH", Decimal("0"))


def test_swap_rejects_negative_input() -> None:
    pool = build_pool()

    with pytest.raises(ValidationError, match="amount_in must be positive"):
        pool.swap_exact_in("trader", "ETH", Decimal("-1"))


def test_swap_rejects_unknown_token() -> None:
    pool = build_pool()

    with pytest.raises(PoolError, match="Unsupported token_in_symbol"):
        pool.swap_exact_in("trader", "BTC", Decimal("1"))
