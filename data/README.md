# Demo 场景说明

当前 `data/` 目录下提供三个最小可运行场景，全部通过同一套 AMM 核心逻辑执行，不引入任何额外协议机制。

## 1. `demo.yaml`

基线场景。

主要展示：

- 一次普通 `swap`
- 一次按比例 `add_liquidity`
- 一次 `external_price_update`
- 完整的摘要、图表和 JSON 导出

适合第一次运行项目时使用。

```bash
python main.py --config data/demo.yaml
```

## 2. `demo_large_trade_shock.yaml`

大额交易冲击场景。

主要展示：

- 大额交易对池内价格的冲击
- 成交均价相对交易前价格的明显恶化
- 更严重的滑点

这个场景只使用一笔大额 `swap`，目的是把“交易冲击”本身单独看清楚。

```bash
python main.py --config data/demo_large_trade_shock.yaml
```

## 3. `demo_il_stress.yaml`

无常损失更明显的场景。

主要展示：

- 按比例加池后，LP 头寸占比变化
- 外部价格大幅变化时，LP 价值与 HODL 价值的差异
- 更明显的 IL 结果

```bash
python main.py --config data/demo_il_stress.yaml
```

## 一键运行全部场景

如果希望一次性运行全部内置场景，并输出对比结果，可以直接执行：

```bash
python run_all_demos.py
```

脚本会自动：

- 运行 3 个 demo
- 生成各自的输出目录
- 读取每个场景的 `summary.json`
- 输出一个简洁的终端对比表
- 生成 `outputs/demo_comparison.json`
