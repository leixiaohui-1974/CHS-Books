# 运河仿真器 - 通用产品

## 产品概述

运河仿真器是一个完全基于配置文件驱动的通用水网仿真产品，支持多种仿真模式，无需修改代码即可适应不同的仿真需求。

## 核心特性

- **完全配置驱动** - 通过JSON/YAML配置文件定义仿真系统
- **多种仿真模式** - 支持纯仿真、数字孪生、控制仿真
- **通用组件系统** - 支持水库、闸门、泵站、渠段等多种组件
- **智能控制算法** - 内置PID、MPC等多种控制算法
- **扰动模拟** - 支持降雨、需求变化、设备故障等扰动
- **结果可视化** - 自动生成仿真结果图表和报告

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行仿真

```bash
# 使用简单配置
python canal_simulator.py config/simple_canal.json

# 使用复杂配置
python canal_simulator.py config/complex_network.json

# 查看帮助
python canal_simulator.py -h
```

### 3. 查看结果

仿真完成后，结果将保存在 `simulation_results/` 目录中。

## 配置文件结构

### 基本结构

```json
{
  "name": "仿真名称",
  "version": "版本号",
  "description": "仿真描述",
  "simulation": {
    "mode": "仿真模式",
    "time_step": "时间步长",
    "duration": "仿真时长"
  },
  "components": [
    // 系统组件定义
  ],
  "connections": [
    // 组件连接关系
  ],
  "agents": {
    // 智能体配置
  }
}
```

### 仿真模式

- `pure_simulation` - 纯仿真模式
- `digital_twin` - 数字孪生模式
- `control` - 控制仿真模式

### 组件类型

#### 水库 (reservoir)
```json
{
  "id": "reservoir_01",
  "type": "reservoir",
  "name": "水库名称",
  "parameters": {
    "capacity": 1000000,
    "max_level": 10.0,
    "min_level": 0.0
  },
  "initial_state": {
    "water_level": 8.0,
    "inflow": 5.0,
    "outflow": 0.0,
    "volume": 800000
  }
}
```

#### 闸门 (gate)
```json
{
  "id": "gate_01",
  "type": "gate",
  "name": "闸门名称",
  "parameters": {
    "width": 3.0,
    "max_opening": 2.0,
    "efficiency": 0.9
  },
  "initial_state": {
    "opening": 1.0,
    "upstream_level": 6.0,
    "downstream_level": 5.5,
    "setpoint": 6.0
  }
}
```

#### 渠段 (channel)
```json
{
  "id": "channel_01",
  "type": "channel",
  "name": "渠段名称",
  "parameters": {
    "length": 1000.0,
    "bottom_width": 5.0,
    "slope": 0.001
  },
  "initial_state": {
    "water_level": 6.0,
    "flow_rate": 5.0
  }
}
```

#### 泵站 (pump)
```json
{
  "id": "pump_01",
  "type": "pump",
  "name": "泵站名称",
  "parameters": {
    "max_flow": 10.0,
    "max_power": 100.0,
    "efficiency": 0.75
  },
  "initial_state": {
    "status": "on",
    "flow_rate": 6.0,
    "power_consumption": 60.0,
    "efficiency": 0.75,
    "setpoint": 6.0
  }
}
```

### 连接关系

```json
{
  "id": "connection_01",
  "type": "flow",
  "from": "source_component_id",
  "to": "target_component_id",
  "parameters": {
    "capacity": 20.0,
    "resistance": 0.001
  }
}
```

### 智能体配置

#### 扰动智能体
```json
{
  "disturbance": {
    "type": "disturbance_agent",
    "disturbances": [
      {
        "id": "rainfall_event",
        "type": "rainfall",
        "start_time": 20,
        "end_time": 50,
        "intensity": 15.0,
        "affected_components": ["reservoir_01"]
      }
    ]
  }
}
```

#### 控制智能体
```json
{
  "control": {
    "type": "control_agent",
    "controllers": [
      {
        "id": "water_level_controller",
        "type": "pid",
        "target_component": "main_channel",
        "controlled_components": ["control_gate"],
        "parameters": {
          "kp": 1.5,
          "ki": 0.2,
          "kd": 0.05,
          "setpoint": 6.0,
          "output_limits": [0.0, 2.0]
        }
      }
    ]
  }
}
```

#### 数字孪生智能体
```json
{
  "twin": {
    "type": "twin_agent",
    "synchronization_components": [
      "reservoir_01",
      "main_channel"
    ],
    "update_interval": 5.0,
    "noise_level": 0.01
  }
}
```

## 使用示例

### 简单运河仿真

```bash
python canal_simulator.py config/simple_canal.json
```

这个配置模拟一个简单的单渠段单闸门系统，包含：
- 上游水库
- 主渠段
- 控制闸门
- 下游渠段
- PID水位控制器
- 降雨和需求变化扰动

### 复杂水网仿真

```bash
python canal_simulator.py config/complex_network.json
```

这个配置模拟一个复杂的水网系统，包含：
- 两个水库
- 主渠段和分支渠段
- 多个闸门
- 泵站
- 多个PID控制器
- 数字孪生同步
- 多种扰动类型

## 自定义配置

### 创建新配置

1. 复制现有配置文件作为模板
2. 修改组件参数和初始状态
3. 调整仿真参数
4. 运行仿真验证配置

### 配置验证

系统会自动验证配置文件的完整性，包括：
- 必要字段检查
- 数据类型验证
- 组件引用检查
- 参数范围验证

## 输出结果

### 结果文件

仿真完成后，系统会生成：
- `simulation_results_YYYYMMDD_HHMMSS.json` - 详细仿真结果
- `canal_simulation.log` - 仿真日志

### 结果内容

结果文件包含：
- 时间序列数据
- 组件状态变化
- 控制输出
- 性能指标

## 故障排除

### 常见问题

1. **配置文件不存在**
   - 检查文件路径是否正确
   - 确认文件扩展名为 `.json` 或 `.yml`

2. **配置验证失败**
   - 检查必要字段是否完整
   - 验证数据类型是否正确
   - 确认组件引用是否存在

3. **仿真运行失败**
   - 检查日志文件获取详细错误信息
   - 验证组件参数是否合理
   - 确认时间步长设置是否合适

### 日志分析

查看 `canal_simulation.log` 文件获取详细的运行信息和错误诊断。

## 技术支持

- 查看 `docs/` 目录中的详细文档
- 参考 `examples/` 目录中的示例配置
- 运行 `python canal_simulator.py -h` 获取命令行帮助

## 版本信息

- 当前版本：v1.0.0
- 支持Python版本：3.8+
- 最后更新：2024年8月

---

**注意**：这是一个完全基于配置文件驱动的通用产品，用户无需修改任何代码即可适应不同的仿真需求。所有功能都通过配置文件进行定制。
