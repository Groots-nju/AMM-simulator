from decimal import Decimal
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.exceptions import PoolError
from src.models import SwapResult, Token
from src.pool import Pool


def build_pool(
    reserve0: Decimal = Decimal("100"),
    reserve1: Decimal = Decimal("200000"),
    fee_rate: Decimal = Decimal("0.003"),
) -> Pool:
    pool = Pool(
        token0=Token(symbol="ETH", name="Ether"),
        token1=Token(symbol="USDC", name="USD Coin"),
        fee_rate=fee_rate,
    )
    pool.initialize_pool("alice", reserve0, reserve1)
    return pool


def test_large_trade_keeps_reserves_positive_and_slippage_worsens() -> None:
    small_trade_pool = build_pool()
    big_trade_pool = build_pool()

    small_trade = small_trade_pool.swap_exact_in("small_trader", "ETH", Decimal("1"))
    big_trade = big_trade_pool.swap_exact_in("big_trader", "ETH", Decimal("90"))

    assert big_trade.amount_out > Decimal("0")
    assert big_trade.amount_out < Decimal("200000")
    assert big_trade_pool.reserve0 > Decimal("0")
    assert big_trade_pool.reserve1 > Decimal("0")
    assert abs(big_trade.slippage) > abs(small_trade.slippage)
    assert big_trade.execution_price_quote < big_trade.pre_trade_price_quote


def test_repeated_small_trades_keep_decimal_state_and_non_negative_reserves() -> None:
    pool = build_pool()
    initial_k = pool.invariant_k()
    last_result: SwapResult | None = None

    for _ in range(500):
        last_result = pool.swap_exact_in("bot", "ETH", Decimal("0.0001"))

    assert last_result is not None
    assert isinstance(pool.reserve0, Decimal)
    assert isinstance(pool.reserve1, Decimal)
    assert isinstance(last_result.amount_out, Decimal)
    assert pool.reserve0 > Decimal("0")
    assert pool.reserve1 > Decimal("0")
    assert pool.invariant_k() >= initial_k


def test_tiny_trade_that_rounds_to_zero_output_is_rejected() -> None:
    extreme_pool = build_pool(
        reserve0=Decimal("1E+999999"),
        reserve1=Decimal("1"),
        fee_rate=Decimal("0"),
    )

    with pytest.raises(PoolError, match="Swap output is zero or negative"):
        extreme_pool.swap_exact_in("dust_trader", "ETH", Decimal("1E-999999"))
