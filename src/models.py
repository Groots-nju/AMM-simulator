"""Data models used by the minimal AMM simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class Token:
    symbol: str
    name: str
    decimals: int = 18


@dataclass(frozen=True)
class Event:
    timestamp: int
    event_type: str
    actor: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class SwapResult:
    actor: str
    token_in_symbol: str
    token_out_symbol: str
    amount_in: Decimal
    effective_amount_in: Decimal
    fee_amount: Decimal
    amount_out: Decimal
    pre_trade_price_quote: Decimal
    post_trade_price_quote: Decimal
    execution_price_quote: Decimal
    slippage: Decimal
    reserve0_after: Decimal
    reserve1_after: Decimal


@dataclass
class LPPosition:
    owner_id: str
    shares: Decimal
    deposited_token0: Decimal
    deposited_token1: Decimal

    def add_deposit(self, amount0: Decimal, amount1: Decimal, minted_shares: Decimal) -> None:
        self.deposited_token0 += amount0
        self.deposited_token1 += amount1
        self.shares += minted_shares


@dataclass(frozen=True)
class Snapshot:
    step: int
    timestamp: int
    event_type: str
    reserve0: Decimal
    reserve1: Decimal
    spot_price_token1_per_token0: Decimal
    invariant_k: Decimal
    total_lp_shares: Decimal
    external_price_token1_per_token0: Decimal | None = None


@dataclass(frozen=True)
class ILAnalysis:
    owner_id: str
    external_price_token1_per_token0: Decimal
    share_ratio: Decimal
    theoretical_pool_reserve0: Decimal
    theoretical_pool_reserve1: Decimal
    position_token0: Decimal
    position_token1: Decimal
    lp_value_in_token1: Decimal
    hodl_value_in_token1: Decimal
    impermanent_loss_pct: Decimal
    value_difference_in_token1: Decimal


@dataclass(frozen=True)
class EventExecutionRecord:
    step: int
    timestamp: int
    event_type: str
    actor: str
    payload: dict[str, Any]
    snapshot_after: Snapshot
    swap_result: SwapResult | None = None
    minted_position: LPPosition | None = None
    il_analysis: ILAnalysis | None = None


@dataclass
class SimulationResult:
    scenario_name: str
    snapshots: list[Snapshot] = field(default_factory=list)
    swap_results: list[SwapResult] = field(default_factory=list)
    event_records: list[EventExecutionRecord] = field(default_factory=list)
    lp_positions: dict[str, LPPosition] = field(default_factory=dict)
    il_analysis: ILAnalysis | None = None
    plot_paths: list[str] = field(default_factory=list)
    export_paths: dict[str, str] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
