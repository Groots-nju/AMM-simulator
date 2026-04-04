"""Configuration loading for the minimal AMM simulator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .decimal_utils import to_decimal
from .exceptions import ConfigError
from .models import Event, Token


def _require_keys(mapping: dict[str, Any], keys: list[str], *, section_name: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ConfigError(f"Missing keys in {section_name}: {', '.join(missing)}")


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file)

    if not isinstance(raw, dict):
        raise ConfigError("Config root must be a mapping.")

    _require_keys(raw, ["project", "tokens", "pool", "events", "output"], section_name="root")

    token0_cfg = raw["tokens"].get("token0", {})
    token1_cfg = raw["tokens"].get("token1", {})
    _require_keys(token0_cfg, ["symbol"], section_name="tokens.token0")
    _require_keys(token1_cfg, ["symbol"], section_name="tokens.token1")

    pool_cfg = raw["pool"]
    _require_keys(pool_cfg, ["initial_reserve0", "initial_reserve1", "fee_rate", "initial_lp_owner"], section_name="pool")

    project_name = raw["project"].get("name", "AMM Demo")

    tokens = {
        "token0": Token(
            symbol=str(token0_cfg["symbol"]),
            name=str(token0_cfg.get("name", token0_cfg["symbol"])),
            decimals=int(token0_cfg.get("decimals", 18)),
        ),
        "token1": Token(
            symbol=str(token1_cfg["symbol"]),
            name=str(token1_cfg.get("name", token1_cfg["symbol"])),
            decimals=int(token1_cfg.get("decimals", 18)),
        ),
    }

    pool = {
        "initial_reserve0": to_decimal(pool_cfg["initial_reserve0"], field_name="pool.initial_reserve0"),
        "initial_reserve1": to_decimal(pool_cfg["initial_reserve1"], field_name="pool.initial_reserve1"),
        "fee_rate": to_decimal(pool_cfg["fee_rate"], field_name="pool.fee_rate"),
        "initial_lp_owner": str(pool_cfg["initial_lp_owner"]),
    }

    events = [_parse_event(event_cfg) for event_cfg in raw["events"]]
    output_cfg = raw["output"]
    visualization_cfg = raw.get("visualization", {})

    return {
        "project_name": project_name,
        "tokens": tokens,
        "pool": pool,
        "events": events,
        "output": {
            "directory": str(output_cfg.get("directory", "outputs")),
            "save_plots": bool(output_cfg.get("save_plots", True)),
        },
        "visualization": {
            "enabled": bool(visualization_cfg.get("enabled", True)),
        },
    }


def _parse_event(raw_event: dict[str, Any]) -> Event:
    if not isinstance(raw_event, dict):
        raise ConfigError("Each event must be a mapping.")
    _require_keys(raw_event, ["timestamp", "type"], section_name="event")

    event_type = str(raw_event["type"])
    actor = str(raw_event.get("actor", "system"))
    timestamp = int(raw_event["timestamp"])
    payload: dict[str, Any] = {}

    if event_type == "add_liquidity":
        _require_keys(raw_event, ["amount0", "amount1"], section_name="add_liquidity")
        payload["amount0"] = to_decimal(raw_event["amount0"], field_name="event.amount0")
        payload["amount1"] = to_decimal(raw_event["amount1"], field_name="event.amount1")
    elif event_type == "swap":
        _require_keys(raw_event, ["token_in", "amount_in"], section_name="swap")
        payload["token_in"] = str(raw_event["token_in"])
        payload["amount_in"] = to_decimal(raw_event["amount_in"], field_name="event.amount_in")
    elif event_type == "external_price_update":
        _require_keys(raw_event, ["price_token1_per_token0", "target_lp_owner"], section_name="external_price_update")
        payload["price_token1_per_token0"] = to_decimal(
            raw_event["price_token1_per_token0"],
            field_name="event.price_token1_per_token0",
        )
        payload["target_lp_owner"] = str(raw_event["target_lp_owner"])
    else:
        raise ConfigError(f"Unsupported event type: {event_type}")

    return Event(timestamp=timestamp, event_type=event_type, actor=actor, payload=payload)
