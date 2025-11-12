#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目5: Python面向对象编程

课程目标：
1. 掌握类的定义和实例化
2. 理解继承和多态
3. 学习封装和属性
4. 掌握特殊方法
5. 应用于水力建筑物类体系

工程案例：
设计一个水力建筑物类体系，包括堰、闸、溢洪道等

作者：Python编程实战教材组
日期：2025-11-12
"""

import math

# ============================================================
# 1. 基础类定义
# ============================================================

class HydraulicStructure:
    """水力建筑物基类"""
    
    # 类变量
    total_count = 0
    
    def __init__(self, name, location):
        """初始化"""
        self.name = name
        self.location = location
        HydraulicStructure.total_count += 1
        self.id = HydraulicStructure.total_count
    
    def get_info(self):
        """获取基本信息"""
        return f"{self.name} @ {self.location}"
    
    def __str__(self):
        """字符串表示"""
        return f"[{self.id}] {self.get_info()}"


# ============================================================
# 2. 继承
# ============================================================

class Weir(HydraulicStructure):
    """堰类"""
    
    def __init__(self, name, location, width, weir_type='sharp'):
        """初始化堰"""
        super().__init__(name, location)
        self.width = width
        self.weir_type = weir_type
    
    def calculate_flow(self, head):
        """计算过堰流量"""
        g = 9.81
        if self.weir_type == 'sharp':
            coefficient = 0.42
        elif self.weir_type == 'broad':
            coefficient = 0.385
        else:
            coefficient = 0.40
        
        flow = coefficient * self.width * math.sqrt(2 * g) * (head ** 1.5)
        return flow
    
    def get_info(self):
        """重写获取信息方法"""
        base_info = super().get_info()
        return f"{base_info}, 堰宽{self.width}m, 类型: {self.weir_type}"


class Gate(HydraulicStructure):
    """闸门类"""
    
    def __init__(self, name, location, width, height):
        """初始化闸门"""
        super().__init__(name, location)
        self.width = width
        self.height = height
        self.opening = 0  # 开度，初始为关闭
    
    def open_gate(self, opening):
        """开启闸门"""
        if 0 <= opening <= self.height:
            self.opening = opening
            return True
        return False
    
    def calculate_flow(self, head):
        """计算过闸流量"""
        if self.opening == 0:
            return 0
        
        g = 9.81
        coefficient = 0.6
        area = self.width * self.opening
        velocity = coefficient * math.sqrt(2 * g * head)
        flow = area * velocity
        return flow
    
    def get_info(self):
        """重写获取信息方法"""
        base_info = super().get_info()
        return f"{base_info}, 尺寸{self.width}×{self.height}m, 开度{self.opening}m"


class Spillway(HydraulicStructure):
    """溢洪道类"""
    
    def __init__(self, name, location, width, crest_elevation):
        """初始化溢洪道"""
        super().__init__(name, location)
        self.width = width
        self.crest_elevation = crest_elevation
    
    def calculate_flow(self, water_level):
        """计算溢洪道流量"""
        head = water_level - self.crest_elevation
        if head <= 0:
            return 0
        
        g = 9.81
        coefficient = 0.5
        flow = coefficient * self.width * math.sqrt(2 * g) * (head ** 1.5)
        return flow
    
    def get_info(self):
        """重写获取信息方法"""
        base_info = super().get_info()
        return f"{base_info}, 宽度{self.width}m, 堰顶高程{self.crest_elevation}m"


# ============================================================
# 3. 封装和属性
# ============================================================

class Reservoir:
    """水库类（演示封装和属性）"""
    
    def __init__(self, name, normal_level, flood_level, dead_level, storage_capacity):
        """初始化水库"""
        self.name = name
        self._normal_level = normal_level  # 正常蓄水位
        self._flood_level = flood_level    # 防洪限制水位
        self._dead_level = dead_level      # 死水位
        self._current_level = normal_level # 当前水位
        self.storage_capacity = storage_capacity
    
    @property
    def current_level(self):
        """水位属性（只读）"""
        return self._current_level
    
    @property
    def storage_utilization(self):
        """库容利用率"""
        useful_range = self._normal_level - self._dead_level
        if useful_range == 0:
            return 0
        current_range = self._current_level - self._dead_level
        return (current_range / useful_range) * 100
    
    def set_water_level(self, new_level):
        """设置水位（带验证）"""
        if new_level < self._dead_level:
            print(f"⚠ 警告: 水位低于死水位！")
            return False
        elif new_level > self._flood_level + 2:
            print(f"⚠ 警告: 水位过高，超过安全范围！")
            return False
        else:
            self._current_level = new_level
            return True
    
    def get_status(self):
        """获取水库状态"""
        if self._current_level < self._dead_level + 1:
            return "低水位"
        elif self._current_level < self._normal_level:
            return "正常"
        elif self._current_level < self._flood_level:
            return "汛限水位以上"
        else:
            return "超汛限"
    
    def __str__(self):
        return f"水库[{self.name}] 水位{self._current_level:.2f}m ({self.get_status()})"


# ============================================================
# 4. 特殊方法
# ============================================================

class Channel:
    """渠道类（演示特殊方法）"""
    
    def __init__(self, name, width, depth, length):
        self.name = name
        self.width = width
        self.depth = depth
        self.length = length
    
    def __str__(self):
        """字符串表示"""
        return f"渠道[{self.name}] {self.width}×{self.depth}×{self.length}m"
    
    def __repr__(self):
        """开发者表示"""
        return f"Channel('{self.name}', {self.width}, {self.depth}, {self.length})"
    
    def __len__(self):
        """长度"""
        return int(self.length)
    
    def __eq__(self, other):
        """相等比较"""
        if not isinstance(other, Channel):
            return False
        return (self.width == other.width and 
                self.depth == other.depth and 
                self.length == other.length)
    
    def __lt__(self, other):
        """小于比较（按长度）"""
        return self.length < other.length
    
    def __add__(self, other):
        """加法（串联渠道）"""
        if isinstance(other, Channel):
            new_name = f"{self.name}+{other.name}"
            # 假设宽度和深度相同
            new_length = self.length + other.length
            return Channel(new_name, self.width, self.depth, new_length)
        return NotImplemented
    
    def get_volume(self):
        """计算容积"""
        return self.width * self.depth * self.length


# ============================================================
# 5. 综合案例：水利工程管理系统
# ============================================================

class WaterProject:
    """水利工程项目类"""
    
    def __init__(self, project_name, location):
        self.project_name = project_name
        self.location = location
        self.structures = []
        self.reservoirs = []
    
    def add_structure(self, structure):
        """添加建筑物"""
        if isinstance(structure, HydraulicStructure):
            self.structures.append(structure)
            return True
        return False
    
    def add_reservoir(self, reservoir):
        """添加水库"""
        if isinstance(reservoir, Reservoir):
            self.reservoirs.append(reservoir)
            return True
        return False
    
    def list_structures(self):
        """列出所有建筑物"""
        print(f"\n{self.project_name} - 建筑物清单:")
        print("-" * 60)
        for s in self.structures:
            print(f"  {s}")
            print(f"    详情: {s.get_info()}")
    
    def list_reservoirs(self):
        """列出所有水库"""
        print(f"\n{self.project_name} - 水库清单:")
        print("-" * 60)
        for r in self.reservoirs:
            print(f"  {r}")
            print(f"    利用率: {r.storage_utilization:.1f}%")
    
    def simulate_flood(self, inflow):
        """模拟洪水调度"""
        print(f"\n模拟洪水调度 (入库流量: {inflow} m³/s):")
        print("-" * 60)
        
        # 计算所有溢洪道和闸门的泄流能力
        total_discharge = 0
        
        for s in self.structures:
            if isinstance(s, Spillway):
                # 假设水位
                flow = s.calculate_flow(155.0)
                total_discharge += flow
                print(f"  {s.name} 泄流: {flow:.2f} m³/s")
            
            elif isinstance(s, Gate):
                # 开启闸门
                s.open_gate(s.height * 0.8)  # 开启80%
                flow = s.calculate_flow(10.0)
                total_discharge += flow
                print(f"  {s.name} 泄流: {flow:.2f} m³/s")
        
        print(f"\n  总入库流量: {inflow:.2f} m³/s")
        print(f"  总出库流量: {total_discharge:.2f} m³/s")
        
        if total_discharge >= inflow:
            print(f"  ✓ 泄流能力足够")
        else:
            print(f"  ⚠ 泄流能力不足，需增加开度或启用备用设施")


def main():
    """主函数"""
    print("╔" + "═"*58 + "╗")
    print("║" + " "*13 + "Python面向对象编程应用" + " "*14 + "║")
    print("║" + " "*12 + "案例：水力建筑物类体系" + " "*13 + "║")
    print("╚" + "═"*58 + "╝")
    
    # 1. 基础类和继承
    print("\n" + "="*60)
    print("1. 类的继承和多态")
    print("="*60)
    
    weir = Weir("1号溢流堰", "三峡大坝", 50.0, 'broad')
    gate = Gate("1号泄洪闸", "三峡大坝", 8.0, 10.0)
    spillway = Spillway("主溢洪道", "三峡大坝", 120.0, 150.0)
    
    print(f"\n建筑物信息:")
    print(f"  {weir}")
    print(f"  {gate}")
    print(f"  {spillway}")
    
    # 测试流量计算
    print(f"\n流量计算（堰上水头2.0m）:")
    print(f"  {weir.name}: {weir.calculate_flow(2.0):.2f} m³/s")
    
    gate.open_gate(8.0)
    print(f"  {gate.name} (开度8m): {gate.calculate_flow(10.0):.2f} m³/s")
    print(f"  {spillway.name} (水位155m): {spillway.calculate_flow(155.0):.2f} m³/s")
    
    # 2. 封装和属性
    print("\n" + "="*60)
    print("2. 封装和属性")
    print("="*60)
    
    reservoir = Reservoir(
        name="三峡水库",
        normal_level=175.0,
        flood_level=145.0,
        dead_level=155.0,
        storage_capacity=39.3
    )
    
    print(f"\n{reservoir}")
    print(f"库容利用率: {reservoir.storage_utilization:.1f}%")
    
    print(f"\n调整水位:")
    reservoir.set_water_level(165.0)
    print(f"  {reservoir}")
    
    reservoir.set_water_level(172.0)
    print(f"  {reservoir}")
    
    # 3. 特殊方法
    print("\n" + "="*60)
    print("3. 特殊方法")
    print("="*60)
    
    ch1 = Channel("引水渠", 10.0, 3.0, 5000.0)
    ch2 = Channel("输水渠", 10.0, 3.0, 3000.0)
    ch3 = Channel("配水渠", 8.0, 2.5, 2000.0)
    
    print(f"\n渠道对象:")
    print(f"  {ch1}")
    print(f"  {ch2}")
    print(f"  {ch3}")
    
    print(f"\n特殊方法测试:")
    print(f"  len(ch1) = {len(ch1)} m")
    print(f"  ch1 == ch2: {ch1 == ch2}")
    print(f"  ch1 < ch2: {ch1 < ch2}")
    
    ch_total = ch1 + ch2
    print(f"  ch1 + ch2 = {ch_total}")
    print(f"    总长度: {len(ch_total)} m")
    print(f"    总容积: {ch_total.get_volume():.0f} m³")
    
    # 4. 综合案例
    print("\n" + "="*60)
    print("4. 综合案例：水利工程管理系统")
    print("="*60)
    
    project = WaterProject("三峡水利枢纽", "湖北省宜昌市")
    
    # 添加建筑物
    project.add_structure(weir)
    project.add_structure(gate)
    project.add_structure(spillway)
    
    # 添加更多闸门
    for i in range(2, 6):
        g = Gate(f"{i}号泄洪闸", "三峡大坝", 8.0, 10.0)
        project.add_structure(g)
    
    # 添加水库
    project.add_reservoir(reservoir)
    
    # 列出建筑物
    project.list_structures()
    
    # 列出水库
    project.list_reservoirs()
    
    # 模拟洪水调度
    project.simulate_flood(80000.0)
    
    # 总结
    print("\n" + "="*60)
    print("学习总结")
    print("="*60)
    print(f"""
本项目学习内容：
1. ✅ 类的定义和实例化
2. ✅ 继承和方法重写
3. ✅ super()调用父类方法
4. ✅ 封装（私有属性）
5. ✅ @property属性装饰器
6. ✅ 特殊方法（__str__, __repr__, __eq__, __lt__, __add__等）
7. ✅ 类的组合和聚合

面向对象设计：
• 建筑物基类 → 堰、闸、溢洪道
• 水库类（封装和属性）
• 渠道类（特殊方法）
• 工程项目类（组合）

最佳实践：
• 单一职责原则
• 开闭原则（对扩展开放）
• 使用继承实现代码复用
• 使用组合实现灵活设计
• 封装内部状态
• 提供清晰的接口

统计数据：
• 创建类数量: 7个
• 建筑物总数: {HydraulicStructure.total_count}个
• 代码行数: ~400行
    """)
    
    print("="*60)
    print("项目5完成！")
    print("="*60)


if __name__ == "__main__":
    main()
