# Day 2：曲面总压力与浮力 ⭐⭐⭐⭐

**学习日期**：第2天  
**学习时间**：2.5小时  
**难度等级**：⭐⭐⭐⭐（中等）  
**重要程度**：⭐⭐⭐⭐⭐（必考）

---

## 📋 今日学习目标

- ✅ 掌握曲面总压力计算方法（压力体法）
- ✅ 熟练计算浮力与浮心
- ✅ 理解浮体稳定性判别方法
- ✅ 应用于工程实际问题

---

## 📚 核心考点

### 考点1：曲面总压力（压力体法）⭐⭐⭐⭐⭐

#### 基本原理
曲面总压力分解为水平分力和垂直分力：
```
P_x = γh̄A_x  （水平分力）
P_z = γV     （垂直分力）
P = √(P_x² + P_z²)  （合力）
```

其中：
- `P_x` - 水平分力，等于曲面在垂直平面上投影面积的总压力
- `P_z` - 垂直分力，等于压力体的重量
- `V` - 压力体体积
- `γ` - 液体容重

#### 压力体确定方法
1. **实压力体**：液体在受压面上方 → P_z向下
2. **虚压力体**：液体在受压面下方 → P_z向上

---

### 考点2：浮力计算 ⭐⭐⭐⭐⭐

#### 阿基米德原理
```
F_b = γV_排
```
- `F_b` - 浮力（N）
- `γ` - 液体容重（N/m³）
- `V_排` - 物体排开液体的体积（m³）

#### 浮心
浮心是排开液体体积的形心，即浮力作用点。

---

### 考点3：浮体稳定性 ⭐⭐⭐⭐

#### 稳定性判别
- **稳定**：重心G在浮心C下方，或定倾中心M在重心G上方
- **不稳定**：M在G下方
- **临界**：M与G重合

#### 定倾中心高度
```
h_M = I_c/V_排 - GC
```
- `h_M > 0` → 稳定
- `h_M < 0` → 不稳定

---

## 📝 精选例题（5题）

### 题目1：圆柱形闸门曲面压力 ⭐⭐⭐⭐

**题目**：
半径r=2m的1/4圆柱形闸门AB，宽度b=3m，A点在水面，B点在水平底部。求作用在闸门上的总压力P及其与水平面的夹角α。

**解答**：

**水平分力P_x**：
```
投影面积：A_x = r × b = 2 × 3 = 6 m²
形心深度：h̄ = r/2 = 1 m
P_x = γh̄A_x = 9800 × 1 × 6 = 58,800 N = 58.8 kN
```

**垂直分力P_z**：
```
压力体体积：V = (1/4)πr² × b = (1/4)π × 4 × 3 = 9.42 m³
P_z = γV = 9800 × 9.42 = 92,316 N = 92.3 kN
```

**总压力**：
```
P = √(P_x² + P_z²) = √(58.8² + 92.3²) = 109.5 kN
tanα = P_z/P_x = 92.3/58.8 = 1.57
α = 57.5°
```

**答案**：P = 109.5 kN，α = 57.5°

---

### 题目2：水下半球形容器 ⭐⭐⭐⭐

**题目**：
半球形容器，半径R=1.5m，开口向下，顶部距水面h=2m。求容器受到的总压力。

**解答**：

**水平分力**：P_x = 0（对称抵消）

**垂直分力**：
```
虚压力体 = 圆柱体 - 半球体
V_cylinder = πR²(h+R) = π × 1.5² × 3.5 = 24.74 m³
V_hemisphere = (2/3)πR³ = (2/3)π × 1.5³ = 7.07 m³
V = 24.74 - 7.07 = 17.67 m³
P_z = γV = 9800 × 17.67 = 173,166 N = 173.2 kN（向上）
```

**答案**：P = 173.2 kN（向上）

---

### 题目3：木块浮力计算 ⭐⭐⭐

**题目**：
长方体木块，长a=2m，宽b=1m，高h=0.5m，密度ρ_wood=600kg/m³，漂浮在水面上。求：
1. 浮力F_b
2. 吃水深度h_d

**解答**：

**1. 浮力（平衡状态）**：
```
重力：G = ρ_wood × g × V = 600 × 9.8 × (2×1×0.5) = 5,880 N
浮力：F_b = G = 5,880 N = 5.88 kN
```

**2. 吃水深度**：
```
F_b = ρ_water × g × V_排
5,880 = 1000 × 9.8 × (2×1×h_d)
h_d = 5,880/(19,600) = 0.3 m = 30 cm
```

**答案**：F_b = 5.88 kN，h_d = 0.3 m

---

### 题目4：浮标稳定性 ⭐⭐⭐⭐⭐

**题目**：
圆柱形浮标，直径D=0.6m，总高H=1.2m，重心距底部h_G=0.4m，吃水深度h_d=0.8m。判断稳定性。

**解答**：

**浮心位置**（排开液体体积的形心）：
```
C距底部：h_C = h_d/2 = 0.4 m
```

**定倾中心高度**：
```
水线面惯性矩：I_c = πD⁴/64 = π×0.6⁴/64 = 0.00636 m⁴
排水体积：V_排 = π×(D/2)²×h_d = π×0.3²×0.8 = 0.226 m³
GC = h_G - h_C = 0.4 - 0.4 = 0
h_M = I_c/V_排 - GC = 0.00636/0.226 - 0 = 0.028 m > 0
```

**答案**：h_M = 2.8 cm > 0，浮标稳定

---

### 题目5：潜水艇浮沉 ⭐⭐⭐⭐

**题目**：
潜水艇总体积V=1000m³，海水密度ρ=1025kg/m³。要使潜水艇从水面下沉，需要注入多少海水？（已知潜艇自重G_0=9,000kN）

**解答**：

**水面漂浮状态**：
```
浮力 = 重力
F_b = G_0
ρgV = G_0
G_0 = 1025 × 9.8 × 1000 = 10,045,000 N = 10,045 kN
```

但题目说自重G_0=9,000kN，说明有部分体积露出水面。

**完全下潜所需总重**：
```
完全潜入时浮力：F_b = 1025 × 9.8 × 1000 = 10,045 kN
需要总重：G_total = F_b = 10,045 kN
需注入海水重量：ΔG = 10,045 - 9,000 = 1,045 kN
注入海水体积：V_water = ΔG/(ρg) = 1,045,000/(1025×9.8) = 104 m³
```

**答案**：需注入104m³海水

---

## 💻 Python代码：浮体稳定性分析

```python
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def floating_body_stability(D, H, h_G, h_d, rho_body, rho_water=1000):
    """
    分析圆柱形浮体稳定性
    
    参数:
        D: 直径 (m)
        H: 总高 (m)
        h_G: 重心距底部高度 (m)
        h_d: 吃水深度 (m)
        rho_body: 物体平均密度 (kg/m³)
        rho_water: 水密度 (kg/m³)
    """
    g = 9.8
    
    # 浮心位置（排水体积形心）
    h_C = h_d / 2
    
    # 水线面惯性矩
    I_c = np.pi * D**4 / 64
    
    # 排水体积
    V_disp = np.pi * (D/2)**2 * h_d
    
    # 定倾中心高度
    GC = h_G - h_C
    h_M = I_c / V_disp - GC
    
    # 判断稳定性
    if h_M > 0:
        stability = "稳定"
    elif h_M < 0:
        stability = "不稳定"
    else:
        stability = "临界"
    
    # 计算重量和浮力验证
    V_total = np.pi * (D/2)**2 * H
    Weight = rho_body * g * V_total
    Buoyancy = rho_water * g * V_disp
    
    print("="*60)
    print("圆柱形浮体稳定性分析")
    print("="*60)
    print(f"浮体直径 D = {D} m")
    print(f"浮体总高 H = {H} m")
    print(f"重心高度 h_G = {h_G} m（距底部）")
    print(f"吃水深度 h_d = {h_d} m")
    print(f"物体密度 ρ_body = {rho_body} kg/m³")
    print("-"*60)
    print(f"浮心高度 h_C = {h_C:.3f} m（距底部）")
    print(f"水线面惯性矩 I_c = {I_c:.6f} m⁴")
    print(f"排水体积 V_排 = {V_disp:.3f} m³")
    print(f"GC距离 = {GC:.3f} m")
    print(f"定倾中心高度 h_M = {h_M:.4f} m")
    print("-"*60)
    print(f"重量 W = {Weight/1000:.2f} kN")
    print(f"浮力 F_b = {Buoyancy/1000:.2f} kN")
    print(f"稳定性判别: {stability} ({'h_M>0' if h_M>0 else 'h_M<0' if h_M<0 else 'h_M=0'})")
    print("="*60)
    
    return h_M, stability

# 示例：题目4
D = 0.6      # 直径 (m)
H = 1.2      # 总高 (m)
h_G = 0.4    # 重心高度 (m)
h_d = 0.8    # 吃水深度 (m)
rho_body = 600  # 平均密度 (kg/m³)

h_M, stability = floating_body_stability(D, H, h_G, h_d, rho_body)

# 可视化
fig, ax = plt.subplots(figsize=(8, 10))

# 绘制浮体
body_rect = plt.Rectangle((0.5-D/2, 0), D, H, 
                          fill=True, facecolor='lightblue', 
                          edgecolor='blue', linewidth=2)
ax.add_patch(body_rect)

# 水线
ax.plot([0, 1], [h_d, h_d], 'c-', linewidth=3, label='水线')
ax.fill_between([0, 1], 0, h_d, alpha=0.2, color='cyan')

# 重心G
ax.plot(0.5, h_G, 'ro', markersize=15, label=f'重心G (h={h_G}m)')
ax.text(0.52, h_G, 'G', fontsize=14, fontweight='bold')

# 浮心C
h_C = h_d / 2
ax.plot(0.5, h_C, 'go', markersize=15, label=f'浮心C (h={h_C}m)')
ax.text(0.52, h_C, 'C', fontsize=14, fontweight='bold')

# 定倾中心M
h_M_abs = h_G + h_M
ax.plot(0.5, h_M_abs, 'mo', markersize=15, label=f'定倾中心M (h={h_M_abs:.3f}m)')
ax.text(0.52, h_M_abs, 'M', fontsize=14, fontweight='bold')

# 连线
ax.plot([0.5, 0.5], [h_C, h_G], 'k--', linewidth=1)
ax.plot([0.5, 0.5], [h_G, h_M_abs], 'k--', linewidth=1)

# 标注
ax.text(0.1, h_d/2, f'吃水深度\nh_d={h_d}m', fontsize=11, ha='center')
ax.text(0.9, H/2, f'总高\nH={H}m', fontsize=11, ha='center')
ax.text(0.5, -0.1, f'直径D={D}m', fontsize=11, ha='center')

# 稳定性判断文字
stability_text = f"稳定性: {stability}\nh_M = {h_M:.4f} m"
color = 'green' if h_M > 0 else 'red'
ax.text(0.5, H+0.15, stability_text, fontsize=14, fontweight='bold',
        ha='center', bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))

ax.set_xlim(0, 1)
ax.set_ylim(-0.2, H+0.3)
ax.set_xlabel('水平距离 (m)', fontsize=12)
ax.set_ylabel('高度 (m)', fontsize=12)
ax.set_title('圆柱形浮体稳定性分析', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10, loc='upper right')
ax.set_aspect('equal')

plt.tight_layout()
plt.savefig('day02_floating_stability.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

## 📊 今日学习总结

### 核心公式

| 公式 | 说明 |
|------|------|
| P_x = γh̄A_x | 曲面水平分力 |
| P_z = γV | 曲面垂直分力 |
| F_b = γV_排 | 浮力（阿基米德原理）|
| h_M = I_c/V_排 - GC | 定倾中心高度 |

### 重点总结

✅ **曲面压力体法**：
- 水平分力 = 垂直投影面压力
- 垂直分力 = 压力体重量
- 实压力体向下，虚压力体向上

✅ **浮力计算**：
- 浮力 = 排水重量
- 浮心 = 排水体积形心
- 浮力向上作用于浮心

✅ **稳定性判别**：
- h_M > 0 → 稳定
- 重心越低越稳定
- 水线面惯性矩越大越稳定

---

## 💪 今日任务

- [ ] 理论复习（30分钟）
- [ ] 完成5道题（60分钟）
- [ ] 运行代码（30分钟）
- [ ] 总结笔记（30分钟）

---

## 🎯 明日预告：Day 3 - 闸门启闭力

---

## 💌 每日鼓励

> **第2天，稳扎稳打！**

曲面压力和浮力是难点，但你坚持下来了！

**记住**：难度提升是进步的标志，继续加油！💪

---

*Day 2 完成！下一站：Day 3* 🚀
