# 📑 Python代码速查手册

快速查找和使用本系列中的Python代码。

---

## 🎯 核心类库索引

### 1. 水力学计算引擎

#### HydraulicsEngine（综合水力学计算）
**位置**：`python-practice/project10/01_综合水力学工程平台_详细.md`

```python
class HydraulicsEngine:
    def __init__(self, g=9.81):
        self.g = g
    
    def manning_normal_depth(self, Q, b, m, n, S0):
        """Manning公式计算正常水深"""
        # 返回：h_n (m)
        
    def critical_depth(self, Q, b, m=0):
        """计算临界水深"""
        # 返回：h_c (m)
        
    def weir_discharge(self, H, b, weir_type='sharp'):
        """堰流泄流量计算"""
        # 返回：Q (m³/s)
        
    def pipe_headloss(self, Q, D, L, epsilon, nu=1e-6):
        """管道水头损失（Darcy-Weisbach + Colebrook-White）"""
        # 返回：h_f, f, flow_regime
        
    def hydraulic_jump(self, h1, v1, b):
        """水跃计算"""
        # 返回：{'h2', 'Fr1', 'Fr2', 'delta_E', 'L_jump'}
        
    def groundwater_thiem(self, Q, r1, r2, h1, h2):
        """Thiem公式（承压井）"""
        # 返回：K, s0
```

**快速示例**：
```python
engine = HydraulicsEngine()

# 计算正常水深
h_n = engine.manning_normal_depth(Q=100, b=10, m=2, n=0.025, S0=0.001)
print(f"正常水深: {h_n:.2f} m")

# 计算临界水深
h_c = engine.critical_depth(Q=100, b=10, m=2)
print(f"临界水深: {h_c:.2f} m")

# 判断流态
Fr = engine.g * h_n / (100 / ((10 + 2*h_n)*h_n))**2
if Fr < 1:
    print("缓流")
elif Fr > 1:
    print("急流")
else:
    print("临界流")
```

---

### 2. 水库优化调度

#### ReservoirDP（动态规划）
**位置**：`python-practice/project09/01_水库优化调度系统_详细.md`

```python
class ReservoirDP:
    def __init__(self, V_min, V_max, n_stages, n_states, eta=0.9, g=9.81):
        """初始化DP求解器"""
        
    def optimize(self, Q_in, Q_min, V_init, V_final=None, H_tail=80):
        """
        动态规划优化
        
        参数：
            Q_in: 入流序列 (m³/s)
            Q_min: 最小出流序列 (m³/s)
            V_init: 初始库容 (m³)
            V_final: 最终库容 (m³, 可选)
            H_tail: 尾水位 (m)
        
        返回：
            Q_opt: 最优出流序列
            V_opt: 库容过程
            P_total: 总发电量 (MW·day)
        """
```

#### CascadeReservoirGA（遗传算法）
**位置**：同上

```python
class CascadeReservoirGA:
    def __init__(self, n_reservoirs, pop_size=100, n_generations=200):
        """梯级水库遗传算法"""
        
    def optimize(self, Q_in, V_init, Q_bounds, params):
        """
        GA优化梯级水库调度
        
        返回：
            Q_opt: 各水库最优出流
            P_total: 总发电量
        """
```

**快速示例**：
```python
# 动态规划
reservoir = ReservoirDP(
    V_min=10e9, 
    V_max=39e9, 
    n_stages=12, 
    n_states=20
)

Q_in = np.array([8000, 9000, 12000, 18000, 25000, 30000,
                 35000, 32000, 28000, 22000, 15000, 10000])

Q_opt, V_opt, P_total = reservoir.optimize(
    Q_in=Q_in,
    Q_min=np.full(12, 5000),
    V_init=20e9
)

print(f"总发电量: {P_total:.2f} MW·day")
```

---

### 3. 地下水数值模拟

#### GroundwaterSimulation（2D稳定流）
**位置**：`groundwater/chapter09/01_地下水数值模拟高级专题_详细.md`

```python
class GroundwaterSimulation:
    def __init__(self, Lx, Ly, nx, ny, K):
        """
        初始化网格
        
        参数：
            Lx, Ly: 区域尺寸 (m)
            nx, ny: 网格数
            K: 渗透系数 (m/day)
        """
        
    def solve_steady_state(self, h_boundary, W=None, tol=1e-6, max_iter=10000):
        """
        稳定流求解（Gauss-Seidel迭代）
        
        参数：
            h_boundary: 边界水头函数
            W: 源汇项 (m/day)
            tol: 收敛容差
        
        返回：
            h: 水头分布 (ny, nx)
            n_iter: 迭代次数
        """
        
    def add_pumping_well(self, x_well, y_well, Q):
        """
        添加抽水井
        
        参数：
            x_well, y_well: 井位置 (m)
            Q: 抽水量 (m³/day, 负值表示抽水)
        
        返回：
            W: 源汇项数组
        """
        
    def calculate_flow(self):
        """
        计算流速场（Darcy定律）
        
        返回：
            vx, vy: x和y方向流速 (m/day)
        """
```

**快速示例**：
```python
# 创建模拟区域
gw = GroundwaterSimulation(Lx=1000, Ly=1000, nx=51, ny=51, K=10)

# 定义边界条件（西高东低）
def h_boundary(i, j):
    if j == 0:  # 西边界
        return 100
    elif j == gw.nx - 1:  # 东边界
        return 80
    elif i == 0 or i == gw.ny - 1:  # 南北边界
        return 100 - 20 * j / (gw.nx - 1)
    return None

# 添加抽水井
W = gw.add_pumping_well(300, 500, Q=-500)

# 求解
h, n_iter = gw.solve_steady_state(h_boundary, W=W)
print(f"迭代次数: {n_iter}, 最大水头: {h.max():.2f} m")

# 计算流速
vx, vy = gw.calculate_flow()
```

---

### 4. 非恒定流数值模拟

#### UnsteadyFlowSimulation（Saint-Venant方程）
**位置**：`hydraulics-advanced/chapter09/01_非恒定流数值方法_详细.md`

```python
class UnsteadyFlowSimulation:
    def __init__(self, L, nx, b, n, S0, g=9.81):
        """
        初始化非恒定流求解器
        
        参数：
            L: 河道长度 (m)
            nx: 空间网格数
            b: 河宽 (m)
            n: 曼宁系数
            S0: 河床坡度
        """
        
    def maccormack_step(self, dt, Q_upstream):
        """
        MacCormack格式单步（预测-校正）
        
        参数：
            dt: 时间步长 (s)
            Q_upstream: 上游边界流量 (m³/s)
        """
        
    def simulate(self, T, Q_upstream_func, CFL=0.5):
        """
        完整模拟
        
        参数：
            T: 总模拟时间 (s)
            Q_upstream_func: 上游流量函数 Q(t)
            CFL: CFL数（稳定性参数）
        
        返回：
            t_series: 时间序列
            h_series: 水深时间序列
            Q_series: 流量时间序列
        """
```

**快速示例**：
```python
# 初始化
ufs = UnsteadyFlowSimulation(L=10000, nx=101, b=50, n=0.03, S0=0.001)

# 初始条件（均匀流）
Q0 = 100
h0 = (Q0 * ufs.n / (ufs.b * np.sqrt(ufs.S0)))**(3/5)
ufs.initialize(h0, Q0)

# 上游洪水过程线（三角形）
def Q_upstream(t):
    T_rise = 3600  # 1小时
    T_fall = 7200  # 2小时
    Q_peak = 500
    
    if t < T_rise:
        return Q0 + (Q_peak - Q0) * t / T_rise
    elif t < T_rise + T_fall:
        return Q_peak - (Q_peak - Q0) * (t - T_rise) / T_fall
    else:
        return Q0

# 模拟
t_series, h_series, Q_series = ufs.simulate(
    T=4*3600,  # 4小时
    Q_upstream_func=Q_upstream,
    CFL=0.8
)

print(f"最大水深: {h_series.max():.2f} m")
print(f"最大流量: {Q_series.max():.2f} m³/s")
```

---

### 5. 水文频率分析

#### HydrologyComprehensive（P-III分布）
**位置**：`hydrology-exam-sprint/day30/01_冲刺模拟卷2_详细.md`

```python
class HydrologyComprehensive:
    @staticmethod
    def pearson_iii_parameters(data):
        """
        计算P-III分布参数
        
        参数：
            data: 水文系列数组
        
        返回：
            mean: 均值
            Cv: 变差系数
            Cs: 偏态系数
        """
        
    @staticmethod
    def pearson_iii_quantile(mean, Cv, Cs, p):
        """
        P-III分布分位数
        
        参数：
            mean: 均值
            Cv: 变差系数
            Cs: 偏态系数
            p: 频率（0-1）
        
        返回：
            quantile: 设计值
        """
        
    @staticmethod
    def correlation_extension(x, y):
        """
        相关分析插补延长
        
        参数：
            x, y: 同步期两站数据
        
        返回：
            slope: 斜率
            intercept: 截距
            r: 相关系数
        """
        
    @staticmethod
    def reservoir_regulation(inflow, demand, V_init, V_active, V_dead):
        """
        水库调节计算
        
        返回：
            storage: 库容过程
            release: 出库流量
            deficit: 缺水量
        """
```

**快速示例**：
```python
hc = HydrologyComprehensive()

# 年径流频率分析
annual_runoff = np.array([50, 45, 62, 38, 55, ...])  # 30年数据

# 计算参数
mean, Cv, Cs = hc.pearson_iii_parameters(annual_runoff)
print(f"均值: {mean:.2f}, Cv: {Cv:.3f}, Cs: {Cs:.3f}")

# 计算不同频率设计值
for p in [0.10, 0.25, 0.50, 0.75, 0.90]:
    Wp = hc.pearson_iii_quantile(mean, Cv, Cs, p)
    print(f"P={p*100:.0f}%: {Wp:.2f} 亿m³")
```

---

### 6. 优化算法

#### GlobalOptimization（全局优化）
**位置**：`numerical-methods/chapter09/01_优化方法进阶_详细.md`

```python
class GlobalOptimization:
    @staticmethod
    def simulated_annealing(f, bounds, T_init=100, T_min=0.01, alpha=0.95, L=100):
        """
        模拟退火算法
        
        参数：
            f: 目标函数
            bounds: 变量界 [(x1_min, x1_max), ...]
            T_init: 初始温度
            T_min: 最低温度
            alpha: 降温系数
            L: 每个温度的迭代次数
        
        返回：
            x_best: 最优解
            f_best: 最优值
            history: 优化历史
        """
        
    @staticmethod
    def genetic_algorithm(f, bounds, pop_size=100, n_gen=200, 
                         p_cross=0.8, p_mut=0.1):
        """
        遗传算法（实数编码）
        
        返回：
            x_best: 最优解
            f_best: 最优值
            history: 进化历史
        """
        
    @staticmethod
    def particle_swarm(f, bounds, n_particles=30, n_iter=200, 
                      w=0.7, c1=2.0, c2=2.0):
        """
        粒子群优化
        
        返回：
            g_best: 全局最优解
            g_best_fitness: 最优适应度
            history: 迭代历史
        """
```

**快速示例**：
```python
go = GlobalOptimization()

# 定义优化问题（Rosenbrock函数）
def rosenbrock(x):
    return sum(100 * (x[i+1] - x[i]**2)**2 + (1 - x[i])**2 
               for i in range(len(x) - 1))

bounds = [(-5, 5)] * 2

# 遗传算法
x_ga, f_ga, hist_ga = go.genetic_algorithm(
    rosenbrock, bounds, pop_size=50, n_gen=100
)
print(f"GA最优解: x = {x_ga}, f(x) = {f_ga:.6f}")

# 粒子群
x_pso, f_pso, hist_pso = go.particle_swarm(
    rosenbrock, bounds, n_particles=20, n_iter=100
)
print(f"PSO最优解: x = {x_pso}, f(x) = {f_pso:.6f}")

# 理论最优：x = [1, 1], f(x) = 0
```

---

### 7. 决策分析

#### DamTypeSelection（坝型选择）
**位置**：`water-structures/chapter09/01_水利枢纽优化设计_详细.md`

```python
class DamTypeSelection:
    def __init__(self):
        self.criteria = ['地质条件', '河谷形状', '坝高', 
                        '施工条件', '工期', '造价', '安全性']
        self.dam_types = ['重力坝', '拱坝', '土石坝']
    
    def ahp_analysis(self, judgment_matrix):
        """
        层次分析法（AHP）
        
        参数：
            judgment_matrix: 判断矩阵 (n x n)
        
        返回：
            weights: 权重向量
            CR: 一致性比率
        """
        
    def topsis_method(self, decision_matrix, weights, cost_criteria=[]):
        """
        TOPSIS法（逼近理想解排序）
        
        参数：
            decision_matrix: 决策矩阵 (n_alternatives, n_criteria)
            weights: 准则权重
            cost_criteria: 成本型指标索引列表
        
        返回：
            scores: 综合得分
            ranking: 排名
        """
```

**快速示例**：
```python
dts = DamTypeSelection()

# AHP权重计算
judgment_matrix = np.array([
    [1,   2,   1,   3,   2,   2,   1],
    [1/2, 1,   1/2, 2,   1,   1,   1/2],
    [1,   2,   1,   2,   1,   1,   1/2],
    # ... (7x7矩阵)
])

weights, CR = dts.ahp_analysis(judgment_matrix)
print(f"准则权重: {weights}")
print(f"一致性比率 CR = {CR:.4f} ({'通过' if CR < 0.10 else '未通过'})")

# TOPSIS排序
dam_scores = np.array([
    [80, 85, 70, 60, 65, 55, 85],  # 重力坝
    [90, 60, 65, 70, 60, 70, 80],  # 拱坝
    [60, 90, 80, 85, 90, 90, 70]   # 土石坝
])

scores, ranking = dts.topsis_method(
    dam_scores, weights, cost_criteria=[4, 5]  # 工期和造价是成本型
)

for i, dam_type in enumerate(dts.dam_types):
    print(f"{dam_type}: 得分{scores[i]:.4f}, 排名第{ranking[i]}")
```

---

## 🎨 可视化工具

### 通用绘图函数

```python
import matplotlib.pyplot as plt
import numpy as np

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 水深-流量关系曲线
def plot_rating_curve(h_range, Q_func):
    """绘制水位-流量关系曲线"""
    h = np.linspace(h_range[0], h_range[1], 100)
    Q = [Q_func(hi) for hi in h]
    
    plt.figure(figsize=(8, 6))
    plt.plot(Q, h, 'b-', linewidth=2)
    plt.xlabel('流量 Q (m³/s)', fontsize=11)
    plt.ylabel('水深 h (m)', fontsize=11)
    plt.title('水位-流量关系曲线', fontsize=12, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.show()

# 洪水过程线
def plot_hydrograph(t, Q, Q_peak=None):
    """绘制洪水过程线"""
    plt.figure(figsize=(10, 6))
    plt.plot(t, Q, 'b-', linewidth=2, label='洪水过程')
    
    if Q_peak:
        t_peak = t[np.argmax(Q)]
        plt.scatter([t_peak], [Q.max()], color='red', s=100, 
                   marker='*', zorder=5, label=f'洪峰 {Q.max():.0f} m³/s')
    
    plt.xlabel('时间 (h)', fontsize=11)
    plt.ylabel('流量 (m³/s)', fontsize=11)
    plt.title('洪水过程线', fontsize=12, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# 频率曲线
def plot_frequency_curve(data, theoretical_curve=None):
    """绘制经验频率曲线"""
    sorted_data = np.sort(data)[::-1]
    emp_freq = np.arange(1, len(sorted_data) + 1) / (len(sorted_data) + 1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(emp_freq * 100, sorted_data, 'bo', markersize=6, label='经验点据')
    
    if theoretical_curve:
        p_range, W_theory = theoretical_curve
        plt.plot(p_range * 100, W_theory, 'r-', linewidth=2, label='理论曲线')
    
    plt.xlabel('频率 P (%)', fontsize=11)
    plt.ylabel('年径流量 (亿m³)', fontsize=11)
    plt.title('频率曲线', fontsize=12, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.gca().invert_xaxis()
    plt.show()
```

---

## 📦 完整项目示例

### 示例1：水库防洪调度

```python
# 完整的水库防洪调度计算

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

class FloodControl:
    def __init__(self, Z_V_data, Q_max):
        """初始化水库参数"""
        self.Z_V_func = interp1d(Z_V_data[0], Z_V_data[1], 
                                kind='cubic', fill_value='extrapolate')
        self.V_Z_func = interp1d(Z_V_data[1], Z_V_data[0],
                                kind='cubic', fill_value='extrapolate')
        self.Q_max = Q_max
    
    def route_flood(self, Q_in_series, dt, Z_init):
        """洪水调节"""
        n = len(Q_in_series)
        Z = np.zeros(n)
        Q_out = np.zeros(n)
        V = np.zeros(n)
        
        Z[0] = Z_init
        V[0] = self.Z_V_func(Z_init)
        
        for i in range(n - 1):
            # 调度规则
            if Z[i] < 145:
                Q_out[i] = min(Q_in_series[i], 20000)
            elif Z[i] < 165:
                Q_out[i] = min(Q_in_series[i] * 0.8, 50000)
            else:
                Q_out[i] = min(Q_in_series[i], self.Q_max)
            
            # 水量平衡
            V[i+1] = V[i] + (Q_in_series[i] - Q_out[i]) * dt
            Z[i+1] = self.V_Z_func(V[i+1])
        
        return Z, Q_out, V

# 使用
Z_V_data = (
    np.array([145, 155, 165, 175]),  # 水位
    np.array([171, 218, 273, 393]) * 1e8  # 库容
)

fc = FloodControl(Z_V_data, Q_max=110000)

# 1954年型洪水
t = np.arange(0, 30*24, 1)  # 30天
Q_in = 20000 + 50000 * np.exp(-((t - 15*24)**2) / (2 * (5*24)**2))

Z, Q_out, V = fc.route_flood(Q_in, dt=3600, Z_init=145)

print(f"最大入库: {Q_in.max():.0f} m³/s")
print(f"最大出库: {Q_out.max():.0f} m³/s")
print(f"削峰率: {(1 - Q_out.max()/Q_in.max())*100:.1f}%")
print(f"最高水位: {Z.max():.2f} m")
```

---

## 🔍 常用函数速查

### 数值计算

```python
# 数值积分
from scipy.integrate import quad, simpson

# 定积分
result, error = quad(lambda x: x**2, 0, 1)

# Simpson法则
y = np.array([f(x) for x in x_values])
integral = simpson(y, x=x_values)

# ODE求解
from scipy.integrate import solve_ivp

sol = solve_ivp(lambda t, y: -y, [0, 10], [1])
```

### 优化求解

```python
from scipy.optimize import minimize, differential_evolution

# 无约束优化
result = minimize(objective_func, x0, method='BFGS')

# 有界优化
result = minimize(objective_func, x0, bounds=bounds, method='L-BFGS-B')

# 全局优化
result = differential_evolution(objective_func, bounds)
```

### 统计分析

```python
from scipy import stats

# t检验
t_stat, p_value = stats.ttest_ind(sample1, sample2)

# 相关分析
slope, intercept, r, p, stderr = stats.linregress(x, y)

# 非参数检验
statistic, p_value = stats.mannwhitneyu(x, y)
```

---

## 💾 保存与加载

### 保存结果

```python
import numpy as np
import pandas as pd

# NumPy数组
np.save('results.npy', data)
np.savetxt('results.txt', data, fmt='%.4f')

# Pandas DataFrame
df = pd.DataFrame({'x': x, 'y': y, 'z': z})
df.to_csv('results.csv', index=False)
df.to_excel('results.xlsx', index=False)
```

### 生成报告

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("report.pdf", pagesize=letter)
c.drawString(100, 750, "水力学计算报告")
c.drawString(100, 730, f"日期: {date}")
# ... 添加更多内容
c.save()
```

---

*Python代码速查手册 v1.0*  
*最后更新：2025-11-12*
