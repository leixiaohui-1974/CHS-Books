# ✅ 工程学习平台 - 最终部署检查清单

**版本**: v1.2.0-beta → Production  
**检查日期**: 2025-10-31  
**负责人**: DevOps Team  

---

## 🎯 部署前检查 (Pre-Deployment)

### 1. 代码质量检查
- [x] 所有核心测试通过 (28/28)
- [x] 代码Review完成
- [x] 无Critical Bug
- [x] 无已知Security漏洞
- [x] 代码格式化完成
- [x] 依赖项安全扫描通过

### 2. 配置文件检查
- [x] `.env.production` 已创建
- [ ] **所有敏感配置已填入实际值**
  - [ ] 数据库密码
  - [ ] JWT密钥
  - [ ] Stripe API密钥
  - [ ] Alipay配置
  - [ ] WeChat Pay配置
  - [ ] OpenAI API密钥
  - [ ] SMTP配置
- [x] `docker-compose.production.yml` 已优化
- [x] `nginx.prod.conf` 已配置
- [ ] **SSL证书已准备** (Let's Encrypt)

### 3. 数据库准备
- [x] PostgreSQL 15安装完成
- [x] 数据库用户创建
- [x] 数据库表结构就绪
- [ ] **数据库备份策略配置**
- [x] 索引优化完成
- [ ] 主从复制配置 (生产环境)

### 4. 缓存与存储
- [x] Redis 7安装配置
- [ ] Redis持久化配置
- [ ] **Redis密码设置**
- [ ] MinIO配置完成
- [ ] 对象存储bucket创建

### 5. 监控与日志
- [x] Prometheus配置
- [x] Grafana配置
- [ ] **Grafana仪表板导入**
- [ ] **告警规则配置**
- [x] 日志系统就绪
- [ ] 日志聚合配置 (ELK Stack)

---

## 🚀 部署步骤 (Deployment)

### Step 1: 服务器准备
```bash
# 1.1 系统更新
sudo apt update && sudo apt upgrade -y

# 1.2 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 1.3 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 1.4 验证安装
docker --version
docker-compose --version
```
- [ ] 完成

### Step 2: 代码部署
```bash
# 2.1 克隆代码
cd /opt
sudo git clone <repository> platform
cd platform

# 2.2 配置环境
sudo cp .env.example .env.production
sudo vim .env.production  # 填入实际配置

# 2.3 配置权限
sudo chown -R $USER:$USER /opt/platform
```
- [ ] 完成

### Step 3: SSL证书配置
```bash
# 3.1 安装Certbot
sudo apt install certbot python3-certbot-nginx -y

# 3.2 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 3.3 自动续期
sudo systemctl enable certbot.timer
```
- [ ] 完成

### Step 4: 启动服务
```bash
# 4.1 构建镜像
docker-compose -f docker-compose.production.yml build

# 4.2 启动服务
docker-compose -f docker-compose.production.yml up -d

# 4.3 查看日志
docker-compose -f docker-compose.production.yml logs -f
```
- [ ] 完成

### Step 5: 数据库初始化
```bash
# 5.1 初始化表结构
docker-compose exec backend python scripts/init_db.py

# 5.2 导入种子数据 (可选)
docker-compose exec backend python scripts/seed_data.py

# 5.3 创建管理员账户
docker-compose exec backend python scripts/create_admin.py
```
- [ ] 完成

---

## 🔍 部署后验证 (Post-Deployment)

### 1. 服务健康检查
```bash
# 检查所有容器状态
docker-compose ps

# 检查健康端点
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health

# 检查前端
curl http://localhost:3000
```
- [ ] 所有服务Running
- [ ] 健康检查返回OK
- [ ] 前端页面正常加载

### 2. API测试
```bash
# 测试注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test123!@#"}'

# 测试登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test123!@#"}'

# 测试获取书籍列表
curl http://localhost:8000/api/v1/books
```
- [ ] 注册成功
- [ ] 登录成功并返回Token
- [ ] API正常响应

### 3. 数据库连接
```bash
# 连接PostgreSQL
docker-compose exec postgres psql -U elp_user -d elp_db -c "SELECT COUNT(*) FROM users;"

# 连接Redis
docker-compose exec redis redis-cli ping
```
- [ ] PostgreSQL连接正常
- [ ] Redis响应PONG

### 4. 支付测试
```bash
# 创建测试订单
curl -X POST http://localhost:8000/api/v1/payments/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"book_id":1,"payment_method":"stripe"}'
```
- [ ] 订单创建成功
- [ ] 返回订单号

### 5. 性能测试
```bash
# 并发测试 (需要安装ab或wrk)
ab -n 1000 -c 100 http://localhost:8000/api/v1/books

# 或使用wrk
wrk -t4 -c100 -d30s http://localhost:8000/api/v1/books
```
- [ ] QPS > 100
- [ ] 响应时间 < 100ms
- [ ] 错误率 < 1%

---

## 📊 监控配置 (Monitoring)

### 1. Prometheus
```bash
# 访问Prometheus
http://your-domain:9090

# 验证指标
- http_requests_total
- http_request_duration_seconds
- database_connections
```
- [ ] Prometheus可访问
- [ ] 指标正常收集

### 2. Grafana
```bash
# 访问Grafana
http://your-domain:3000
Username: admin
Password: (见.env.production)

# 导入仪表板
- Dashboard ID: 12345 (FastAPI)
- Dashboard ID: 67890 (PostgreSQL)
```
- [ ] Grafana可访问
- [ ] 仪表板显示正常
- [ ] 数据实时更新

### 3. 日志系统
```bash
# 查看应用日志
docker-compose logs backend | tail -100

# 查看访问日志
tail -f logs/access_$(date +%Y-%m-%d).log

# 查看错误日志
tail -f logs/error_$(date +%Y-%m-%d).log
```
- [ ] 日志正常写入
- [ ] 日志轮转工作
- [ ] 错误日志可查询

---

## 🔐 安全加固 (Security)

### 1. 防火墙配置
```bash
# 启用UFW
sudo ufw enable

# 允许必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 禁止其他端口
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 查看状态
sudo ufw status
```
- [ ] 防火墙已启用
- [ ] 端口配置正确

### 2. 系统加固
```bash
# 禁用root SSH登录
sudo vim /etc/ssh/sshd_config
# 设置: PermitRootLogin no

# 配置fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 自动安全更新
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```
- [ ] SSH配置加固
- [ ] Fail2ban已配置
- [ ] 自动更新已启用

### 3. 应用安全
```bash
# 检查环境变量
docker-compose exec backend printenv | grep -i key

# 检查文件权限
ls -la /opt/platform/.env.production

# 验证JWT配置
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"username":"admin","password":"wrong"}' | jq
```
- [ ] 敏感信息未泄露
- [ ] 文件权限600
- [ ] JWT认证工作正常

---

## 📋 备份策略 (Backup)

### 1. 数据库备份
```bash
# 创建备份脚本
sudo vim /opt/scripts/backup_db.sh

#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U elp_user elp_db > /backup/db_$DATE.sql
gzip /backup/db_$DATE.sql
find /backup -name "db_*.sql.gz" -mtime +7 -delete

# 设置定时任务
crontab -e
0 2 * * * /opt/scripts/backup_db.sh
```
- [ ] 备份脚本已创建
- [ ] 定时任务已配置
- [ ] 备份目录可写

### 2. 代码备份
```bash
# 创建代码备份
sudo tar -czf /backup/platform_$(date +%Y%m%d).tar.gz /opt/platform

# 定时任务
0 3 * * 0 tar -czf /backup/platform_$(date +\%Y\%m\%d).tar.gz /opt/platform
```
- [ ] 代码备份可用
- [ ] 定时任务已配置

### 3. 日志备份
```bash
# 日志归档
find /opt/platform/logs -name "*.log" -mtime +30 -exec gzip {} \;
find /opt/platform/logs -name "*.log.gz" -mtime +90 -delete
```
- [ ] 日志归档策略配置
- [ ] 清理策略配置

---

## 🔄 灾难恢复测试 (Disaster Recovery)

### 1. 数据库恢复测试
```bash
# 停止服务
docker-compose down

# 恢复数据库
gunzip -c /backup/db_20251031.sql.gz | docker-compose exec -T postgres psql -U elp_user elp_db

# 重启服务
docker-compose up -d
```
- [ ] 恢复成功
- [ ] 数据完整
- [ ] 服务正常

### 2. 完整恢复测试
```bash
# 模拟完全故障
sudo rm -rf /opt/platform/*

# 从备份恢复
sudo tar -xzf /backup/platform_20251031.tar.gz -C /opt/

# 恢复数据库
# (同上)

# 重启所有服务
docker-compose up -d
```
- [ ] 恢复成功
- [ ] 所有功能正常

---

## 📈 性能优化 (Performance)

### 1. 数据库优化
```sql
-- 分析慢查询
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- 创建缺失索引
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```
- [ ] 慢查询已优化
- [ ] 索引已完善

### 2. 缓存优化
```bash
# Redis内存使用
docker-compose exec redis redis-cli info memory

# 缓存命中率
docker-compose exec redis redis-cli info stats | grep hits
```
- [ ] 内存使用正常
- [ ] 缓存命中率 > 80%

### 3. 应用优化
```bash
# 检查进程数
ps aux | grep gunicorn | wc -l

# 检查内存使用
docker stats backend
```
- [ ] Worker数量合理
- [ ] 内存使用 < 50%

---

## 📞 应急联系 (Emergency Contacts)

### 团队联系方式
- **DevOps负责人**: [姓名] [电话] [邮箱]
- **后端负责人**: [姓名] [电话] [邮箱]
- **前端负责人**: [姓名] [电话] [邮箱]
- **DBA**: [姓名] [电话] [邮箱]

### 服务商支持
- **云服务商**: [名称] [支持热线]
- **CDN服务商**: [名称] [支持热线]
- **支付服务商**: [名称] [支持热线]

---

## ✅ 最终检查 (Final Check)

### 关键指标确认
- [ ] **所有服务Running** - `docker-compose ps`
- [ ] **API响应正常** - 响应时间 < 100ms
- [ ] **数据库连接正常** - 连接数 < 80%
- [ ] **缓存工作正常** - 命中率 > 80%
- [ ] **日志正常写入** - 无ERROR级别日志
- [ ] **监控数据正常** - Grafana有数据
- [ ] **SSL证书有效** - 有效期 > 30天
- [ ] **备份任务运行** - 最近24小时有备份
- [ ] **防火墙已启用** - `ufw status`
- [ ] **域名解析正常** - `nslookup yourdomain.com`

### 功能测试清单
- [ ] 用户注册
- [ ] 用户登录
- [ ] 浏览课程
- [ ] 购买课程
- [ ] 在线支付
- [ ] 学习进度追踪
- [ ] AI助手对话
- [ ] 优惠券使用
- [ ] 数据统计查看
- [ ] 管理后台访问

---

## 🎉 上线确认 (Go-Live Confirmation)

### 签字确认
- [ ] **开发负责人签字**: _______________  日期: ___________
- [ ] **测试负责人签字**: _______________  日期: ___________
- [ ] **运维负责人签字**: _______________  日期: ___________
- [ ] **项目经理签字**: _______________  日期: ___________
- [ ] **技术总监签字**: _______________  日期: ___________

### 上线时间
- **计划上线时间**: 2025-10-31 23:00:00
- **实际上线时间**: ___________________
- **上线负责人**: _____________________

---

## 📝 备注 (Notes)

### 重要提醒
1. ⚠️ **所有敏感配置必须使用真实值，不要使用示例值**
2. ⚠️ **SSL证书必须配置，不要使用HTTP**
3. ⚠️ **数据库备份必须验证可恢复**
4. ⚠️ **监控告警必须配置并测试**
5. ⚠️ **应急联系人必须可达**

### 已知问题
- 部分集成测试需要真实API密钥 (可在生产环境测试)
- 微信支付回调需要外网可访问的URL

### 后续优化计划
1. 配置CDN加速
2. 实施数据库读写分离
3. 配置Redis Sentinel高可用
4. 实施蓝绿部署
5. 配置自动扩容

---

**✅ 部署检查清单完成！**

*最后更新: 2025-10-31*  
*版本: v1.2.0-final*  
*状态: Ready for Production*
