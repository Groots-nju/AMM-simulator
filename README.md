# AMM 交易所仿真

一个面向教学、课程展示和面试讲解的最小可运行 AMM 交易所仿真项目。  
项目聚焦单池恒定乘积 AMM，以本地实现的协议逻辑为核心，当前已经支持建池、交易、手续费、滑点、按比例加池、无常损失分析、图表输出和结构化结果导出。

## 项目简介

这个项目的目标不是“解释一下公式”，而是做一个可以真实跑起来的 AMM 仿真最小系统。  
当前版本以单池模型为中心，围绕下面几个问题展开：

- AMM 的价格是如何由池内储备决定的
- 一笔交易如何改变池子状态
- 手续费如何积累到池中
- 大额交易为什么会带来更明显的滑点
- LP 提供流动性后，为什么会出现无常损失
- 如何把一次仿真的过程和结果保存下来，便于分析和展示

## 为什么这不是“伪仿真”

这个项目不是静态公式展示，也不是只会算一次结果的计算器，原因有三点：

1. 协议核心逻辑在本地实现  
   恒定乘积交易、手续费、LP 份额、无常损失分析都由本地 Python 代码完成，不依赖链上 API 作为核心计算来源。

2. 仿真是可执行、可交互、可复现的  
   通过 `data/demo.yaml` 配置事件序列，执行层会按顺序推进事件，并输出状态快照、事件明细、图表和 JSON 结果。

3. 结果不是只有终端文本  
   当前版本会自动生成：
   - 图表文件
   - `summary.json`
   - `snapshots.json`
   - `event_records.json`

这使得项目既能演示，也能复查、复用和继续分析。

## 当前实现的功能列表

- 单池 AMM，采用恒定乘积公式 `x * y = k`
- 初始建池
- `swap exact in` 交易
- 手续费处理
- 滑点计算
- 按当前池比例 `add_liquidity`
- 外部价格更新下的 LP / HODL 对比
- 无常损失（Impermanent Loss）分析
- 顺序事件执行引擎
- CLI 运行入口
- 图表输出
- JSON 结果导出
- `pytest` 核心测试

## 项目结构说明

```text
AMM 交易所仿真/
├── .gitignore
├── FINAL_CHECKLIST.md
├── Makefile
├── PROJECT_STATUS.md
├── run_all_demos.py
├── main.py
├── README.md
├── requirements.txt
├── data/
│   ├── README.md
│   ├── demo.yaml
│   ├── demo_large_trade_shock.yaml
│   └── demo_il_stress.yaml
├── simulator/
│   ├── __init__.py
│   └── engine.py
├── src/
│   ├── __init__.py
│   ├── analytics.py
│   ├── config.py
│   ├── decimal_utils.py
│   ├── exceptions.py
│   ├── exporters.py
│   ├── models.py
│   ├── pool.py
│   ├── reporting.py
│   └── visualization.py
└── tests/
    ├── test_cli_demo.py
    ├── test_config.py
    ├── test_engine.py
    ├── test_exports.py
    ├── test_lp_and_il.py
    ├── test_pool.py
    ├── test_precision.py
    └── test_visualization.py
```

### 各目录职责

#### `src/`

核心业务层。

- `pool.py`：AMM 池子逻辑，负责建池、交易、加池、储备更新
- `analytics.py`：滑点、LP / HODL 对比、无常损失分析
- `models.py`：结果对象、快照、事件记录等数据结构
- `reporting.py`：基于仿真结果生成 summary
- `exporters.py`：把结果导出为 JSON
- `visualization.py`：基于结果对象生成图表
- `config.py`：读取和校验配置文件

#### `simulator/`

最小执行层。

- `engine.py`：按配置顺序执行事件，并生成 `SimulationResult`

#### `tests/`

测试层，覆盖核心公式、边界场景、精度稳定性、导出和 CLI 集成。

#### `data/`

示例输入配置。

- `demo.yaml`：当前最小可运行 demo
- `demo_large_trade_shock.yaml`：大额交易冲击场景
- `demo_il_stress.yaml`：更明显的 IL 场景

## 示例场景

当前项目除了基线 demo 外，还提供两个更有代表性的场景，用来展示同一套系统在不同输入下的行为差异。

### 1. 基线场景

```bash
python main.py --config data/demo.yaml
```

主要展示：

- 普通 `swap`
- 按比例加池
- 一次价格更新下的 IL 分析

### 2. 大额交易冲击场景

```bash
python main.py --config data/demo_large_trade_shock.yaml
```

主要展示：

- 大额订单导致的价格冲击
- 更明显的滑点恶化
- 池内价格快速偏移

### 3. IL 压力场景

```bash
python main.py --config data/demo_il_stress.yaml
```

主要展示：

- 外部价格大幅变化后 LP 与 HODL 的差异
- 更明显的无常损失

## 快速启动

### 环境要求

- Python 3.11+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 常用命令

```bash
make demo
make demos
make test
```

### 运行 demo

```bash
python main.py --config data/demo.yaml
```

也可以运行其他场景：

```bash
python main.py --config data/demo_large_trade_shock.yaml
python main.py --config data/demo_il_stress.yaml
```

### 一键运行全部 demo

```bash
python run_all_demos.py
```

这个脚本会：

- 顺序运行 3 个内置 demo 场景
- 生成每个场景各自的图表和 JSON 输出
- 读取每个场景的 `summary.json`
- 在终端打印一个简洁的场景对比表
- 额外生成 `outputs/demo_comparison.json`

更完整的验收和演示顺序见 [PROJECT_STATUS.md](PROJECT_STATUS.md)。
提交前最终检查见 [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md)。

## 测试命令

```bash
pytest
```

当前版本包含覆盖核心路径的自动化测试，用于验证：

- 恒定乘积交易逻辑
- 手续费与滑点
- 非法输入与边界情况
- `Decimal` 精度稳定性
- LP 与 IL 分析
- CLI demo 能否跑通
- 图表和 JSON 文件是否生成

## 输出结果说明

运行 demo 后，程序会在终端打印仿真摘要，并在输出目录中生成图表和 JSON 文件。

默认输出目录由 `data/demo.yaml` 指定，当前为：

```text
outputs/demo_run/
```

### 图表文件

- `spot_price_series.png`
  - 展示池内隐含价格如何随仿真步骤变化
- `lp_vs_hodl.png`
  - 展示最近一次外部价格分析下，LP 价值与 HODL 价值的对比

### JSON 导出文件

- `summary.json`
  - 仿真摘要，例如事件计数、最终价格、最终储备、手续费、最新 IL
- `snapshots.json`
  - 每一步事件执行后的状态快照
- `event_records.json`
  - 每个事件的输入、执行结果和事件后快照

## 核心机制说明

### 1. 恒定乘积公式

当前 AMM 采用最经典的恒定乘积形式：

```text
x * y = k
```

其中：

- `x`：池中 `token0` 储备
- `y`：池中 `token1` 储备
- `k`：交易前后近似保持约束关系的乘积

交易发生后，池子会沿着这条曲线移动。

### 2. 手续费

当前版本支持固定费率，例如 demo 中的 `0.3%`。

处理方式：

- 用户输入 `amount_in`
- 先扣除手续费，得到 `effective_amount_in`
- 用有效输入量参与定价
- 手续费会累积在池中，并体现在结果 summary 中

### 3. 滑点

滑点反映“本次实际成交均价”和“交易前池内价格”之间的偏差。

当前实现会记录：

- 交易前价格
- 交易后价格
- 成交均价
- 滑点方向和大小

这能直接观察大额交易对成交质量的影响。

### 4. LP 份额

LP 份额表示流动性提供者拥有池子的比例。

当前版本支持：

- 初始建池
- 按当前池比例加池

当前 MVP 不支持：

- 单边加池
- 自动配比
- 集中流动性

### 5. 无常损失

当前版本通过一次 `external_price_update` 事件，分析：

- 如果某个 LP 继续留在池中，其头寸价值是多少
- 如果同样的初始资产不做 LP、只是持有，价值是多少
- 两者的差额和百分比，即当前的无常损失结果

## 当前系统设计说明

### `src/`

这里是唯一的核心公式来源。

- 所有 AMM 数学逻辑都集中在 `pool.py`
- 所有指标分析都集中在 `analytics.py`
- summary、export、visualization 都只读取结果对象，不重新定义协议逻辑

### `simulator/`

当前是极简执行层。

- 只做确定性的顺序事件执行
- 支持的事件类型只有：
  - `swap`
  - `add_liquidity`
  - `external_price_update`

### `tests/`

围绕“锁稳当前 MVP”来设计。

- 不是堆形式化测试
- 而是优先覆盖最容易出错的数学逻辑和边界情况

### `data/`

通过 `demo.yaml` 描述一次完整仿真。

这让项目具备：

- 可配置
- 可重复运行
- 可共享

## 示例运行结果说明

当前 demo 的典型运行输出包含以下信息：

- 场景名称
- 池子最终储备
- 最终 spot price
- 每笔 swap 的输入、输出、手续费、滑点
- 最近一次 IL 分析结果
- 图表保存路径
- JSON 导出路径

这使得一次仿真既能“看过程”，也能“拿结果做后续分析”。

## 风险与限制

当前版本是教学型最小系统，不是生产级 DeFi 基础设施，主要限制包括：

- 仅支持单池
- 仅支持顺序事件执行，不支持复杂调度
- 不支持多池路由
- 不支持集中流动性
- 不支持真实链上交互
- 不支持套利代理、普通交易者代理等行为策略
- 只支持最小范围的 LP 分析，不做完整收益归因
- 图表和导出能力以 MVP 为主，尚未形成完整实验框架

## 后续规划

在保持当前工程结构清晰的前提下，后续可以继续扩展：

- 更丰富的事件类型
- 更细的收益统计
- 更多图表和实验对比
- 多用户代理
- 更完整的仿真调度器
- 多池扩展
- Web 前端展示

但这些都应建立在“当前单池 MVP 正确、稳定、可测试”的基础上逐步推进，而不是一次性堆复杂度。

## 参考说明

本项目参考了 Uniswap V2 类 AMM 的公开机制思想，包括：

- 恒定乘积定价
- 交易手续费进入池子
- LP 份额表示池子占比
- LP 与 HODL 的对比分析思路

需要强调的是：

- 本项目代码实现为自主组织的教学型最小版本
- 没有复制任何协议的生产代码
- 当前目标是帮助理解 AMM 核心机制与仿真工程化方法，而不是复刻完整 DeFi 协议
