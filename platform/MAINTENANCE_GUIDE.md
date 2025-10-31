# 🔧 工程学习平台 - 运维维护手册

**版本:** v1.1.0-rc1  
**更新日期:** 2025-10-31  
**适用人员:** 系统管理员、运维工程师

---

## 📋 目录

1. [日常运维](#日常运维)
2. [监控告警](#监控告警)
3. [故障排查](#故障排查)
4. [备份恢复](#备份恢复)
5. [性能优化](#性能优化)
6. [安全维护](#安全维护)
7. [版本更新](#版本更新)

---

## 🔄 日常运维

### 系统检查清单

#### 每日检查 (10分钟)

```bash
# 1. 检查服务状态
docker-compose ps

# 2. 查看资源使用
docker stats --no-stream

# 3. 检查日志错误
docker-compose logs --tail=100 | grep -i error

# 4. 检查磁盘空间
df -h

# 5. 检查健康状态
curl http://localhost:8000/health
```

#### 每周检查 (30分钟)

```bash
# 1. 查看详细日志
docker-compose logs --tail=1000 backend

# 2. 数据库性能
docker-compose exec postgres psql -U postgres -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;"

# 3. Redis内存使用
docker-compose exec redis redis-cli info memory

# 4. 清理Docker资源
docker system prune -f

# 5. 更新系统软件包
apt update && apt upgrade -y
```

#### 每月检查 (1小时)

```bash
# 1. 完整备份
./scripts/backup_full.sh

# 2. 安全更新
apt list --upgradable | grep -i security

# 3. SSL证书检查
openssl x509 -in /path/to/cert.pem -noout -enddate

# 4. 性能测试
cd backend && pytest tests/test_performance.py

# 5. 日志归档
./scripts/archive_logs.sh
```

---

## 📊 监控告警

### 关键指标

#### 系统指标

```yaml
CPU使用率:
  - 警告: >70%
  - 严重: >90%
  - 检查: docker stats

内存使用率:
  - 警告: >80%
  - 严重: >95%
  - 检查: free -h

磁盘使用率:
  - 警告: >80%
  - 严重: >90%
  - 检查: df -h

磁盘IO:
  - 警告: >80%
  - 严重: >95%
  - 检查: iostat -x 1
```

#### 应用指标

```yaml
API响应时间:
  - 正常: <100ms
  - 警告: 100-500ms
  - 严重: >500ms
  - 监控: Prometheus + Grafana

错误率:
  - 正常: <1%
  - 警告: 1-5%
  - 严重: >5%
  - 查看: docker-compose logs backend | grep ERROR

数据库连接:
  - 正常: <50
  - 警告: 50-80
  - 严重: >80
  - 查询: SELECT count(*) FROM pg_stat_activity;

Redis内存:
  - 正常: <1GB
  - 警告: 1-2GB
  - 严重: >2GB
  - 查询: redis-cli info memory
```

### 监控命令

```bash
# 实时监控脚本
cat > /usr/local/bin/platform-monitor.sh << 'EOF'
#!/bin/bash
echo "=== 工程学习平台监控 ==="
echo "时间: $(date)"
echo ""

echo "1. 服务状态:"
docker-compose ps

echo ""
echo "2. 资源使用:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "3. API健康:"
curl -s http://localhost:8000/health | jq .

echo ""
echo "4. 最近错误:"
docker-compose logs --tail=20 backend | grep -i error | tail -5
EOF

chmod +x /usr/local/bin/platform-monitor.sh

# 运行监控
platform-monitor.sh
```

---

## 🔍 故障排查

### 常见问题

#### 1. 服务无法启动

**症状:** `docker-compose up` 失败

**排查步骤:**

```bash
# 1. 查看详细日志
docker-compose up --abort-on-container-exit

# 2. 检查端口占用
netstat -tlnp | grep -E '(3000|8000|5432|6379)'

# 3. 检查环境变量
docker-compose config

# 4. 检查磁盘空间
df -h

# 5. 清理并重启
docker-compose down -v
docker system prune -af
docker-compose up -d
```

#### 2. API响应慢

**症状:** 响应时间>500ms

**排查步骤:**

```bash
# 1. 检查数据库查询
docker-compose exec postgres psql -U postgres -d learning_platform -c "
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC
LIMIT 10;"

# 2. 检查Redis
docker-compose exec redis redis-cli --latency

# 3. 检查网络
docker-compose exec backend ping -c 3 postgres

# 4. 查看慢查询日志
docker-compose logs backend | grep "slow query"

# 5. 检查索引
docker-compose exec postgres psql -U postgres -d learning_platform -c "
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;"
```

#### 3. 数据库连接池耗尽

**症状:** "Too many connections"

**解决方案:**

```bash
# 1. 查看当前连接
docker-compose exec postgres psql -U postgres -c "
SELECT count(*), state 
FROM pg_stat_activity 
GROUP BY state;"

# 2. 终止空闲连接
docker-compose exec postgres psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
  AND state_change < now() - interval '10 minutes';"

# 3. 增加连接池大小（修改配置）
# 编辑 backend/app/core/config.py
# DB_POOL_SIZE = 20  # 增加到30

# 4. 重启服务
docker-compose restart backend
```

#### 4. Redis内存不足

**症状:** "OOM command not allowed"

**解决方案:**

```bash
# 1. 查看内存使用
docker-compose exec redis redis-cli info memory

# 2. 清理过期键
docker-compose exec redis redis-cli --scan --pattern "*" | \
  xargs docker-compose exec redis redis-cli del

# 3. 设置内存限制和淘汰策略
docker-compose exec redis redis-cli config set maxmemory 1gb
docker-compose exec redis redis-cli config set maxmemory-policy allkeys-lru

# 4. 重启Redis
docker-compose restart redis
```

#### 5. 前端无法访问后端

**症状:** CORS错误或网络错误

**排查步骤:**

```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查CORS配置
docker-compose logs backend | grep CORS

# 3. 检查网络连接
docker network ls
docker network inspect platform_platform_network

# 4. 检查环境变量
docker-compose exec frontend printenv | grep API

# 5. 重启服务
docker-compose restart frontend backend
```

---

## 💾 备份恢复

### 备份策略

#### 数据库备份

**每日自动备份:**

```bash
# 创建备份脚本
cat > /usr/local/bin/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/platform"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U postgres learning_platform | \
  gzip > $BACKUP_FILE

# 保留最近7天的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_FILE"
EOF

chmod +x /usr/local/bin/backup-db.sh

# 添加到crontab
echo "0 2 * * * /usr/local/bin/backup-db.sh" | crontab -
```

#### 文件备份

```bash
# 备份上传文件和配置
tar -czf /var/backups/platform/files_$(date +%Y%m%d).tar.gz \
  /workspace/platform/backend/uploads \
  /workspace/platform/.env \
  /workspace/platform/docker-compose.yml
```

### 恢复数据

#### 数据库恢复

```bash
# 1. 停止服务
docker-compose stop backend

# 2. 恢复数据库
gunzip < /var/backups/platform/db_backup_20251031.sql.gz | \
  docker-compose exec -T postgres psql -U postgres learning_platform

# 3. 重启服务
docker-compose start backend

# 4. 验证
curl http://localhost:8000/health
```

#### 文件恢复

```bash
# 恢复上传文件
tar -xzf /var/backups/platform/files_20251031.tar.gz -C /
```

---

## ⚡ 性能优化

### 数据库优化

#### 查询优化

```sql
-- 1. 分析慢查询
SELECT 
  calls,
  total_time,
  mean_time,
  query
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- 2. 更新统计信息
ANALYZE;

-- 3. 重建索引
REINDEX DATABASE learning_platform;

-- 4. 清理死元组
VACUUM FULL ANALYZE;
```

#### 配置调优

```ini
# postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Redis优化

```bash
# 1. 启用持久化
redis-cli config set save "900 1 300 10 60 10000"

# 2. 设置内存策略
redis-cli config set maxmemory-policy allkeys-lru

# 3. 启用压缩
redis-cli config set list-compress-depth 1
```

### 应用优化

```python
# 1. 启用连接池
# app/core/database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

# 2. 启用查询缓存
# app/services/book_service.py
@cache(ttl=300)
async def get_books(db: AsyncSession):
    # ...

# 3. 使用批量查询
# 避免N+1查询
books = await db.execute(
    select(Book).options(
        joinedload(Book.chapters)
    )
)
```

---

## 🔒 安全维护

### 安全检查清单

#### 每周安全检查

```bash
# 1. 检查系统更新
apt list --upgradable | grep -i security

# 2. 检查失败登录
docker-compose logs backend | grep "login failed"

# 3. 检查异常请求
docker-compose logs nginx | grep -E "(403|404|500)"

# 4. 检查Docker镜像漏洞
docker scan platform_backend

# 5. 检查SSL证书
openssl s_client -connect localhost:443 -servername yourdomain.com
```

#### 安全加固

```bash
# 1. 限制SSH访问
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
AllowUsers admin

# 2. 配置防火墙
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 3. 启用fail2ban
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# 4. 定期更新密钥
# 更新JWT密钥、数据库密码等
```

### 日志审计

```bash
# 审计日志分析
docker-compose logs --since 24h backend | \
  grep -E "(login|logout|delete|update)" | \
  awk '{print $1, $2, $NF}' | \
  sort | uniq -c | sort -rn
```

---

## 🔄 版本更新

### 更新流程

#### 1. 准备阶段

```bash
# 1. 备份数据
/usr/local/bin/backup-db.sh

# 2. 备份代码
cd /workspace/platform
git stash
git tag -a v$(cat VERSION) -m "Backup before update"

# 3. 通知用户
# 发送维护通知邮件
```

#### 2. 更新代码

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 检查变更
git log --oneline -10

# 3. 更新依赖
cd backend
pip install -r requirements.txt

cd ../frontend
npm install
```

#### 3. 数据库迁移

```bash
# 1. 检查迁移
python scripts/migrate_db.py current

# 2. 执行迁移
python scripts/migrate_db.py upgrade

# 3. 验证
python scripts/migrate_db.py current
```

#### 4. 重启服务

```bash
# 1. 构建新镜像
docker-compose build --no-cache

# 2. 滚动更新
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend

# 3. 验证
curl http://localhost:8000/health
curl http://localhost:3000
```

#### 5. 验证测试

```bash
# 1. 运行测试
cd backend
pytest tests/ -v

# 2. 检查日志
docker-compose logs --tail=100

# 3. 监控指标
platform-monitor.sh
```

#### 6. 回滚（如需要）

```bash
# 1. 停止服务
docker-compose down

# 2. 恢复代码
git reset --hard <previous-commit>

# 3. 恢复数据库
gunzip < /var/backups/platform/db_backup_latest.sql.gz | \
  docker-compose exec -T postgres psql -U postgres learning_platform

# 4. 重启服务
docker-compose up -d
```

---

## 📞 紧急联系

### 故障升级流程

```
Level 1 (轻微):
  - 响应时间: 4小时
  - 联系人: 运维工程师
  - 邮箱: ops@example.com

Level 2 (重要):
  - 响应时间: 1小时
  - 联系人: 技术主管
  - 电话: +86-xxx-xxxx

Level 3 (紧急):
  - 响应时间: 15分钟
  - 联系人: CTO
  - 电话: +86-xxx-xxxx (24/7)
```

### 应急响应

```bash
# 紧急重启
docker-compose restart

# 完全重启
docker-compose down
docker-compose up -d

# 查看实时日志
docker-compose logs -f

# 进入容器调试
docker-compose exec backend bash
```

---

## 📝 维护日志

### 日志模板

```
日期: YYYY-MM-DD
操作人: 张三
操作类型: 例行维护/故障处理/版本更新
描述: 详细描述维护内容
影响: 是否影响服务
结果: 成功/失败
备注: 其他说明
```

### 记录示例

```
日期: 2025-10-31
操作人: 运维团队
操作类型: 例行维护
描述: 
  1. 数据库备份
  2. 日志清理
  3. 性能检查
影响: 无
结果: 成功
备注: 所有指标正常
```

---

## ✅ 维护检查表

### 日常检查

- [ ] 服务状态正常
- [ ] 资源使用正常
- [ ] 无错误日志
- [ ] 备份成功
- [ ] 监控正常

### 每周检查

- [ ] 数据库性能正常
- [ ] Redis性能正常
- [ ] 磁盘空间充足
- [ ] 安全检查完成
- [ ] 日志分析完成

### 每月检查

- [ ] 完整备份完成
- [ ] 安全更新完成
- [ ] 性能测试通过
- [ ] SSL证书有效
- [ ] 文档更新完成

---

**维护手册版本:** v1.0  
**最后更新:** 2025-10-31  
**维护团队:** 运维部门
