#!/bin/bash

# 工程学习平台 - 测试脚本
# 版本: v0.9.0
# 日期: 2025-10-31

set -e

echo "🧪 工程学习平台 - 测试脚本"
echo "=========================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查Python
echo -e "${BLUE}🐍 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION${NC}"
echo ""

# 检查依赖
echo -e "${BLUE}📦 检查Python依赖...${NC}"
if ! python3 -c "import pytest" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  pytest未安装，正在安装依赖...${NC}"
    pip3 install -r requirements.txt --quiet
    pip3 install asyncpg aiosqlite --quiet
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✅ 依赖已安装${NC}"
fi
echo ""

# 运行测试
echo -e "${BLUE}🧪 运行测试套件...${NC}"
echo ""

# 服务层测试
echo -e "${BLUE}[1/3] 服务层测试${NC}"
TESTING=1 python3 -m pytest tests/test_*_service.py -v --tb=short

echo ""

# API集成测试
echo -e "${BLUE}[2/3] API集成测试${NC}"
TESTING=1 python3 -m pytest tests/test_api_integration.py -v --tb=line 2>&1 | head -50

echo ""

# 测试总结
echo -e "${BLUE}[3/3] 测试总结${NC}"
TESTING=1 python3 -m pytest tests/ -v --tb=no -q

echo ""
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✅ 测试执行完成！${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""

# 测试覆盖率（可选）
read -p "是否生成测试覆盖率报告? [y/N]: " generate_coverage
if [ "$generate_coverage" == "y" ] || [ "$generate_coverage" == "Y" ]; then
    echo ""
    echo -e "${BLUE}📊 生成覆盖率报告...${NC}"
    TESTING=1 python3 -m pytest tests/ --cov=app --cov-report=html --cov-report=term
    echo ""
    echo -e "${GREEN}✅ 覆盖率报告已生成: htmlcov/index.html${NC}"
fi

echo ""
echo -e "${BLUE}💡 提示:${NC}"
echo "  - 核心服务层测试应该100%通过"
echo "  - API集成测试可能需要修复fixture"
echo "  - 查看详细报告: QUICK_TEST_GUIDE.md"
echo ""
echo -e "${GREEN}🎉 测试完成！${NC}"
