# 最终检查清单

本清单用于项目提交前的最后检查，目标是确认当前仓库已经处于一个可运行、可测试、可展示、可交付的状态。

## 1. 项目结构检查

确认以下关键文件存在：

- `README.md`
- `PROJECT_STATUS.md`
- `FINAL_CHECKLIST.md`
- `TESTING.md`
- `Makefile`
- `requirements.txt`
- `main.py`
- `run_all_demos.py`
- `data/demo.yaml`
- `data/demo_large_trade_shock.yaml`
- `data/demo_il_stress.yaml`
- `data/README.md`

## 2. 依赖安装检查

```bash
pip install -r requirements.txt
```

确认依赖安装成功，至少包括：

- `PyYAML`
- `matplotlib`
- `pytest`

## 3. 基线 demo 运行检查

```bash
make demo
```

确认：

- 命令能成功运行
- 终端输出场景摘要
- `outputs/demo_run/` 下生成图表和 JSON 文件

## 4. 批量 demo 检查

```bash
make demos
```

确认：

- 3 个内置场景都能运行成功
- 终端输出场景对比表
- `outputs/demo_comparison.json` 成功生成

## 5. 测试通过检查

```bash
make test
```

确认：

- `pytest` 全部通过
- `TESTING.md` 中描述的测试范围与当前实现一致

## 5.1 Web 运行入口检查

```bash
make -n web-backend web-frontend
```

确认：

- `make web-backend` 指向当前 FastAPI 启动命令
- `make web-frontend` 指向当前 Next.js 启动命令

## 6. 输出文件检查

单场景输出至少应包含：

- `spot_price_series.png`
- `summary.json`
- `snapshots.json`
- `event_records.json`

存在 IL 分析时还应包含：

- `lp_vs_hodl.png`

批量运行后还应包含：

- `outputs/demo_comparison.json`

## 7. 文档检查

确认以下文档齐全且内容一致：

- `README.md`
- `PROJECT_STATUS.md`
- `FINAL_CHECKLIST.md`
- `TESTING.md`
- `data/README.md`

需要确认：

- 运行命令与当前项目真实实现一致
- 批量运行脚本名称一致
- 当前限制写清楚
- 未把后续规划误写成“已实现功能”

## 8. 当前限制是否写清楚

确认文档已明确说明：

- 当前只支持单池
- 当前只支持顺序事件执行
- 不支持多池路由
- 不支持集中流动性
- 不支持代理策略系统
- 不支持前端与数据库

## 9. 提交前建议清理项

如需清理运行产物，可执行：

```bash
make clean
```

并确认 `.gitignore` 已忽略以下内容：

- `outputs/`
- `.pytest_cache/`
- `__pycache__/`
- `.DS_Store`

## 10. 提交前最终确认

提交前建议最后核对一次：

- 当前目录是否为项目根目录
- `make demo` 是否可运行
- `make demos` 是否可运行
- `make test` 是否通过
- Git 状态是否符合预期
- 提交信息是否清晰表达这是最终交付版本
