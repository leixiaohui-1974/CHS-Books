"""
案例20：二维明渠水流模拟 - 主程序

问题描述：
河道洪水漫滩，需要二维模拟水位和流速的空间分布。

方法：
- 二维浅水波方程
- 有限体积法（Lax-Friedrichs通量）
- 干湿处理

作者：CHS-Books项目
日期：2025-10-29
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


def print_separator(title="", width=80):
    """打印分隔线"""
    if title:
        print(f"\n{'='*width}")
        print(f"{title:^{width}}")
        print(f"{'='*width}")
    else:
        print(f"{'='*width}")


class ShallowWater2DSolver:
    """二维浅水波方程求解器

    求解方程组：
    ∂h/∂t + ∂(hu)/∂x + ∂(hv)/∂y = 0
    ∂(hu)/∂t + ∂(hu²+gh²/2)/∂x + ∂(huv)/∂y = S_x
    ∂(hv)/∂t + ∂(huv)/∂x + ∂(hv²+gh²/2)/∂y = S_y

    其中源项包括底坡和摩阻
    """

    def __init__(self, Lx, Ly, Nx, Ny, g=9.81):
        """
        Args:
            Lx: x方向长度 (m)
            Ly: y方向长度 (m)
            Nx: x方向网格数
            Ny: y方向网格数
            g: 重力加速度 (m/s²)
        """
        self.Lx = Lx
        self.Ly = Ly
        self.Nx = Nx
        self.Ny = Ny
        self.g = g

        # 网格间距
        self.dx = Lx / Nx
        self.dy = Ly / Ny

        # 网格坐标（单元中心）
        self.x = np.linspace(self.dx/2, Lx - self.dx/2, Nx)
        self.y = np.linspace(self.dy/2, Ly - self.dy/2, Ny)
        self.X, self.Y = np.meshgrid(self.x, self.y, indexing='ij')

        # 状态变量 (Nx, Ny)
        self.h = np.zeros((Nx, Ny))  # 水深
        self.u = np.zeros((Nx, Ny))  # x方向流速
        self.v = np.zeros((Nx, Ny))  # y方向流速

        # 地形和糙率
        self.z_b = np.zeros((Nx, Ny))  # 底高程
        self.n_manning = np.zeros((Nx, Ny))  # 曼宁糙率

        # 干湿临界值
        self.h_dry = 0.01  # m

        # 时间
        self.t = 0.0

    def set_topography(self, z_b, n_manning):
        """设置地形和糙率"""
        self.z_b = z_b.copy()
        self.n_manning = n_manning.copy()

    def set_initial_conditions(self, h, u, v):
        """设置初始条件"""
        self.h = h.copy()
        self.u = u.copy()
        self.v = v.copy()
        self.t = 0.0

    def compute_timestep(self, CFL=0.4):
        """根据CFL条件计算时间步长"""
        # 浅水波速
        c = np.sqrt(self.g * np.maximum(self.h, 1e-6))

        # 最大信号传播速度
        s_max_x = np.max(np.abs(self.u) + c)
        s_max_y = np.max(np.abs(self.v) + c)

        dt_x = CFL * self.dx / max(s_max_x, 1e-6)
        dt_y = CFL * self.dy / max(s_max_y, 1e-6)

        return min(dt_x, dt_y)

    def lax_friedrichs_flux_x(self, h_L, hu_L, hv_L, h_R, hu_R, hv_R):
        """计算x方向Lax-Friedrichs数值通量

        Args:
            左右状态的守恒变量

        Returns:
            F: 数值通量 [F_h, F_hu, F_hv]
        """
        # 计算流速
        eps = 1e-8
        u_L = hu_L / (h_L + eps) if h_L > self.h_dry else 0.0
        u_R = hu_R / (h_R + eps) if h_R > self.h_dry else 0.0

        # 物理通量
        F_L = np.array([
            hu_L,
            hu_L * u_L + 0.5 * self.g * h_L**2,
            hv_L * u_L
        ])

        F_R = np.array([
            hu_R,
            hu_R * u_R + 0.5 * self.g * h_R**2,
            hv_R * u_R
        ])

        # 波速估计
        c_L = np.sqrt(self.g * h_L) if h_L > self.h_dry else 0.0
        c_R = np.sqrt(self.g * h_R) if h_R > self.h_dry else 0.0
        alpha = max(abs(u_L) + c_L, abs(u_R) + c_R)

        # Lax-Friedrichs通量
        U_L = np.array([h_L, hu_L, hv_L])
        U_R = np.array([h_R, hu_R, hv_R])

        F = 0.5 * (F_L + F_R) - 0.5 * alpha * (U_R - U_L)

        return F

    def lax_friedrichs_flux_y(self, h_B, hu_B, hv_B, h_T, hu_T, hv_T):
        """计算y方向Lax-Friedrichs数值通量"""
        eps = 1e-8
        v_B = hv_B / (h_B + eps) if h_B > self.h_dry else 0.0
        v_T = hv_T / (h_T + eps) if h_T > self.h_dry else 0.0

        # 物理通量（G方向）
        G_B = np.array([
            hv_B,
            hu_B * v_B,
            hv_B * v_B + 0.5 * self.g * h_B**2
        ])

        G_T = np.array([
            hv_T,
            hu_T * v_T,
            hv_T * v_T + 0.5 * self.g * h_T**2
        ])

        # 波速
        c_B = np.sqrt(self.g * h_B) if h_B > self.h_dry else 0.0
        c_T = np.sqrt(self.g * h_T) if h_T > self.h_dry else 0.0
        alpha = max(abs(v_B) + c_B, abs(v_T) + c_T)

        U_B = np.array([h_B, hu_B, hv_B])
        U_T = np.array([h_T, hu_T, hv_T])

        G = 0.5 * (G_B + G_T) - 0.5 * alpha * (U_T - U_B)

        return G

    def compute_source_terms(self, i, j):
        """计算源项（底坡+摩阻）

        Returns:
            S: 源项 [0, S_x, S_y]
        """
        h = self.h[i, j]
        u = self.u[i, j]
        v = self.v[i, j]

        # 源项初始化
        S = np.zeros(3)

        if h < self.h_dry:
            return S

        # 底坡源项（中心差分）
        if i > 0 and i < self.Nx - 1:
            dz_dx = (self.z_b[i+1, j] - self.z_b[i-1, j]) / (2 * self.dx)
        else:
            dz_dx = 0.0

        if j > 0 and j < self.Ny - 1:
            dz_dy = (self.z_b[i, j+1] - self.z_b[i, j-1]) / (2 * self.dy)
        else:
            dz_dy = 0.0

        S_bx = -self.g * h * dz_dx
        S_by = -self.g * h * dz_dy

        # 摩阻源项（Manning公式）
        n = self.n_manning[i, j]
        vel_mag = np.sqrt(u**2 + v**2)

        if vel_mag > 1e-6:
            C_f = self.g * n**2 * vel_mag / (h**(4.0/3.0))
            S_fx = -C_f * u * h
            S_fy = -C_f * v * h
        else:
            S_fx = 0.0
            S_fy = 0.0

        S[1] = S_bx + S_fx
        S[2] = S_by + S_fy

        return S

    def apply_boundary_conditions(self, Q_inflow=0.0):
        """应用边界条件

        Args:
            Q_inflow: 上游总流量 (m³/s)
        """
        # 上游边界（x=0）：固定流量
        if Q_inflow > 0:
            # 计算湿单元
            wet_cells = np.sum(self.h[0, :] > self.h_dry)
            if wet_cells > 0:
                # 均匀分配流量
                q_per_cell = Q_inflow / (wet_cells * self.dy)  # 单宽流量
                for j in range(self.Ny):
                    if self.h[0, j] > self.h_dry:
                        self.u[0, j] = q_per_cell / self.h[0, j]

        # 下游边界（x=Lx）：自由出流
        self.h[-1, :] = self.h[-2, :]
        self.u[-1, :] = self.u[-2, :]
        self.v[-1, :] = self.v[-2, :]

        # 南北边界（y=0, y=Ly）：固壁
        self.v[:, 0] = 0.0
        self.v[:, -1] = 0.0

    def step(self, dt, Q_inflow=0.0):
        """前进一个时间步（显式欧拉）

        Args:
            dt: 时间步长 (s)
            Q_inflow: 上游流量 (m³/s)
        """
        # 守恒变量
        hu = self.h * self.u
        hv = self.h * self.v

        # 新时间层
        h_new = self.h.copy()
        hu_new = hu.copy()
        hv_new = hv.copy()

        # 内部单元更新
        for i in range(1, self.Nx - 1):
            for j in range(1, self.Ny - 1):

                # x方向通量
                F_E = self.lax_friedrichs_flux_x(
                    self.h[i, j], hu[i, j], hv[i, j],
                    self.h[i+1, j], hu[i+1, j], hv[i+1, j]
                )
                F_W = self.lax_friedrichs_flux_x(
                    self.h[i-1, j], hu[i-1, j], hv[i-1, j],
                    self.h[i, j], hu[i, j], hv[i, j]
                )

                # y方向通量
                G_N = self.lax_friedrichs_flux_y(
                    self.h[i, j], hu[i, j], hv[i, j],
                    self.h[i, j+1], hu[i, j+1], hv[i, j+1]
                )
                G_S = self.lax_friedrichs_flux_y(
                    self.h[i, j-1], hu[i, j-1], hv[i, j-1],
                    self.h[i, j], hu[i, j], hv[i, j]
                )

                # 源项
                S = self.compute_source_terms(i, j)

                # 更新
                dU_dt = -(F_E - F_W) / self.dx - (G_N - G_S) / self.dy + S

                h_new[i, j] = self.h[i, j] + dt * dU_dt[0]
                hu_new[i, j] = hu[i, j] + dt * dU_dt[1]
                hv_new[i, j] = hv[i, j] + dt * dU_dt[2]

        # 更新状态
        self.h = h_new
        hu = hu_new
        hv = hv_new

        # 从守恒变量恢复原始变量
        for i in range(self.Nx):
            for j in range(self.Ny):
                if self.h[i, j] > self.h_dry:
                    self.u[i, j] = hu[i, j] / self.h[i, j]
                    self.v[i, j] = hv[i, j] / self.h[i, j]
                else:
                    self.h[i, j] = 0.0
                    self.u[i, j] = 0.0
                    self.v[i, j] = 0.0

        # 边界条件
        self.apply_boundary_conditions(Q_inflow)

        self.t += dt

    def run(self, t_end, Q_inflow, dt_output=10.0, CFL=0.3):
        """运行模拟

        Args:
            t_end: 结束时间 (s)
            Q_inflow: 上游流量 (m³/s)
            dt_output: 输出时间间隔 (s)
            CFL: Courant数

        Returns:
            results: 包含时间历史的字典
        """
        times = [self.t]
        h_history = [self.h.copy()]
        u_history = [self.u.copy()]
        v_history = [self.v.copy()]

        t_next_output = dt_output
        step_count = 0

        print(f"开始模拟：t_end = {t_end}s")

        while self.t < t_end:
            # 计算时间步长
            dt = self.compute_timestep(CFL)
            dt = min(dt, t_end - self.t)

            # 前进一步
            self.step(dt, Q_inflow)
            step_count += 1

            # 输出
            if self.t >= t_next_output or abs(self.t - t_end) < 1e-6:
                times.append(self.t)
                h_history.append(self.h.copy())
                u_history.append(self.u.copy())
                v_history.append(self.v.copy())
                t_next_output += dt_output

                print(f"  t = {self.t:.1f}s, 步数 = {step_count}, dt = {dt:.3f}s")

        print(f"模拟完成！总步数 = {step_count}")

        return {
            'times': np.array(times),
            'h': np.array(h_history),
            'u': np.array(u_history),
            'v': np.array(v_history),
            'X': self.X,
            'Y': self.Y,
            'z_b': self.z_b
        }


def create_channel_floodplain_topography(X, Y):
    """创建河道+滩地地形

    Args:
        X, Y: 网格坐标

    Returns:
        z_b: 底高程
        n_manning: 糙率分布
    """
    Nx, Ny = X.shape

    # 参数
    channel_width = 50.0  # 主槽宽度
    floodplain_elevation = 2.0  # 滩地高程
    channel_center = Y[0, Ny//2]  # 主槽中心

    z_b = np.zeros_like(X)
    n_manning = np.zeros_like(X)

    for i in range(Nx):
        for j in range(Ny):
            y = Y[i, j]
            dist_from_center = abs(y - channel_center)

            if dist_from_center < channel_width / 2:
                # 主槽：底高程0，糙率低
                z_b[i, j] = 0.0
                n_manning[i, j] = 0.03
            else:
                # 滩地：底高程2m，糙率高
                z_b[i, j] = floodplain_elevation
                n_manning[i, j] = 0.05

    return z_b, n_manning


def main():
    """主函数"""
    print_separator("案例20：二维明渠水流模拟")

    # ==================== 参数设置 ====================
    Lx = 500.0  # m
    Ly = 200.0  # m
    Nx = 50  # 粗网格以加快计算
    Ny = 20

    print(f"\n计算域：")
    print(f"  长度 Lx = {Lx} m")
    print(f"  宽度 Ly = {Ly} m")
    print(f"  网格数 Nx × Ny = {Nx} × {Ny}")
    print(f"  网格间距 Δx × Δy = {Lx/Nx:.1f} m × {Ly/Ny:.1f} m")

    # ==================== 创建求解器 ====================
    solver = ShallowWater2DSolver(Lx, Ly, Nx, Ny)

    # ==================== 地形 ====================
    z_b, n_manning = create_channel_floodplain_topography(solver.X, solver.Y)
    solver.set_topography(z_b, n_manning)

    print(f"\n地形：")
    print(f"  主槽宽度：50 m")
    print(f"  主槽高程：0 m")
    print(f"  滩地高程：2 m")
    print(f"  主槽糙率：0.03")
    print(f"  滩地糙率：0.05")

    # ==================== 初始条件 ====================
    h0 = np.zeros((Nx, Ny))
    u0 = np.zeros((Nx, Ny))
    v0 = np.zeros((Nx, Ny))

    # 初始时主槽有水（3m深）
    for i in range(Nx):
        for j in range(Ny):
            y = solver.Y[i, j]
            if abs(y - Ly/2) < 25:  # 主槽中心±25m
                h0[i, j] = 3.0

    solver.set_initial_conditions(h0, u0, v0)

    print(f"\n初始条件：")
    print(f"  主槽水深：3.0 m")
    print(f"  滩地水深：0.0 m（干地）")

    # ==================== 运行模拟 ====================
    print_separator("开始模拟")

    Q_inflow = 500.0  # m³/s
    t_end = 600.0  # s (10分钟)

    print(f"\n边界条件：")
    print(f"  上游流量：{Q_inflow} m³/s")
    print(f"  下游：自由出流")
    print(f"  模拟时长：{t_end} s")

    results = solver.run(t_end, Q_inflow, dt_output=100.0, CFL=0.3)

    # ==================== 分析结果 ====================
    print_separator("结果分析")

    times = results['times']
    h_history = results['h']
    u_history = results['u']
    v_history = results['v']

    print(f"\n水深统计（最终时刻）：")
    h_final = h_history[-1]
    print(f"  最大水深：{np.max(h_final):.2f} m")
    print(f"  平均水深：{np.mean(h_final[h_final > 0.01]):.2f} m")
    print(f"  淹没面积：{np.sum(h_final > 0.01) * (Lx/Nx) * (Ly/Ny):.0f} m²")

    print(f"\n流速统计（最终时刻）：")
    u_final = u_history[-1]
    v_final = v_history[-1]
    vel_mag = np.sqrt(u_final**2 + v_final**2)
    print(f"  最大流速：{np.max(vel_mag):.2f} m/s")
    print(f"  主槽流速：{np.mean(vel_mag[10:40, 8:12]):.2f} m/s")

    # ==================== 绘图 ====================
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    X = results['X']
    Y = results['Y']

    # 选择几个时刻绘图
    plot_times_idx = [0, len(times)//3, 2*len(times)//3, -1]

    for idx, ti in enumerate(plot_times_idx[:4]):
        ax = fig.add_subplot(gs[idx//2, idx%2])
        h = h_history[ti]
        u = u_history[ti]
        v = v_history[ti]

        # 水深等值线
        levels = np.linspace(0, np.max(h), 15)
        cf = ax.contourf(X, Y, h, levels=levels, cmap='Blues')
        plt.colorbar(cf, ax=ax, label='水深 (m)')

        # 流速矢量（稀疏显示）
        skip = 3
        ax.quiver(X[::skip, ::skip], Y[::skip, ::skip],
                 u[::skip, ::skip], v[::skip, ::skip],
                 scale=20, width=0.003, alpha=0.7)

        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_title(f't = {times[ti]:.0f} s')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

    # 纵剖面（沿中心线）
    ax5 = fig.add_subplot(gs[2, 0])
    centerline_j = Ny // 2
    for ti in plot_times_idx:
        eta = h_history[ti][:, centerline_j] + z_b[:, centerline_j]
        ax5.plot(X[:, centerline_j], eta, label=f't={times[ti]:.0f}s')

    ax5.plot(X[:, centerline_j], z_b[:, centerline_j], 'k--', linewidth=2, label='河床')
    ax5.set_xlabel('x (m)')
    ax5.set_ylabel('水位 (m)')
    ax5.set_title('中心线水位纵剖面')
    ax5.legend()
    ax5.grid(True, alpha=0.3)

    # 横断面（x=250m处）
    ax6 = fig.add_subplot(gs[2, 1])
    cross_section_i = Nx // 2
    for ti in plot_times_idx:
        eta = h_history[ti][cross_section_i, :] + z_b[cross_section_i, :]
        ax6.plot(Y[cross_section_i, :], eta, label=f't={times[ti]:.0f}s')

    ax6.plot(Y[cross_section_i, :], z_b[cross_section_i, :], 'k--', linewidth=2, label='河床')
    ax6.set_xlabel('y (m)')
    ax6.set_ylabel('水位 (m)')
    ax6.set_title('x=250m处横断面')
    ax6.legend()
    ax6.grid(True, alpha=0.3)

    # 流速时间历程
    ax7 = fig.add_subplot(gs[2, 2])
    # 选择几个点
    points = [(10, Ny//2), (25, Ny//2), (40, Ny//2)]
    for i, j in points:
        vel_mag_history = np.sqrt(u_history[:, i, j]**2 + v_history[:, i, j]**2)
        ax7.plot(times, vel_mag_history, label=f'x={X[i,j]:.0f}m')

    ax7.set_xlabel('时间 (s)')
    ax7.set_ylabel('流速 (m/s)')
    ax7.set_title('中心线流速时程')
    ax7.legend()
    ax7.grid(True, alpha=0.3)

    plt.suptitle('二维明渠水流模拟 - 河道漫滩', fontsize=16, fontweight='bold')
    plt.savefig('case_20_2d_flow.png', dpi=150, bbox_inches='tight')
    print(f"\n图形已保存：case_20_2d_flow.png")

    print("\n" + "="*80)
    print("计算完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
