#!/bin/bash
# ============================================================
# DeFi AMM 交易所仿真系统 - 一键启动脚本
# ============================================================
# 使用方式:
#   chmod +x start_demo.sh && ./start_demo.sh
# ============================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/jrrg_framework_backend"
FRONTEND_DIR="$PROJECT_DIR/jrrg_framework_frontend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  DeFi AMM 交易所仿真系统 - 一键启动${NC}"
echo -e "${GREEN}============================================================${NC}"

# ---------- 1. 后端启动 ----------
echo -e "\n${YELLOW}[1/2] 启动后端服务...${NC}"

cd "$BACKEND_DIR"

# 检查 requirements.txt 中的依赖是否已安装
if ! python3 -c "import flask, yaml" 2>/dev/null; then
    echo -e "${YELLOW}  安装后端依赖...${NC}"
    pip install -r requirements.txt --break-system-packages -q
fi

# 以后台方式启动后端
python3 main.py --config demo.yaml &
BACKEND_PID=$!
echo -e "${GREEN}  后端已启动 (PID: $BACKEND_PID)${NC}"

# 等待后端就绪
echo -n "  等待后端就绪"
for i in $(seq 1 30); do
    if curl -s http://localhost:8080/user/login > /dev/null 2>&1; then
        echo -e "\n${GREEN}  后端就绪 ✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# ---------- 2. 前端启动 ----------
echo -e "\n${YELLOW}[2/2] 启动前端服务...${NC}"

cd "$FRONTEND_DIR"

# 检查 node_modules 是否已安装
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}  安装前端依赖（npm install）...${NC}"
    npm install --silent
fi

# 启动前端
echo -e "${GREEN}  启动前端开发服务器...${NC}"
npm start &
FRONTEND_PID=$!

echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}  系统已启动！${NC}"
echo -e "${GREEN}------------------------------------------------------------${NC}"
echo -e "  前端地址:  ${YELLOW}http://localhost:3000${NC}"
echo -e "  后端地址:  ${YELLOW}http://localhost:8080${NC}"
echo -e "  默认账号:  ${YELLOW}admin / 123456${NC}"
echo -e "${GREEN}------------------------------------------------------------${NC}"
echo -e "  停止方式:  ${YELLOW}按 Ctrl+C 停止，或执行: kill $BACKEND_PID $FRONTEND_PID${NC}"
echo -e "${GREEN}============================================================${NC}"

# 等待任意子进程结束
wait