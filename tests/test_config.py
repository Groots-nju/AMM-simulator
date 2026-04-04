from decimal import Decimal
from pathlib import Path
import sys

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import load_config
from src.exceptions import ConfigError


def test_load_config_rejects_missing_root_keys(tmp_path: Path) -> None:
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("{}", encoding="utf-8")

    with pytest.raises(ConfigError, match="Missing keys in root"):
        load_config(config_path)


def test_load_config_rejects_missing_event_fields(tmp_path: Path) -> None:
    raw_config = {
        "project": {"name": "bad config"},
        "tokens": {
            "token0": {"symbol": "ETH"},
            "token1": {"symbol": "USDC"},
        },
        "pool": {
            "initial_reserve0": "100",
            "initial_reserve1": "200000",
            "fee_rate": "0.003",
            "initial_lp_owner": "alice",
        },
        "events": [
            {
                "timestamp": 1,
                "type": "swap",
                "actor": "trader",
                "token_in": "ETH",
            }
        ],
        "output": {"directory": "outputs"},
    }
    config_path = tmp_path / "bad_event.yaml"
    config_path.write_text(yaml.safe_dump(raw_config, sort_keys=False), encoding="utf-8")

    with pytest.raises(ConfigError, match="Missing keys in swap: amount_in"):
        load_config(config_path)


def test_load_config_converts_numeric_values_to_decimal_without_float_leakage(tmp_path: Path) -> None:
    raw_config = {
        "project": {"name": "numeric config"},
        "tokens": {
            "token0": {"symbol": "ETH"},
            "token1": {"symbol": "USDC"},
        },
        "pool": {
            "initial_reserve0": 100.5,
            "initial_reserve1": 200000.25,
            "fee_rate": 0.003,
            "initial_lp_owner": "alice",
        },
        "events": [
            {
                "timestamp": 1,
                "type": "swap",
                "actor": "trader",
                "token_in": "ETH",
                "amount_in": 0.1,
            }
        ],
        "output": {"directory": "outputs"},
        "visualization": {"enabled": False},
    }
    config_path = tmp_path / "numeric.yaml"
    config_path.write_text(yaml.safe_dump(raw_config, sort_keys=False), encoding="utf-8")

    config = load_config(config_path)

    assert isinstance(config["pool"]["initial_reserve0"], Decimal)
    assert isinstance(config["pool"]["fee_rate"], Decimal)
    assert isinstance(config["events"][0].payload["amount_in"], Decimal)
    assert config["pool"]["initial_reserve0"] == Decimal("100.5")
    assert config["pool"]["fee_rate"] == Decimal("0.003")
    assert config["events"][0].payload["amount_in"] == Decimal("0.1")
