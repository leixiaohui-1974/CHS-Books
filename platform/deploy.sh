#!/bin/bash

# 工程学习平台 - 一键部署脚本
# 版本: v0.9.0
# 日期: 2025-10-31

set -e

echo "🚀 工程学习平台 - 一键部署脚本"
echo "================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查Docker
echo -e "${BLUE}📦 检查Docker环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker未安装，请先安装Docker${NC}"
    echo "安装指南: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose未安装${NC}"
    echo "安装指南: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✅ Docker环境检查通过${NC}"
echo ""

# 检查环境变量文件
echo -e "${BLUE}📝 检查环境变量配置...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo -e "${YELLOW}⚠️  .env文件不存在，从.env.example复制...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ .env文件已创建${NC}"
        echo -e "${YELLOW}⚠️  请编辑.env文件，配置必要的环境变量${NC}"
        echo ""
        read -p "按回车键继续部署，或Ctrl+C退出编辑.env文件..."
    else
        echo -e "${RED}❌ .env.example文件不存在${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env文件已存在${NC}"
fi
echo ""

# 选择部署模式
echo -e "${BLUE}🎯 选择部署模式:${NC}"
echo "1) 开发环境 (development)"
echo "2) 生产环境 (production)"
read -p "请选择 [1/2, 默认1]: " mode
mode=${mode:-1}

if [ "$mode" == "2" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV="production"
    echo -e "${YELLOW}📦 生产环境部署模式${NC}"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV="development"
    echo -e "${GREEN}🔧 开发环境部署模式${NC}"
fi
echo ""

# 构建镜像
echo -e "${BLUE}🏗️  构建Docker镜像...${NC}"
if [ -f "docker/$COMPOSE_FILE" ]; then
    docker-compose -f "docker/$COMPOSE_FILE" build --no-cache
else
    echo -e "${YELLOW}⚠️  未找到$COMPOSE_FILE，使用默认配置${NC}"
    docker-compose build --no-cache
fi
echo -e "${GREEN}✅ 镜像构建完成${NC}"
echo ""

# 启动服务
echo -e "${BLUE}🚀 启动服务...${NC}"
if [ -f "docker/$COMPOSE_FILE" ]; then
    docker-compose -f "docker/$COMPOSE_FILE" up -d
else
    docker-compose up -d
fi

echo -e "${GREEN}✅ 服务启动成功${NC}"
echo ""

# 等待服务就绪
echo -e "${BLUE}⏳ 等待服务就绪...${NC}"
sleep 5

# 健康检查
echo -e "${BLUE}🏥 健康检查...${NC}"
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务健康${NC}"
        break
    fi
    retry_count=$((retry_count+1))
    echo -e "${YELLOW}⏳ 等待后端启动... ($retry_count/$max_retries)${NC}"
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo -e "${RED}❌ 后端服务启动超时${NC}"
    echo "查看日志: docker-compose logs backend"
    exit 1
fi

# 显示服务状态
echo ""
echo -e "${BLUE}📊 服务状态:${NC}"
if [ -f "docker/$COMPOSE_FILE" ]; then
    docker-compose -f "docker/$COMPOSE_FILE" ps
else
    docker-compose ps
fi
echo ""

# 显示访问信息
echo -e "${GREEN}=================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}=================================${NC}"
echo ""
echo -e "${BLUE}🌐 访问地址:${NC}"
echo "  前端应用:     http://localhost:3000"
echo "  后端API:      http://localhost:8000"
echo "  API文档:      http://localhost:8000/docs"
echo "  交互式文档:   http://localhost:8000/redoc"
echo ""
echo -e "${BLUE}📊 管理工具:${NC}"
echo "  PostgreSQL:   localhost:5432"
echo "  Redis:        localhost:6379"
echo "  MongoDB:      localhost:27017"
echo "  MinIO:        http://localhost:9000"
echo ""
echo -e "${BLUE}🔧 常用命令:${NC}"
echo "  查看日志:     docker-compose logs -f"
echo "  停止服务:     docker-compose down"
echo "  重启服务:     docker-compose restart"
echo "  查看状态:     docker-compose ps"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo "  - 首次部署需要初始化数据库"
echo "  - 运行: docker-compose exec backend python scripts/init_db.py"
echo "  - 填充示例数据: docker-compose exec backend python scripts/seed_data.py"
echo ""
echo -e "${GREEN}🎉 祝您使用愉快！${NC}"
