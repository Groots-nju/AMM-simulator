from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from simulator.engine import SimulationEngine
from src.config import load_config
from src.pool import Pool
from src.visualization import save_visualizations


def test_save_visualizations_generates_expected_plot_files(tmp_path: Path) -> None:
    project_dir = Path(__file__).resolve().parents[1]
    config = load_config(project_dir / "data" / "demo.yaml")
    pool_cfg = config["pool"]
    pool = Pool(
        token0=config["tokens"]["token0"],
        token1=config["tokens"]["token1"],
        fee_rate=pool_cfg["fee_rate"],
    )
    engine = SimulationEngine(
        pool=pool,
        scenario_name=config["project_name"],
        initial_lp_owner=pool_cfg["initial_lp_owner"],
        initial_reserve0=pool_cfg["initial_reserve0"],
        initial_reserve1=pool_cfg["initial_reserve1"],
    )
    result = engine.run(config["events"])

    plot_paths = save_visualizations(result, tmp_path)

    assert len(plot_paths) == 2
    assert plot_paths[0].endswith("spot_price_series.png")
    assert plot_paths[1].endswith("lp_vs_hodl.png")
    for plot_path in plot_paths:
        assert Path(plot_path).exists()
