# 智能水网工程设计教材 - 开发实施计划

**版本**: v3.0-progressive  
**开始日期**: 2025-10-31  
**开发方式**: 递进式开发（Level 1 → 2 → 3 → 4）

---

## 📋 开发总体规划

### 开发原则
1. **由浅入深**：先完成Level 1（单体），再做Level 2-4
2. **充分测试**：每个案例都要通过在环测试
3. **文档同步**：代码和文档同步完成
4. **持续集成**：每完成一个案例立即可用

### 开发周期预估
- **Phase 1** (已完成): 案例1 ✅
- **Phase 2** (2-3个月): Level 1剩余5个案例
- **Phase 3** (3-4个月): Level 2全部6个案例
- **Phase 4** (4-6个月): Level 3全部6个案例
- **Phase 5** (6-8个月): Level 4全部6个案例

**总计**: 15-21个月（可并行缩短至12-16个月）

---

## 🎯 Phase 2 实施计划（当前阶段）

### 目标
完成Level 1（单体建筑物）的剩余5个案例

### 案例优先级

**P0（最高优先级）**:
1. ✅ 案例1：灌溉闸站（已完成）
2. 🔄 **案例2：提水泵站**（正在开发）
3. 案例4：调压阀站

**P1（高优先级）**:
4. 案例3：小型水电站
5. 案例5：排涝闸站

**P2（中优先级）**:
6. 案例6：多功能水闸

### 时间安排（未来8周）

```
Week 1-3: 案例2 - 提水泵站智能化设计
  Week 1: 需求分析、水力设计、代码架构
  Week 2: 控制系统开发、智能体设计
  Week 3: 在环测试、文档编写

Week 4-6: 案例4 - 调压阀站智能控制设计
  Week 4: 阀门水力设计、压力控制算法
  Week 5: 代码实现、测试验证
  Week 6: 文档完善、示例优化

Week 7-8: 案例3 - 小型水电站智能发电设计
  （或根据进度调整）
```

---

## 🔧 案例2开发详细计划

### 案例2：提水泵站智能化设计（L2→L3）

**工程背景**:
- 灌区首部泵站，扬程15m
- 3台立式轴流泵，单泵流量1.2 m³/s
- 总装机功率250kW

**开发任务清单**:

#### 1. 水力设计模块（复用第2本书）

```python
# models/pump.py
class Pump:
    """
    水泵模型（复用第2本书案例10）
    """
    def __init__(self, rated_flow, rated_head, rated_power):
        self.Q_rated = rated_flow
        self.H_rated = rated_head
        self.P_rated = rated_power
        # 泵特性曲线数据
        self.load_pump_curve()
    
    def compute_operating_point(self, Q):
        """计算给定流量下的扬程、效率、功率"""
        H = self.head_curve(Q)
        eta = self.efficiency_curve(Q)
        P = (9.81 * Q * H) / eta
        return H, eta, P
    
    def load_pump_curve(self):
        """加载泵特性曲线"""
        # Q-H曲线（流量-扬程）
        # Q-eta曲线（流量-效率）
        # Q-P曲线（流量-功率）
        pass
```

#### 2. 控制器设计（复用第1本书）

```python
# controllers/pump_controller.py
from books.water_system_control.code.control.pid import PIDController

class PumpStationController:
    """
    泵站控制器
    """
    def __init__(self, n_pumps=3):
        self.n_pumps = n_pumps
        # 进水池水位PID控制器
        self.level_controller = PIDController(
            Kp=1.5, Ki=0.3, Kd=0.05,
            setpoint=3.5,  # 目标水位3.5m
            output_limits=(0, n_pumps)
        )
        self.pump_status = [0] * n_pumps  # 0=停机, 1=运行
    
    def update(self, water_level, dt):
        """
        根据水位决定开几台泵
        """
        # PID输出（0-3）
        control_signal = self.level_controller.update(water_level, dt)
        
        # 转换为开泵台数（四舍五入）
        n_pumps_on = round(control_signal)
        n_pumps_on = max(0, min(self.n_pumps, n_pumps_on))
        
        # 更新泵状态
        self.update_pump_status(n_pumps_on)
        
        return self.pump_status
    
    def update_pump_status(self, n_target):
        """
        更新泵状态，考虑启停约束
        """
        n_current = sum(self.pump_status)
        
        if n_target > n_current:
            # 需要开泵
            self.start_pumps(n_target - n_current)
        elif n_target < n_current:
            # 需要停泵
            self.stop_pumps(n_current - n_target)
    
    def start_pumps(self, n):
        """启动n台泵（轮换运行）"""
        pass
    
    def stop_pumps(self, n):
        """停止n台泵"""
        pass
```

#### 3. 数字孪生仿真（本书新增）

```python
# simulator/pump_station_twin.py
class PumpStationDigitalTwin:
    """
    泵站数字孪生仿真器
    """
    def __init__(self, pumps, controller):
        self.pumps = pumps
        self.controller = controller
        
        # 进水池参数
        self.inlet_pool_area = 200  # m²
        self.inlet_level = 3.5  # 初始水位
        
        # 出水池参数
        self.outlet_pool_area = 150
        self.outlet_level = 2.0
        
        # 时间
        self.t = 0
        self.dt = 60  # 时间步长60秒
    
    def step(self, inflow, demand):
        """
        推进一个时间步
        
        Parameters:
        -----------
        inflow : float
            上游来水流量 [m³/s]
        demand : float
            下游需水流量 [m³/s]
        """
        # 1. 控制器决策（开几台泵）
        pump_status = self.controller.update(self.inlet_level, self.dt)
        
        # 2. 计算泵站总出力
        Q_pump = 0
        for i, status in enumerate(pump_status):
            if status == 1:
                Q_pump += self.pumps[i].Q_rated
        
        # 3. 进水池水量平衡
        dV_inlet = (inflow - Q_pump) * self.dt
        dh_inlet = dV_inlet / self.inlet_pool_area
        self.inlet_level += dh_inlet
        
        # 4. 出水池水量平衡
        dV_outlet = (Q_pump - demand) * self.dt
        dh_outlet = dV_outlet / self.outlet_pool_area
        self.outlet_level += dh_outlet
        
        # 5. 更新时间
        self.t += self.dt
        
        return {
            'inlet_level': self.inlet_level,
            'outlet_level': self.outlet_level,
            'pump_status': pump_status,
            'Q_pump': Q_pump
        }
```

#### 4. 在环测试（本书核心）

```python
# tests/test_case_02.py
def test_pump_station_scenarios():
    """
    案例2在环测试
    """
    # 创建泵站数字孪生
    pumps = [Pump(Q_rated=1.2, H_rated=15, P_rated=80) for _ in range(3)]
    controller = PumpStationController(n_pumps=3)
    twin = PumpStationDigitalTwin(pumps, controller)
    
    # 测试场景1：流量阶跃
    scenario_1 = {
        'name': '上游流量阶跃变化',
        'duration': 3600,  # 1小时
        'inflow': lambda t: 2.0 if t < 1800 else 4.0,  # 0.5h后流量翻倍
        'demand': 3.0  # 恒定需求
    }
    
    results_1 = run_scenario(twin, scenario_1)
    
    # 性能评估
    assert max(results_1['inlet_level']) < 5.0  # 不溢出
    assert min(results_1['inlet_level']) > 2.0  # 不干涸
    
    # 测试场景2：需求波动
    # ...
    
    # 测试场景3：单泵故障
    # ...
```

#### 5. 文档编写

- **README.md** (5000字):
  - 工程背景
  - 对应标准（GB 50265-2022）
  - 复用前序教材成果
  - 设计任务（4个方面）
  - 在环测试
  - 设计交付物

- **main.py** (600行):
  - 完整可运行的示例
  - 详细中文注释
  - 结果可视化

---

## 📁 案例2文件结构

```
case_02_pump_station/
├── README.md                    # 案例说明（5000+字）
├── main.py                      # 主程序（600行）
├── config.json                  # 配置文件
│
├── models/                      # 模型
│   ├── __init__.py
│   ├── pump.py                  # 泵模型（100行）
│   └── pool.py                  # 水池模型（80行）
│
├── controllers/                 # 控制器
│   ├── __init__.py
│   └── pump_controller.py       # 泵站控制器（150行）
│
├── simulator/                   # 仿真器
│   ├── __init__.py
│   └── pump_station_twin.py     # 数字孪生（200行）
│
├── tests/                       # 测试
│   ├── __init__.py
│   ├── test_pump.py            # 单元测试
│   ├── test_controller.py      # 控制器测试
│   └── test_scenarios.py       # 在环测试（100工况）
│
└── outputs/                     # 输出
    ├── simulation_results.png   # 仿真结果图
    ├── performance_report.pdf   # 性能报告
    └── test_summary.txt         # 测试总结
```

**预计代码量**: 约1200行Python + 5000字文档

---

## ✅ 验收标准

### 代码质量
- [ ] 代码可运行，无语法错误
- [ ] 充分的中文注释（每个类、函数都有docstring）
- [ ] 遵循PEP 8编码规范
- [ ] 单元测试覆盖率 > 80%

### 功能完整性
- [ ] 水力模型正确（泵特性曲线）
- [ ] 控制器稳定（PID参数合理）
- [ ] 仿真可信（水量平衡守恒）
- [ ] 可视化清晰（至少3张图）

### 在环测试
- [ ] 至少10种测试工况
- [ ] 正常工况（5种）
- [ ] 扰动工况（3种）
- [ ] 故障工况（2种）
- [ ] 性能指标达标

### 文档质量
- [ ] README完整（5个章节）
- [ ] 标准引用准确（条文编号）
- [ ] 复用说明清晰
- [ ] 使用说明详细

### 智能化等级
- [ ] L2（单泵控制）认证
- [ ] L3（多泵协调）选项
- [ ] 评估报告生成

---

## 🧪 测试策略

### 单元测试（test_pump.py）
```python
def test_pump_characteristics():
    """测试泵特性曲线"""
    pump = Pump(Q_rated=1.2, H_rated=15, P_rated=80)
    
    # 测试额定工况
    H, eta, P = pump.compute_operating_point(Q=1.2)
    assert abs(H - 15) < 0.1
    assert eta > 0.70  # 效率>70%
    
    # 测试小流量
    H, eta, P = pump.compute_operating_point(Q=0.6)
    assert H > 15  # 小流量时扬程高
    
    # 测试大流量
    H, eta, P = pump.compute_operating_point(Q=1.5)
    assert H < 15  # 大流量时扬程低
```

### 集成测试（test_scenarios.py）
```python
def test_scenario_flow_step():
    """场景测试：流量阶跃"""
    twin = create_pump_station_twin()
    
    # 运行仿真
    results = twin.simulate(
        duration=3600,
        inflow=lambda t: 2.0 if t < 1800 else 4.0,
        demand=3.0
    )
    
    # 性能验证
    assert results['inlet_level_max'] < 5.0
    assert results['inlet_level_min'] > 2.0
    assert results['pump_switches'] < 10  # 启停次数<10
```

### 在环测试（100工况）
- 自动生成工况组合
- 批量运行仿真
- 性能统计分析
- 生成测试报告

---

## 📊 进度跟踪

### Week 1进度（当前）
- [x] 开发计划制定
- [x] 文件结构创建
- [ ] 泵模型开发
- [ ] 控制器开发
- [ ] 仿真器框架

### Week 2进度
- [ ] 数字孪生完善
- [ ] 单元测试
- [ ] 可视化开发

### Week 3进度
- [ ] 在环测试
- [ ] 文档编写
- [ ] 验收测试

---

## 🚀 后续Phase规划

### Phase 3（Week 9-16）
- 案例5：排涝闸站
- 案例6：多功能水闸
- Level 1总结

### Phase 4（Week 17-28）
- 案例7：串级渠道（复用案例1）
- 案例8：多级泵站（复用案例2）
- 案例9：树状管网
- 案例10：环状管网
- 案例11：雨水系统
- 案例12：污水泵站群

### Phase 5（Week 29-40）
- Level 3（6个案例）

### Phase 6（Week 41-52）
- Level 4（6个案例）

---

## 📝 开发规范

### 代码规范
```python
# 1. 文件头注释
"""
案例2：提水泵站智能化设计
模块名称：泵站控制器

功能：
- 进水池水位PID控制
- 多泵协调启停
- 轮换运行策略

作者：CHS-Books项目
日期：2025-10-31
"""

# 2. 类注释
class PumpStationController:
    """
    泵站控制器
    
    功能：
    1. 根据进水池水位决定开泵台数
    2. 实现轮换运行（均衡磨损）
    3. 避免频繁启停
    
    Parameters:
    -----------
    n_pumps : int
        泵的数量
    min_run_time : float
        最小运行时间（分钟）
    min_stop_time : float
        最小停机时间（分钟）
    
    Attributes:
    -----------
    pump_status : list
        各泵运行状态（0/1）
    run_time : list
        各泵累计运行时间
    """
    pass

# 3. 函数注释
def compute_operating_point(self, Q):
    """
    计算泵的工况点
    
    Parameters:
    -----------
    Q : float
        流量 [m³/s]
    
    Returns:
    --------
    H : float
        扬程 [m]
    eta : float
        效率 [-]
    P : float
        功率 [kW]
    
    Examples:
    ---------
    >>> pump = Pump(Q_rated=1.2, H_rated=15, P_rated=80)
    >>> H, eta, P = pump.compute_operating_point(Q=1.0)
    >>> print(f"扬程={H:.2f}m, 效率={eta:.2%}")
    """
    pass
```

### Git提交规范
```bash
# 提交格式
git commit -m "[案例2] 功能描述"

# 示例
git commit -m "[案例2] 添加泵模型和特性曲线"
git commit -m "[案例2] 完成控制器开发"
git commit -m "[案例2] 通过在环测试"
```

---

## 📞 联系与协作

**项目管理**:
- 进度跟踪：每周更新本文档
- 问题记录：GitHub Issues
- 代码审查：Pull Request

**技术支持**:
- 水力计算：参考第2本书案例10
- 控制算法：参考第1本书案例4、7
- 仿真方法：参考第3本书案例13

---

**开发启动日期**: 2025-10-31  
**预计完成日期**: Phase 2完成于2025-12-31（2个月）  
**当前状态**: 🔄 案例2开发中

---

## ✅ Checklist

- [x] 开发计划制定
- [x] 文件结构设计
- [ ] 开始编码
- [ ] 单元测试
- [ ] 在环测试
- [ ] 文档编写
- [ ] 代码审查
- [ ] 验收通过

**让我们开始吧！** 🚀
