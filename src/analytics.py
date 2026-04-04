"""Pure analytics functions for LP and IL calculations."""

from __future__ import annotations

from decimal import Decimal

from .decimal_utils import DECIMAL_ONE, require_positive
from .exceptions import PoolError
from .models import ILAnalysis, LPPosition
from .pool import Pool


def calculate_slippage(pre_trade_price: Decimal, execution_price: Decimal) -> Decimal:
    require_positive(pre_trade_price, field_name="pre_trade_price")
    require_positive(execution_price, field_name="execution_price")
    return (execution_price / pre_trade_price) - DECIMAL_ONE


def analyze_impermanent_loss(
    pool: Pool,
    position: LPPosition,
    external_price_token1_per_token0: Decimal,
) -> ILAnalysis:
    require_positive(external_price_token1_per_token0, field_name="external_price_token1_per_token0")
    if pool.total_lp_shares <= Decimal("0"):
        raise PoolError("Pool must have LP shares before IL analysis.")
    if position.shares <= Decimal("0"):
        raise PoolError("LP position must have positive shares.")

    share_ratio = position.shares / pool.total_lp_shares
    invariant_k = pool.invariant_k()

    theoretical_reserve0 = (invariant_k / external_price_token1_per_token0).sqrt()
    theoretical_reserve1 = (invariant_k * external_price_token1_per_token0).sqrt()

    position_token0 = share_ratio * theoretical_reserve0
    position_token1 = share_ratio * theoretical_reserve1

    lp_value_in_token1 = position_token0 * external_price_token1_per_token0 + position_token1
    hodl_value_in_token1 = (
        position.deposited_token0 * external_price_token1_per_token0 + position.deposited_token1
    )
    impermanent_loss_pct = (lp_value_in_token1 / hodl_value_in_token1) - DECIMAL_ONE
    value_difference_in_token1 = lp_value_in_token1 - hodl_value_in_token1

    return ILAnalysis(
        owner_id=position.owner_id,
        external_price_token1_per_token0=external_price_token1_per_token0,
        share_ratio=share_ratio,
        theoretical_pool_reserve0=theoretical_reserve0,
        theoretical_pool_reserve1=theoretical_reserve1,
        position_token0=position_token0,
        position_token1=position_token1,
        lp_value_in_token1=lp_value_in_token1,
        hodl_value_in_token1=hodl_value_in_token1,
        impermanent_loss_pct=impermanent_loss_pct,
        value_difference_in_token1=value_difference_in_token1,
    )
