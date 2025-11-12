#!/bin/bash

# CHS-Books 开发环境快速启动脚本
# Sprint 1 - Standalone Textbook Server

set -e  # 遇到错误立即退出

echo "============================================================"
echo "🚀 CHS-Books 开发环境启动脚本"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 杀死占用端口的进程
kill_port() {
    local port=$1
    echo -e "${YELLOW}🔄 端口 $port 已被占用，正在清理...${NC}"
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 1
}

# 检查必要的依赖
echo -e "${BLUE}📋 检查系统依赖...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 系统依赖检查完成${NC}"
echo ""

# 清理端口
echo -e "${BLUE}🔍 检查端口占用...${NC}"

if check_port 8000; then
    kill_port 8000
fi

if check_port 3000; then
    kill_port 3000
fi

echo -e "${GREEN}✅ 端口清理完成${NC}"
echo ""

# 启动后端服务器
echo -e "${BLUE}🚀 启动后端API服务器 (端口 8000)...${NC}"

cd backend/standalone_textbook_server

# 检查Python依赖
if [ ! -f "textbook_test.db" ]; then
    echo -e "${YELLOW}📦 首次运行，将创建数据库...${NC}"
fi

# 启动后端服务器（后台运行）
python3 main.py > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
echo -e "${YELLOW}⏳ 等待后端服务器启动...${NC}"
sleep 3

# 检查后端是否启动成功
if kill -0 $BACKEND_PID 2>/dev/null; then
    # 测试健康检查
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务器启动成功!${NC}"
        echo -e "   📍 API文档: ${BLUE}http://localhost:8000/docs${NC}"
        echo -e "   📍 健康检查: ${BLUE}http://localhost:8000/health${NC}"
    else
        echo -e "${RED}❌ 后端服务器启动失败 - 健康检查未通过${NC}"
        echo -e "${YELLOW}💡 查看日志: tail -f logs/backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
else
    echo -e "${RED}❌ 后端服务器进程启动失败${NC}"
    echo -e "${YELLOW}💡 查看日志: cat logs/backend.log${NC}"
    exit 1
fi

cd ../..
echo ""

# 启动前端服务器
echo -e "${BLUE}🚀 启动前端开发服务器 (端口 3000)...${NC}"

cd frontend

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 首次运行，正在安装依赖...${NC}"
    npm install
fi

# 启动前端服务器（后台运行）
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
echo -e "${YELLOW}⏳ 等待前端服务器编译...${NC}"
sleep 10

# 检查前端是否启动成功
if kill -0 $FRONTEND_PID 2>/dev/null; then
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务器启动成功!${NC}"
        echo -e "   📍 演示页面: ${BLUE}http://localhost:3000/textbook-demo${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务器进程运行中，但HTTP未响应（可能还在编译）${NC}"
        echo -e "${YELLOW}💡 查看日志: tail -f logs/frontend.log${NC}"
    fi
else
    echo -e "${RED}❌ 前端服务器进程启动失败${NC}"
    echo -e "${YELLOW}💡 查看日志: cat logs/frontend.log${NC}"
    echo -e "${YELLOW}🔄 正在清理后端进程...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

cd ..
echo ""

# 保存PID到文件
mkdir -p .pids
echo $BACKEND_PID > .pids/backend.pid
echo $FRONTEND_PID > .pids/frontend.pid

echo "============================================================"
echo -e "${GREEN}🎉 开发环境启动完成!${NC}"
echo "============================================================"
echo ""
echo -e "${BLUE}📍 服务地址:${NC}"
echo -e "   - 后端API:    http://localhost:8000"
echo -e "   - API文档:    http://localhost:8000/docs"
echo -e "   - 前端应用:   http://localhost:3000"
echo -e "   - 演示页面:   http://localhost:3000/textbook-demo"
echo ""
echo -e "${BLUE}📝 进程信息:${NC}"
echo -e "   - 后端PID:    $BACKEND_PID"
echo -e "   - 前端PID:    $FRONTEND_PID"
echo ""
echo -e "${BLUE}📋 常用命令:${NC}"
echo -e "   - 查看后端日志:  tail -f logs/backend.log"
echo -e "   - 查看前端日志:  tail -f logs/frontend.log"
echo -e "   - 停止所有服务:  ./stop-dev.sh"
echo -e "   - 测试API:       curl http://localhost:8000/health"
echo ""
echo -e "${YELLOW}💡 提示: 服务运行在后台，关闭终端不会停止服务${NC}"
echo -e "${YELLOW}   使用 ./stop-dev.sh 停止所有服务${NC}"
echo ""
