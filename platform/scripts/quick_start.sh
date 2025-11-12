#!/bin/bash
# Platform 快速启动脚本
# 用途：一键设置开发环境

set -e  # 遇到错误立即退出

echo "======================================"
echo "Platform 开发环境快速设置"
echo "======================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查操作系统
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo -e "${GREEN}检测到操作系统: ${MACHINE}${NC}"
echo ""

# 1. 检查必需的工具
echo "==== 步骤 1/7: 检查必需工具 ===="
echo ""

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 已安装"
        return 0
    else
        echo -e "${RED}✗${NC} $1 未安装"
        return 1
    fi
}

MISSING_TOOLS=0

check_command "docker" || MISSING_TOOLS=1
check_command "docker-compose" || MISSING_TOOLS=1
check_command "python3" || MISSING_TOOLS=1
check_command "node" || MISSING_TOOLS=1
check_command "npm" || MISSING_TOOLS=1
check_command "git" || MISSING_TOOLS=1

echo ""

if [ $MISSING_TOOLS -eq 1 ]; then
    echo -e "${RED}错误：缺少必需工具，请先安装以上工具${NC}"
    echo ""
    echo "安装指南："
    if [ "$MACHINE" = "Mac" ]; then
        echo "  brew install docker docker-compose python@3.11 node"
    elif [ "$MACHINE" = "Linux" ]; then
        echo "  sudo apt-get install -y docker.io docker-compose python3.11 nodejs npm"
    fi
    exit 1
fi

# 2. 克隆或进入项目目录
echo "==== 步骤 2/7: 检查项目目录 ===="
echo ""

if [ ! -d "platform" ]; then
    echo -e "${YELLOW}警告：不在项目根目录，尝试进入 platform 目录${NC}"
    if [ -d "../platform" ]; then
        cd ../platform
    else
        echo -e "${RED}错误：找不到 platform 目录${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓${NC} 项目目录确认"
echo ""

# 3. 创建 Python 虚拟环境
echo "==== 步骤 3/7: 设置 Python 虚拟环境 ===="
echo ""

cd backend

if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} 虚拟环境创建成功"
else
    echo -e "${YELLOW}虚拟环境已存在，跳过创建${NC}"
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo ""
echo "安装 Python 依赖..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# 检查是否有开发依赖文件
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

echo -e "${GREEN}✓${NC} Python 依赖安装完成"
echo ""

cd ..

# 4. 设置前端环境
echo "==== 步骤 4/7: 设置前端环境 ===="
echo ""

cd frontend

if [ ! -d "node_modules" ]; then
    echo "安装 Node.js 依赖..."
    npm install
    echo -e "${GREEN}✓${NC} Node.js 依赖安装完成"
else
    echo -e "${YELLOW}node_modules 已存在，跳过安装${NC}"
    echo "如需重新安装，运行: rm -rf node_modules && npm install"
fi

echo ""

cd ..

# 5. 配置环境变量
echo "==== 步骤 5/7: 配置环境变量 ===="
echo ""

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "复制 .env.example 到 .env..."
        cp .env.example .env
        echo -e "${GREEN}✓${NC} .env 文件创建成功"
        echo ""
        echo -e "${YELLOW}⚠ 重要：请编辑 .env 文件，填写必要的配置：${NC}"
        echo "  - DATABASE_URL"
        echo "  - REDIS_URL"
        echo "  - JWT_SECRET_KEY"
        echo "  - OPENAI_API_KEY (如果使用 AI 功能)"
        echo ""
        read -p "是否现在编辑 .env 文件? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo -e "${RED}错误：找不到 .env.example 文件${NC}"
    fi
else
    echo -e "${YELLOW}.env 文件已存在${NC}"
fi

echo ""

# 6. 启动 Docker 服务
echo "==== 步骤 6/7: 启动 Docker 服务 ===="
echo ""

if [ -f "docker-compose.dev.yml" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
elif [ -f "docker-compose.v2.yml" ]; then
    COMPOSE_FILE="docker-compose.v2.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

echo "使用配置文件: $COMPOSE_FILE"
echo ""

read -p "是否启动 Docker 服务 (PostgreSQL, Redis, MongoDB)? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "启动 Docker 服务..."
    docker-compose -f $COMPOSE_FILE up -d postgres redis mongo

    echo ""
    echo "等待数据库就绪..."
    sleep 10

    echo -e "${GREEN}✓${NC} Docker 服务启动成功"
    echo ""
    echo "运行中的服务："
    docker-compose -f $COMPOSE_FILE ps
else
    echo -e "${YELLOW}跳过 Docker 服务启动${NC}"
fi

echo ""

# 7. 初始化数据库
echo "==== 步骤 7/7: 初始化数据库 ===="
echo ""

read -p "是否运行数据库迁移? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd backend
    source venv/bin/activate

    # 检查是否安装了 alembic
    if command -v alembic &> /dev/null; then
        echo "运行数据库迁移..."
        alembic upgrade head
        echo -e "${GREEN}✓${NC} 数据库迁移完成"
    else
        echo -e "${YELLOW}Alembic 未安装，跳过数据库迁移${NC}"
        echo "安装: pip install alembic"
    fi

    cd ..
else
    echo -e "${YELLOW}跳过数据库迁移${NC}"
fi

echo ""
echo ""

# 完成
echo "======================================"
echo -e "${GREEN}✓ 开发环境设置完成！${NC}"
echo "======================================"
echo ""
echo "下一步："
echo ""
echo "1. 启动后端开发服务器："
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. 启动前端开发服务器（新终端）："
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. 访问应用："
echo "   - 后端 API 文档: http://localhost:8000/docs"
echo "   - 前端应用: http://localhost:3000"
echo ""
echo "4. 运行测试："
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   pytest tests/ -v"
echo ""
echo "更多信息请查看: platform/IMPLEMENTATION_GUIDE.md"
echo ""
