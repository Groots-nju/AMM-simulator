from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics import analyze_impermanent_loss
from src.models import LPPosition, Token
from src.pool import Pool


def build_pool() -> tuple[Pool, LPPosition]:
    pool = Pool(
        token0=Token(symbol="ETH", name="Ether"),
        token1=Token(symbol="USDC", name="USD Coin"),
        fee_rate=Decimal("0.003"),
    )
    position = pool.initialize_pool("alice", Decimal("100"), Decimal("200000"))
    return pool, position


def test_add_liquidity_mints_expected_lp_shares() -> None:
    pool, _ = build_pool()
    initial_shares = pool.total_lp_shares
    minted = pool.add_liquidity("bob", Decimal("20"), Decimal("40000"))

    assert minted.shares == Decimal("20") * initial_shares / Decimal("100")
    assert pool.total_lp_shares == initial_shares + minted.shares
    assert pool.reserve0 == Decimal("120")
    assert pool.reserve1 == Decimal("240000")


def test_il_analysis_matches_constant_product_expectation() -> None:
    pool, position = build_pool()
    analysis = analyze_impermanent_loss(pool, position, Decimal("2500"))

    assert analysis.external_price_token1_per_token0 == Decimal("2500")
    assert analysis.lp_value_in_token1 < analysis.hodl_value_in_token1
    assert analysis.impermanent_loss_pct < Decimal("0")
    assert analysis.position_token0 == analysis.theoretical_pool_reserve0
    assert analysis.position_token1 == analysis.theoretical_pool_reserve1


def test_il_is_zero_when_external_price_is_unchanged() -> None:
    pool, position = build_pool()
    analysis = analyze_impermanent_loss(pool, position, Decimal("2000"))

    tolerance = Decimal("1E-24")
    assert abs(analysis.lp_value_in_token1 - analysis.hodl_value_in_token1) <= tolerance
    assert abs(analysis.impermanent_loss_pct) <= tolerance
