"""Core AMM pool implementation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .decimal_utils import DECIMAL_ONE, DECIMAL_ZERO, decimal_sqrt, require_positive
from .exceptions import PoolError
from .models import LPPosition, Snapshot, SwapResult, Token


@dataclass
class Pool:
    token0: Token
    token1: Token
    fee_rate: Decimal
    reserve0: Decimal = DECIMAL_ZERO
    reserve1: Decimal = DECIMAL_ZERO
    total_lp_shares: Decimal = DECIMAL_ZERO
    cumulative_fees_token0: Decimal = DECIMAL_ZERO
    cumulative_fees_token1: Decimal = DECIMAL_ZERO
    liquidity_tolerance: Decimal = Decimal("0.000000000001")

    def __post_init__(self) -> None:
        if not (DECIMAL_ZERO <= self.fee_rate < DECIMAL_ONE):
            raise PoolError(f"fee_rate must be in [0, 1), got {self.fee_rate}.")
        if self.reserve0 < DECIMAL_ZERO or self.reserve1 < DECIMAL_ZERO:
            raise PoolError("Initial reserves must be non-negative.")

    def invariant_k(self) -> Decimal:
        return self.reserve0 * self.reserve1

    def spot_price_token1_per_token0(self) -> Decimal:
        if self.reserve0 <= DECIMAL_ZERO or self.reserve1 <= DECIMAL_ZERO:
            raise PoolError("Cannot compute spot price for an empty pool.")
        return self.reserve1 / self.reserve0

    def initialize_pool(self, owner_id: str, amount0: Decimal, amount1: Decimal) -> LPPosition:
        require_positive(amount0, field_name="initial amount0")
        require_positive(amount1, field_name="initial amount1")
        if self.total_lp_shares != DECIMAL_ZERO or self.reserve0 != DECIMAL_ZERO or self.reserve1 != DECIMAL_ZERO:
            raise PoolError("Pool is already initialized.")

        self.reserve0 = amount0
        self.reserve1 = amount1
        minted_shares = decimal_sqrt(amount0 * amount1)
        self.total_lp_shares = minted_shares
        return LPPosition(
            owner_id=owner_id,
            shares=minted_shares,
            deposited_token0=amount0,
            deposited_token1=amount1,
        )

    def add_liquidity(self, owner_id: str, amount0: Decimal, amount1: Decimal) -> LPPosition:
        require_positive(amount0, field_name="amount0")
        require_positive(amount1, field_name="amount1")
        if self.total_lp_shares <= DECIMAL_ZERO:
            raise PoolError("Pool must be initialized before adding liquidity.")

        expected_amount1 = amount0 * self.reserve1 / self.reserve0
        if abs(expected_amount1 - amount1) > self.liquidity_tolerance:
            raise PoolError(
                "Liquidity must be added proportionally. "
                f"Expected amount1={expected_amount1}, got {amount1}."
            )

        minted_shares = amount0 * self.total_lp_shares / self.reserve0
        self.reserve0 += amount0
        self.reserve1 += amount1
        self.total_lp_shares += minted_shares

        return LPPosition(
            owner_id=owner_id,
            shares=minted_shares,
            deposited_token0=amount0,
            deposited_token1=amount1,
        )

    def swap_exact_in(self, actor: str, token_in_symbol: str, amount_in: Decimal) -> SwapResult:
        require_positive(amount_in, field_name="amount_in")
        if self.total_lp_shares <= DECIMAL_ZERO:
            raise PoolError("Pool must be initialized before swaps.")

        if token_in_symbol == self.token0.symbol:
            reserve_in = self.reserve0
            reserve_out = self.reserve1
            token_out_symbol = self.token1.symbol
            pre_trade_price = reserve_out / reserve_in
            fee_amount = amount_in * self.fee_rate
            effective_amount_in = amount_in - fee_amount
            amount_out = reserve_out * effective_amount_in / (reserve_in + effective_amount_in)
            new_reserve0 = self.reserve0 + amount_in
            new_reserve1 = self.reserve1 - amount_out
            self.cumulative_fees_token0 += fee_amount
            self.reserve0 = new_reserve0
            self.reserve1 = new_reserve1
        elif token_in_symbol == self.token1.symbol:
            reserve_in = self.reserve1
            reserve_out = self.reserve0
            token_out_symbol = self.token0.symbol
            pre_trade_price = reserve_out / reserve_in
            fee_amount = amount_in * self.fee_rate
            effective_amount_in = amount_in - fee_amount
            amount_out = reserve_out * effective_amount_in / (reserve_in + effective_amount_in)
            new_reserve1 = self.reserve1 + amount_in
            new_reserve0 = self.reserve0 - amount_out
            self.cumulative_fees_token1 += fee_amount
            self.reserve0 = new_reserve0
            self.reserve1 = new_reserve1
        else:
            raise PoolError(f"Unsupported token_in_symbol: {token_in_symbol}")

        if amount_out <= DECIMAL_ZERO:
            raise PoolError("Swap output is zero or negative.")
        if self.reserve0 <= DECIMAL_ZERO or self.reserve1 <= DECIMAL_ZERO:
            raise PoolError("Swap would deplete the pool.")

        post_trade_price = self.reserve1 / self.reserve0 if token_in_symbol == self.token0.symbol else self.reserve0 / self.reserve1
        execution_price = amount_out / amount_in
        slippage = (execution_price / pre_trade_price) - DECIMAL_ONE

        return SwapResult(
            actor=actor,
            token_in_symbol=token_in_symbol,
            token_out_symbol=token_out_symbol,
            amount_in=amount_in,
            effective_amount_in=effective_amount_in,
            fee_amount=fee_amount,
            amount_out=amount_out,
            pre_trade_price_quote=pre_trade_price,
            post_trade_price_quote=post_trade_price,
            execution_price_quote=execution_price,
            slippage=slippage,
            reserve0_after=self.reserve0,
            reserve1_after=self.reserve1,
        )

    def snapshot(
        self,
        *,
        step: int,
        timestamp: int,
        event_type: str,
        external_price_token1_per_token0: Decimal | None = None,
    ) -> Snapshot:
        return Snapshot(
            step=step,
            timestamp=timestamp,
            event_type=event_type,
            reserve0=self.reserve0,
            reserve1=self.reserve1,
            spot_price_token1_per_token0=self.spot_price_token1_per_token0(),
            invariant_k=self.invariant_k(),
            total_lp_shares=self.total_lp_shares,
            external_price_token1_per_token0=external_price_token1_per_token0,
        )
