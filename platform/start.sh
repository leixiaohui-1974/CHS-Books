#!/bin/bash

# ========================================
# Engineering Learning Platform - 一键启动脚本
# ========================================

set -e  # 遇到错误立即退出

echo "========================================"
echo "  Engineering Learning Platform"
echo "  智能工程教学平台 - 启动脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
    echo "   访问: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker环境检查通过${NC}"
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  未找到.env文件，正在创建...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env文件已创建${NC}"
    echo -e "${YELLOW}   请根据需要编辑.env文件后重新运行此脚本${NC}"
    echo ""
fi

# 询问用户是否继续
read -p "是否启动所有服务？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消启动"
    exit 0
fi

echo ""
echo -e "${YELLOW}📦 启动Docker服务...${NC}"
echo ""

cd docker

# 启动服务
docker-compose up -d

echo ""
echo -e "${GREEN}✅ 服务启动成功！${NC}"
echo ""

# 等待服务就绪
echo -e "${YELLOW}⏳ 等待服务就绪（约30秒）...${NC}"
sleep 5

# 检查服务状态
echo ""
echo -e "${YELLOW}📊 服务状态：${NC}"
docker-compose ps

echo ""
echo "========================================"
echo -e "${GREEN}🎉 平台启动完成！${NC}"
echo "========================================"
echo ""
echo "访问地址："
echo -e "  🌐 前端应用: ${GREEN}http://localhost:3000${NC}"
echo -e "  📡 后端API:  ${GREEN}http://localhost:8000${NC}"
echo -e "  📖 API文档:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  🗄️  MinIO:    ${GREEN}http://localhost:9001${NC} (admin/admin)"
echo ""
echo "常用命令："
echo "  查看日志:  docker-compose logs -f"
echo "  停止服务:  docker-compose down"
echo "  重启服务:  docker-compose restart"
echo ""
echo -e "${YELLOW}提示: 首次启动需要等待数据库初始化${NC}"
echo ""
