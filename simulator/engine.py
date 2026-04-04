"""Minimal deterministic engine for sequential event execution."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from src.analytics import analyze_impermanent_loss
from src.models import Event, EventExecutionRecord, LPPosition, SimulationResult
from src.pool import Pool


@dataclass
class SimulationEngine:
    pool: Pool
    scenario_name: str
    initial_lp_owner: str
    initial_reserve0: Decimal
    initial_reserve1: Decimal

    def run(self, events: list[Event]) -> SimulationResult:
        lp_positions: dict[str, LPPosition] = {}
        initial_lp = self.pool.initialize_pool(
            owner_id=self.initial_lp_owner,
            amount0=self.initial_reserve0,
            amount1=self.initial_reserve1,
        )
        lp_positions[initial_lp.owner_id] = initial_lp

        result = SimulationResult(scenario_name=self.scenario_name)
        result.lp_positions = lp_positions
        result.snapshots.append(self.pool.snapshot(step=0, timestamp=0, event_type="initialize"))

        current_external_price: Decimal | None = None

        for step, event in enumerate(events, start=1):
            event_record, current_external_price = self._execute_event(
                step=step,
                event=event,
                lp_positions=lp_positions,
                current_external_price=current_external_price,
                result=result,
            )
            result.event_records.append(event_record)
            result.snapshots.append(event_record.snapshot_after)

        result.lp_positions = lp_positions
        return result

    def _execute_event(
        self,
        *,
        step: int,
        event: Event,
        lp_positions: dict[str, LPPosition],
        current_external_price: Decimal | None,
        result: SimulationResult,
    ) -> tuple[EventExecutionRecord, Decimal | None]:
        swap_result = None
        minted_position = None
        il_analysis = None

        if event.event_type == "swap":
            swap_result = self.pool.swap_exact_in(
                actor=event.actor,
                token_in_symbol=event.payload["token_in"],
                amount_in=event.payload["amount_in"],
            )
            result.swap_results.append(swap_result)
        elif event.event_type == "add_liquidity":
            minted_position = self.pool.add_liquidity(
                owner_id=event.actor,
                amount0=event.payload["amount0"],
                amount1=event.payload["amount1"],
            )
            if event.actor in lp_positions:
                lp_positions[event.actor].add_deposit(
                    event.payload["amount0"],
                    event.payload["amount1"],
                    minted_position.shares,
                )
            else:
                lp_positions[event.actor] = minted_position
        elif event.event_type == "external_price_update":
            current_external_price = event.payload["price_token1_per_token0"]
            target_lp = lp_positions[event.payload["target_lp_owner"]]
            il_analysis = analyze_impermanent_loss(
                pool=self.pool,
                position=target_lp,
                external_price_token1_per_token0=current_external_price,
            )
            result.il_analysis = il_analysis
        else:
            raise ValueError(f"Unsupported event type: {event.event_type}")

        snapshot_after = self.pool.snapshot(
            step=step,
            timestamp=event.timestamp,
            event_type=event.event_type,
            external_price_token1_per_token0=current_external_price,
        )
        event_record = EventExecutionRecord(
            step=step,
            timestamp=event.timestamp,
            event_type=event.event_type,
            actor=event.actor,
            payload=event.payload,
            snapshot_after=snapshot_after,
            swap_result=swap_result,
            minted_position=minted_position,
            il_analysis=il_analysis,
        )
        return event_record, current_external_price
