"""Summary-building helpers for simulation outputs."""

from __future__ import annotations

from collections import Counter
from decimal import Decimal
from typing import Any

from .models import SimulationResult
from .pool import Pool


def build_summary(pool: Pool, result: SimulationResult) -> dict[str, Any]:
    final_snapshot = result.snapshots[-1]
    event_counts = Counter(record.event_type for record in result.event_records)
    final_total_lp_shares = final_snapshot.total_lp_shares

    final_lp_ownership_by_owner: dict[str, Decimal] = {}
    if final_total_lp_shares > Decimal("0"):
        final_lp_ownership_by_owner = {
            owner: position.shares / final_total_lp_shares
            for owner, position in result.lp_positions.items()
        }

    latest_lp_value = None
    latest_hodl_value = None
    latest_il_pct = None
    if result.il_analysis is not None:
        latest_lp_value = result.il_analysis.lp_value_in_token1
        latest_hodl_value = result.il_analysis.hodl_value_in_token1
        latest_il_pct = result.il_analysis.impermanent_loss_pct

    return {
        "scenario_name": result.scenario_name,
        "total_events": len(result.event_records),
        "swap_event_count": event_counts.get("swap", 0),
        "add_liquidity_event_count": event_counts.get("add_liquidity", 0),
        "external_price_update_event_count": event_counts.get("external_price_update", 0),
        "total_fees_collected": {
            pool.token0.symbol: pool.cumulative_fees_token0,
            pool.token1.symbol: pool.cumulative_fees_token1,
        },
        "final_spot_price": final_snapshot.spot_price_token1_per_token0,
        "final_reserve0": final_snapshot.reserve0,
        "final_reserve1": final_snapshot.reserve1,
        "final_total_lp_shares": final_total_lp_shares,
        "final_lp_ownership_by_owner": final_lp_ownership_by_owner,
        "latest_lp_value": latest_lp_value,
        "latest_hodl_value": latest_hodl_value,
        "latest_il_pct": latest_il_pct,
    }
