#!/bin/bash

# CHS-Books 开发环境停止脚本

set -e

echo "============================================================"
echo "🛑 停止CHS-Books开发环境"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 读取保存的PID
if [ -f ".pids/backend.pid" ]; then
    BACKEND_PID=$(cat .pids/backend.pid)
    echo -e "${BLUE}🔍 尝试停止后端服务器 (PID: $BACKEND_PID)...${NC}"

    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null || true
        sleep 1

        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${YELLOW}⚠️  进程未响应，强制终止...${NC}"
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi

        echo -e "${GREEN}✅ 后端服务器已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  后端服务器进程不存在${NC}"
    fi

    rm -f .pids/backend.pid
else
    echo -e "${YELLOW}⚠️  未找到后端PID文件${NC}"
fi

echo ""

if [ -f ".pids/frontend.pid" ]; then
    FRONTEND_PID=$(cat .pids/frontend.pid)
    echo -e "${BLUE}🔍 尝试停止前端服务器 (PID: $FRONTEND_PID)...${NC}"

    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 1

        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${YELLOW}⚠️  进程未响应，强制终止...${NC}"
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi

        echo -e "${GREEN}✅ 前端服务器已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务器进程不存在${NC}"
    fi

    rm -f .pids/frontend.pid
else
    echo -e "${YELLOW}⚠️  未找到前端PID文件${NC}"
fi

echo ""

# 额外清理：强制终止端口占用
echo -e "${BLUE}🧹 清理端口占用...${NC}"

if lsof -ti:8000 >/dev/null 2>&1; then
    echo -e "${YELLOW}🔄 清理端口 8000...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -ti:3000 >/dev/null 2>&1; then
    echo -e "${YELLOW}🔄 清理端口 3000...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

echo -e "${GREEN}✅ 端口清理完成${NC}"
echo ""

# 清理PID目录
rmdir .pids 2>/dev/null || true

echo "============================================================"
echo -e "${GREEN}🎉 所有服务已停止${NC}"
echo "============================================================"
echo ""
