# Day 8：管道阻力与能量损失 ⭐⭐⭐⭐

**学习日期**：第8天（第二周开始）  
**学习时间**：2.5小时  
**难度等级**：⭐⭐⭐⭐（重要）  
**重要程度**：⭐⭐⭐⭐⭐（必考）

---

## 📋 今日学习目标

- ✅ 掌握雷诺数与流态判别
- ✅ 熟练计算沿程损失与局部损失
- ✅ 理解达西公式与摩阻系数
- ✅ 应用于管道水力计算

---

## 📚 核心考点

### 考点1：雷诺数与流态 ⭐⭐⭐⭐⭐

#### 雷诺数定义
```
Re = vd/ν = ρvd/μ
```

其中：
- `v` - 平均流速（m/s）
- `d` - 管径（m）
- `ν` - 运动粘滞系数（m²/s）
- `μ` - 动力粘滞系数（Pa·s）
- `ρ` - 密度（kg/m³）

#### 流态判别（圆管）
```
Re < 2000：层流
2000 < Re < 4000：过渡流
Re > 4000：紊流
```

---

### 考点2：沿程损失 ⭐⭐⭐⭐⭐

#### 达西公式
```
h_f = λ(L/d) × v²/(2g)
```

其中：
- `λ` - 沿程阻力系数
- `L` - 管长（m）
- `d` - 管径（m）

#### 摩阻系数λ

**层流（Re<2000）**：
```
λ = 64/Re
```

**紊流**：
- 光滑管：λ = f(Re)，用穆迪图或经验公式
- 粗糙管：λ = f(Re, Δ/d)
- 完全粗糙区：λ = f(Δ/d)

**经验公式（紊流光滑管）**：
```
λ = 0.3164/Re^0.25  (Re < 10^5, Blasius公式)
```

---

### 考点3：局部损失 ⭐⭐⭐⭐

#### 基本公式
```
h_j = ζ × v²/(2g)
```

其中：
- `ζ` - 局部阻力系数
- `v` - 局部断面流速

#### 典型局部损失系数

| 类型 | ζ值 |
|------|-----|
| 突然扩大 | ζ = (1 - A₁/A₂)² |
| 突然缩小 | ζ ≈ 0.5 |
| 90°弯头 | ζ ≈ 1.1-1.3 |
| 闸阀（全开）| ζ ≈ 0.2 |
| 管道进口 | ζ ≈ 0.5 |
| 管道出口 | ζ = 1.0 |

---

## 📝 精选例题（5题）

### 题目1：雷诺数与流态判别 ⭐⭐⭐

**题目**：
水在d=0.1m圆管中流动，流量Q=0.015m³/s，水温20℃（ν=1.0×10⁻⁶m²/s）。判断流态并计算沿程阻力系数λ。

**解答**：

**Step 1：计算流速**
```
v = Q/A = 0.015/(π×0.1²/4) = 1.91 m/s
```

**Step 2：计算雷诺数**
```
Re = vd/ν = 1.91×0.1/(1.0×10⁻⁶) = 191,000
```

**Step 3：判别流态**
```
Re = 191,000 > 4,000 → 紊流
```

**Step 4：计算λ（用Blasius公式）**
```
λ = 0.3164/Re^0.25 = 0.3164/191,000^0.25 = 0.0151
```

**答案**：紊流，λ = 0.0151

---

### 题目2：沿程损失计算 ⭐⭐⭐⭐

**题目**：
输水管道L=500m，d=0.2m，v=2m/s，λ=0.025。求沿程损失h_f。

**解答**：

**达西公式**
```
h_f = λ(L/d) × v²/(2g)
h_f = 0.025 × (500/0.2) × 2²/(2×9.8)
h_f = 0.025 × 2500 × 0.204
h_f = 12.75 m
```

**答案**：h_f = 12.75 m

---

### 题目3：局部损失计算 ⭐⭐⭐⭐

**题目**：
管道系统：进口（ζ=0.5）、2个90°弯头（ζ=1.2）、1个闸阀（ζ=0.2）、出口（ζ=1.0），流速v=3m/s。求总局部损失。

**解答**：

**各项局部损失**
```
进口：h_j1 = 0.5 × 3²/(2×9.8) = 0.230 m
弯头1：h_j2 = 1.2 × 3²/(2×9.8) = 0.551 m
弯头2：h_j3 = 1.2 × 3²/(2×9.8) = 0.551 m
闸阀：h_j4 = 0.2 × 3²/(2×9.8) = 0.092 m
出口：h_j5 = 1.0 × 3²/(2×9.8) = 0.459 m
```

**总局部损失**
```
Σh_j = 0.230 + 0.551 + 0.551 + 0.092 + 0.459 = 1.883 m
```

或直接计算：
```
Σζ = 0.5 + 1.2 + 1.2 + 0.2 + 1.0 = 4.1
Σh_j = 4.1 × 3²/(2×9.8) = 1.883 m
```

**答案**：Σh_j = 1.88 m

---

### 题目4：突然扩大损失 ⭐⭐⭐⭐

**题目**：
管道突然从d₁=0.1m扩大到d₂=0.2m，Q=0.02m³/s。求突然扩大损失h_j。

**解答**：

**Step 1：计算流速**
```
v₁ = Q/A₁ = 0.02/(π×0.1²/4) = 2.55 m/s
v₂ = Q/A₂ = 0.02/(π×0.2²/4) = 0.64 m/s
```

**Step 2：突然扩大阻力系数**
```
ζ = (1 - A₁/A₂)² = (1 - d₁²/d₂²)² = (1 - 0.25)² = 0.5625
```

**Step 3：损失计算（基于小管流速）**
```
h_j = ζ × v₁²/(2g) = 0.5625 × 2.55²/(2×9.8)
h_j = 0.5625 × 0.332 = 0.187 m
```

**或用波达公式**：
```
h_j = (v₁ - v₂)²/(2g) = (2.55 - 0.64)²/(2×9.8) = 0.186 m
```

**答案**：h_j = 0.187 m

---

### 题目5：管道总损失 ⭐⭐⭐⭐⭐

**题目**：
输水管道L=1000m，d=0.15m，λ=0.03，Q=0.03m³/s。沿途有：进口、3个弯头（ζ=1.1）、1个闸阀（ζ=0.2）、出口。求总水头损失h_w。

**解答**：

**Step 1：流速**
```
v = Q/A = 0.03/(π×0.15²/4) = 1.70 m/s
```

**Step 2：沿程损失**
```
h_f = λ(L/d) × v²/(2g) = 0.03 × (1000/0.15) × 1.70²/(2×9.8)
h_f = 0.03 × 6667 × 0.147 = 29.4 m
```

**Step 3：局部损失**
```
Σζ = 0.5(进口) + 3×1.1(弯头) + 0.2(阀) + 1.0(出口) = 5.0
Σh_j = 5.0 × 1.70²/(2×9.8) = 0.736 m
```

**Step 4：总损失**
```
h_w = h_f + Σh_j = 29.4 + 0.736 = 30.14 m
```

**答案**：h_w = 30.14 m

---

## 💻 Python代码：管道损失计算器

```python
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def reynolds_number(v, d, nu=1.0e-6):
    """计算雷诺数"""
    return v * d / nu

def friction_factor(Re, epsilon_d=0):
    """计算沿程阻力系数λ"""
    if Re < 2000:  # 层流
        return 64 / Re
    elif Re < 4000:  # 过渡流（简化为紊流）
        return 0.3164 / Re**0.25
    else:  # 紊流
        if epsilon_d == 0:  # 光滑管
            if Re < 1e5:
                return 0.3164 / Re**0.25  # Blasius
            else:
                return 0.0032 + 0.221/Re**0.237  # 近似公式
        else:  # 粗糙管（Colebrook-White简化）
            return 0.25 / (np.log10(epsilon_d/3.7 + 5.74/Re**0.9))**2

def head_loss_friction(lamda, L, d, v, g=9.8):
    """计算沿程损失"""
    return lamda * (L/d) * v**2 / (2*g)

def head_loss_local(zeta, v, g=9.8):
    """计算局部损失"""
    return zeta * v**2 / (2*g)

# 示例计算
print("="*60)
print("管道水头损失计算器")
print("="*60)

# 输入参数
L = 1000  # 管长(m)
d = 0.15  # 管径(m)
Q = 0.03  # 流量(m³/s)
lamda = 0.03  # 沿程阻力系数
nu = 1.0e-6  # 运动粘滞系数(m²/s)

# 局部损失系数
zeta_entrance = 0.5
zeta_bend = 1.1
n_bends = 3
zeta_valve = 0.2
zeta_exit = 1.0

# 计算
A = np.pi * d**2 / 4
v = Q / A
Re = reynolds_number(v, d, nu)

h_f = head_loss_friction(lamda, L, d, v)

zeta_total = zeta_entrance + n_bends*zeta_bend + zeta_valve + zeta_exit
h_j_total = head_loss_local(zeta_total, v)

h_w = h_f + h_j_total

print(f"管长 L = {L} m")
print(f"管径 d = {d} m")
print(f"流量 Q = {Q} m³/s")
print(f"流速 v = {v:.2f} m/s")
print(f"雷诺数 Re = {Re:.0f}")
print(f"流态: {'层流' if Re<2000 else '过渡流' if Re<4000 else '紊流'}")
print("-"*60)
print(f"沿程阻力系数 λ = {lamda}")
print(f"沿程损失 h_f = {h_f:.2f} m")
print(f"局部损失系数之和 Σζ = {zeta_total}")
print(f"局部损失 Σh_j = {h_j_total:.3f} m")
print(f"总水头损失 h_w = {h_w:.2f} m")
print("="*60)

# 可视化
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 左图：损失组成
labels = ['沿程损失', '局部损失']
sizes = [h_f, h_j_total]
colors = ['lightblue', 'lightcoral']
explode = (0.1, 0)

ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=90)
ax1.set_title(f'水头损失组成\n总损失 = {h_w:.2f} m', fontsize=14, fontweight='bold')

# 右图：沿管道损失分布
x = np.linspace(0, L, 100)
h_loss = lamda * (x/d) * v**2 / (2*9.8)

ax2.plot(x, h_loss, 'b-', linewidth=2, label='沿程损失累积')
ax2.axhline(y=h_f, color='r', linestyle='--', label=f'总沿程损失={h_f:.1f}m')
ax2.axhline(y=h_w, color='g', linestyle='--', label=f'总损失={h_w:.1f}m')
ax2.fill_between(x, 0, h_loss, alpha=0.3)
ax2.set_xlabel('管道长度 (m)', fontsize=12)
ax2.set_ylabel('累积损失 (m)', fontsize=12)
ax2.set_title('沿管道水头损失分布', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig('day08_pipe_losses.png', dpi=300, bbox_inches='tight')
plt.show()
```

---

## 📊 今日学习总结

### 核心公式

| 公式 | 说明 |
|------|------|
| Re = vd/ν | 雷诺数 |
| h_f = λ(L/d)×v²/(2g) | 沿程损失（达西公式）|
| h_j = ζ×v²/(2g) | 局部损失 |
| λ = 64/Re | 层流摩阻系数 |

### 重点提示

✅ **流态判别**：Re<2000层流，Re>4000紊流  
✅ **达西公式**：管道损失计算核心  
✅ **局部损失**：突然扩大损失最大  
✅ **总损失**：h_w = h_f + Σh_j

---

## 💪 今日任务

- [ ] 完成5道题（90分钟）
- [ ] 运行Python代码（30分钟）
- [ ] 熟记核心公式

---

## 💌 每日鼓励

> **第8天，进入第二周！**

管道阻力是水力学的重要内容，掌握它就能解决很多实际问题！💪

---

*Day 8 完成！下一站：Day 9* 🚀
