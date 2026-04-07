# 测试说明

本项目当前采用“核心逻辑自动化测试 + Web 轻量 smoke 验证”的策略。

目标不是把当前教学型项目堆成重型测试平台，而是在保持轻量的前提下，确保：

- Python AMM 核心逻辑稳定
- CLI 和导出链路稳定
- FastAPI 接口可用
- Next.js 前端在 localhost 下可正常联调

## 1. 已自动化覆盖的部分

当前 `pytest` 已覆盖：

- 配置读取与校验
- 恒定乘积交易逻辑
- 手续费与滑点
- 流动性添加约束
- 无常损失分析
- `Decimal` 精度稳定性
- CLI demo 运行
- 多 demo 场景运行
- 导出文件生成
- 图表文件生成
- FastAPI 基础接口
  - `/health`
  - `/scenarios`
  - `/simulate`
- 交付层文件检查
  - `Makefile`
  - `README.md`
  - `PROJECT_STATUS.md`
  - `FINAL_CHECKLIST.md`

运行方式：

```bash
pytest -q
```

## 2. Web 当前的轻量验证方式

当前没有引入 Playwright、Cypress、Selenium 等重型浏览器自动化框架。

Web 层目前采用以下轻量验证：

- `npm run build`
  - 验证 Next.js 页面能正常编译
- 启动本地服务后做 localhost smoke 检查
  - `make web-backend`
  - `make web-frontend`
- 请求以下地址确认服务可用
  - `http://localhost:8000/health`
  - `http://localhost:3000`
- 手工验证页面交互闭环
  - 场景列表可加载
  - 选择场景后可运行仿真
  - 页面可展示 summary、图表和简版 event records

## 3. 当前未自动化覆盖的部分

下面这些目前仍然主要依赖轻量 smoke 验证或人工检查：

- 浏览器点击交互的端到端自动化
- 图表图片的视觉回归对比
- 不同浏览器兼容性
- 长时间运行下的前后端进程管理
- 生产部署环境验证

这不是遗漏，而是当前阶段有意保持轻量。

## 4. 推荐的最终本地检查

提交或演示前，建议至少执行：

```bash
pytest -q
make demo
make demos
make -n web-backend web-frontend
```

如需实际联调，再分别启动：

```bash
make web-backend
make web-frontend
```

然后打开：

```text
http://localhost:3000
```
