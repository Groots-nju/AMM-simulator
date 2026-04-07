# 项目验收说明

## 当前项目状态

当前项目已经完成了一个面向教学、展示和基础实验的单池 AMM 仿真 MVP。

它已经具备：

- 本地实现的恒定乘积 AMM 核心逻辑
- 可执行的事件驱动仿真流程
- 可复现的多场景 demo 配置
- 本地 FastAPI + Next.js Web MVP
- 图表输出
- JSON 结果导出
- 自动化测试
- 批量运行全部 demo 的交付脚本

如果目标是“完成一个结构清晰、可运行、可测试、可讲解的 AMM 单池仿真项目”，当前版本已经可以视为基本完成。

## 已完成能力列表

- 单池 AMM
- 恒定乘积公式 `x * y = k`
- `swap exact in`
- 手续费处理
- 滑点计算
- 初始建池
- 按比例加池
- 外部价格更新下的 IL 分析
- 顺序事件执行引擎
- 终端摘要输出
- 图表输出
- JSON 导出
- 多场景 demo
- 批量运行全部 demo
- FastAPI 后端接口
- Next.js 本地前端页面
- `pytest` 回归测试

## 快速验收步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 跑基线 demo

```bash
make demo
```

预期看到：

- 终端打印场景摘要
- `outputs/demo_run/` 下生成图表和 JSON 文件

### 3. 跑全部 demo

```bash
make demos
```

预期看到：

- 3 个场景依次运行完成
- 终端输出场景对比表
- `outputs/demo_comparison.json` 生成成功

### 4. 跑测试

```bash
make test
```

预期看到：

- `pytest` 全部通过

### 5. 跑本地 Web MVP

```bash
make web-backend
make web-frontend
```

预期看到：

- 后端运行在 `http://localhost:8000`
- 前端运行在 `http://localhost:3000`
- 页面可加载场景列表，并能运行内置 demo

## 推荐演示顺序

如果向老师、同学或面试官演示，建议按下面顺序：

### 1. 基线场景

```bash
make demo
```

说明：

- 展示 AMM 的完整最小闭环
- 包含 swap、加池、IL 分析、图表和导出

### 2. 大额交易冲击场景

```bash
python main.py --config data/demo_large_trade_shock.yaml
```

说明：

- 强调大额订单如何冲击价格
- 强调滑点恶化

### 3. IL 压力场景

```bash
python main.py --config data/demo_il_stress.yaml
```

说明：

- 强调价格大幅变化后 LP 与 HODL 的差异
- 展示更明显的无常损失

### 4. 全部场景对比

```bash
make demos
```

说明：

- 展示项目不仅能跑单个案例，也能做批量交付和结果对比

## 预期输出文件

### 单场景运行

每个场景的输出目录通常会包含：

- `spot_price_series.png`
- `lp_vs_hodl.png`（仅在存在 IL 分析时生成）
- `summary.json`
- `snapshots.json`
- `event_records.json`

### 批量运行

批量运行全部 demo 后，还会额外生成：

- `outputs/demo_comparison.json`

## 当前限制

当前版本的边界非常明确：

- 仅支持单池
- 仅支持顺序事件执行
- 不支持多池路由
- 不支持集中流动性
- 不支持真实链上交互
- 不支持代理策略系统
- 不支持数据库
- 不支持生产级部署与鉴权体系
- 不以生产部署为目标

## 哪些属于后续扩展，而非当前已实现

下面这些都属于后续扩展方向，不应和当前能力混淆：

- 多用户代理
- 套利者策略
- 更复杂的事件调度器
- 多池扩展
- 更完整的收益归因
- 前端交互界面
- 数据库持久化
- 参数扫描和系统化实验框架

## 常用命令

```bash
make demo
make demos
make test
make web-backend
make web-frontend
make clean
```
