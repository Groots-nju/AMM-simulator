# DeFi AMM 交易所仿真系统

基于 Flask + React 的本地化去中心化交易所（DEX）仿真平台，模拟恒定产品自动做市商（Constant Product AMM）的核心机制，支持代币交易（Swap）、流动性提供与赎回、不可永久损失（IL）计算等功能。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.x, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, bcrypt |
| 前端 | React 18, Ant Design 5, Axios, Recharts, React Router 7 |
| 数据库 | SQLite（开发/测试） |
| 代理 | http-proxy-middleware（解决跨域） |

---

## 项目结构

```
├── jrrg_framework_backend/     # Flask 后端
│   ├── app/
│   │   ├── config/             # 配置文件
│   │   ├── controllers/        # 控制器（路由）
│   │   ├── exchange/           # AMM 核心引擎 + 业务服务
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   └── utils/              # 工具函数（加密、统一响应）
│   ├── requirements.txt        # Python 依赖
│   └── run.py                  # 后端启动入口
│
└── jrrg_framework_frontend/    # React 前端
    ├── src/
    │   ├── api/                # API 接口封装
    │   ├── views/              # 页面组件
    │   ├── utils/http.js       # Axios 封装（含 JWT 拦截器）
    │   └── setupProxy.js       # 开发代理配置
    └── package.json            # Node 依赖
```

---

## 快速启动

### 1. 克隆/准备项目

确保项目目录结构如上所示，进入项目根目录。

### 2. 启动后端

```bash
cd jrrg_framework_backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# 或 venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端服务（默认端口 8080）
python run.py
```

后端启动后会自动：
- 创建 SQLite 数据库（`exchange_simulator.db`）
- 初始化默认代币和交易池数据
- 创建默认用户 `admin` / `123456`

### 3. 启动前端

```bash
cd jrrg_framework_frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 3000）
npm start
```

前端启动后会自动打开浏览器访问 `http://localhost:3000`。

> 前端通过 `setupProxy.js` 将 `/api/*` 请求代理到 `http://localhost:8080/`，无需额外配置跨域。

---

## 默认账户

| 用户名 | 密码 | 说明 |
|--------|------|------|
| admin | 123456 | 预置测试账户，登录后自动发放模拟资产 |

---

## 核心功能

- **代币交易（Swap）**：基于恒定产品公式 `x × y = k` 自动定价，支持滑点保护
- **流动性管理**：添加/移除流动性，实时计算 LP 份额和池子占比
- **不可永久损失（IL）计算**：实时对比 LP 持仓价值与 HODL 价值
- **资产领取（Faucet）**：免费领取模拟代币用于测试
- **仿真重置**：一键恢复初始状态，便于反复实验
- **事件审计**：完整记录所有交易、流动性操作历史

---

## 预设交易池

| 交易池 | Token0 储备 | Token1 储备 | 现货价格 | 手续费率 |
|--------|------------|------------|---------|---------|
| ETH/USDC | 500 ETH | 1,000,000 USDC | 2,000 USDC/ETH | 0.3% |
| BTC/USDC | 80 BTC | 5,200,000 USDC | 65,000 USDC/BTC | 0.3% |
| MANBO/USDC | 1,000,000 MANBO | 250,000 USDC | 0.25 USDC/MANBO | 0.3% |

---

## 后端 API 概览

所有交易接口均需 JWT 认证（`Authorization: Bearer <token>`）。

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/user/login` | 用户登录 |
| POST | `/user/register` | 用户注册 |
| GET | `/exchange/tokens` | 获取代币列表 |
| GET | `/exchange/pools` | 获取交易池列表 |
| GET | `/exchange/wallet` | 获取钱包余额 |
| POST | `/exchange/faucet` | 领取模拟资产 |
| POST | `/exchange/swap/quote` | 获取 Swap 报价 |
| POST | `/exchange/swap` | 执行 Swap 交易 |
| POST | `/exchange/liquidity/add` | 添加流动性 |
| POST | `/exchange/liquidity/remove` | 移除流动性 |
| GET | `/exchange/positions` | 获取 LP 持仓 |
| GET | `/exchange/history` | 获取交易历史 |
| POST | `/exchange/simulation/reset` | 重置仿真环境 |

---

## 环境配置

后端配置位于 `jrrg_framework_backend/app/config/base_config.py`：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///exchange_simulator.db` | 数据库连接 |
| `JWT_SECRET_KEY` | `local_exchange_simulator_secret` | JWT 密钥 |
| `DEBUG` | `False` | 调试模式 |

可通过在项目根目录创建 `app.env` 文件覆盖配置：

```env
DEBUG=True
JWT_SECRET_KEY=your_secret_key_here
```

---

## 开发注意事项

1. **端口占用**：后端默认使用 `8080`，前端默认使用 `3000`，请确保端口未被占用。
2. **跨域问题**：开发环境下由 `setupProxy.js` 自动处理，生产环境需配置 Nginx 等反向代理。
3. **数据库**：默认使用 SQLite，如需切换至 MySQL/PostgreSQL，修改 `SQLALCHEMY_DATABASE_URI` 即可。
4. **精度问题**：所有金融计算使用 Python `Decimal` 类型，避免浮点数精度损失。

---

## 许可证

本项目仅供学习和研究使用。
