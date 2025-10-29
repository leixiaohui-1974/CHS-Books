"""
Saint-Venant方程组求解器

采用Lax显式差分格式求解一维明渠非恒定流

方程组：
  ∂A/∂t + ∂Q/∂x = 0                     (连续方程)
  ∂Q/∂t + ∂(Q²/A)/∂x + gA·∂h/∂x = gA(S₀-Sf)  (动量方程)

作者：CHS-Books项目
日期：2025-10-29
"""

import numpy as np
from typing import Dict, Tuple, Callable, Optional
import warnings


class SaintVenantSolver:
    """
    Saint-Venant方程组求解器（Lax显式格式）

    参数：
        L: 河道长度 (m)
        b: 河道宽度 (m)
        S0: 河床坡度
        n: 糙率系数
        dx: 空间步长 (m)
        dt: 时间步长 (s)，如果为None则自动计算
        g: 重力加速度 (m/s²)
    """

    def __init__(self, L: float, b: float, S0: float, n: float,
                 dx: float = 100.0, dt: Optional[float] = None,
                 g: float = 9.81):
        """初始化求解器"""
        self.L = L
        self.b = b
        self.S0 = S0
        self.n = n
        self.dx = dx
        self.g = g

        # 网格节点数
        self.nx = int(L / dx) + 1
        self.x = np.linspace(0, L, self.nx)

        # 时间步长（如果未指定则后续自动计算）
        self.dt = dt
        self.auto_dt = (dt is None)

        # 状态变量
        self.h = None  # 水深 (m)
        self.Q = None  # 流量 (m³/s)
        self.A = None  # 断面面积 (m²)
        self.v = None  # 流速 (m/s)

        # 时间
        self.t = 0.0
        self.time_step = 0

        # 边界条件函数
        self.bc_upstream = None
        self.bc_downstream = None

    def set_initial_conditions(self, h0: np.ndarray, Q0: np.ndarray):
        """设置初始条件

        Args:
            h0: 初始水深数组 (nx,)
            Q0: 初始流量数组 (nx,)
        """
        if len(h0) != self.nx or len(Q0) != self.nx:
            raise ValueError(f"初始条件数组长度必须为{self.nx}")

        self.h = h0.copy()
        self.Q = Q0.copy()
        self.A = self.b * self.h
        self.v = self.Q / self.A
        self.t = 0.0
        self.time_step = 0

    def set_uniform_initial(self, h0: float, Q0: float):
        """设置均匀初始条件

        Args:
            h0: 初始水深 (m)
            Q0: 初始流量 (m³/s)
        """
        h_array = np.full(self.nx, h0)
        Q_array = np.full(self.nx, Q0)
        self.set_initial_conditions(h_array, Q_array)

    def set_boundary_conditions(self,
                               upstream: Callable[[float], Tuple[float, float]],
                               downstream: Callable[[float], Tuple[float, float]]):
        """设置边界条件

        Args:
            upstream: 上游边界函数 f(t) -> (h, Q)
            downstream: 下游边界函数 f(t) -> (h, Q)
        """
        self.bc_upstream = upstream
        self.bc_downstream = downstream

    def compute_friction_slope(self, Q: float, A: float) -> float:
        """计算摩阻坡度

        Sf = n² * Q² / (A² * R^(4/3))

        对于矩形断面：R = A/P = bh/(b+2h)
        """
        if A < 1e-6:
            return 0.0

        h = A / self.b
        P = self.b + 2 * h
        R = A / P

        if R < 1e-6:
            return 0.0

        Sf = (self.n**2 * Q**2) / (A**2 * R**(4.0/3.0))
        return Sf

    def compute_wave_speed(self) -> Tuple[float, float]:
        """计算波速

        Returns:
            (c_max, c_mean): 最大波速和平均波速
        """
        c = np.sqrt(self.g * self.h)  # 重力波速度
        wave_speed_plus = np.abs(self.v) + c
        wave_speed_minus = np.abs(self.v) - c

        c_max = np.max(np.abs(np.concatenate([wave_speed_plus, wave_speed_minus])))
        c_mean = np.mean(wave_speed_plus)

        return c_max, c_mean

    def compute_timestep(self, cfl: float = 0.7) -> float:
        """根据CFL条件计算时间步长

        Args:
            cfl: Courant数，应<1，推荐0.5-0.8

        Returns:
            dt: 时间步长 (s)
        """
        c_max, _ = self.compute_wave_speed()
        dt = cfl * self.dx / c_max
        return dt

    def advance_lax(self):
        """Lax显式格式推进一个时间步

        连续方程：
          A[i]^(n+1) = (A[i-1]^n + A[i+1]^n)/2
                     - (dt/2dx)(Q[i+1]^n - Q[i-1]^n)

        动量方程：
          Q[i]^(n+1) = (Q[i-1]^n + Q[i+1]^n)/2
                     - (dt/2dx)(F[i+1]^n - F[i-1]^n)
                     + dt·S[i]^n

        其中 F = Q²/A + gA²/(2b), S = gA(S₀ - Sf)
        """
        # 自动计算时间步长
        if self.auto_dt:
            self.dt = self.compute_timestep(cfl=0.7)

        # 当前状态
        A_old = self.A.copy()
        Q_old = self.Q.copy()
        h_old = self.h.copy()

        # 计算新状态（内部节点）
        A_new = np.zeros_like(A_old)
        Q_new = np.zeros_like(Q_old)

        for i in range(1, self.nx - 1):
            # 连续方程
            A_new[i] = (A_old[i-1] + A_old[i+1]) / 2.0 \
                     - (self.dt / (2.0 * self.dx)) * (Q_old[i+1] - Q_old[i-1])

            # 动量方程的通量项 F = Q²/A + gA²/(2b)
            F_im1 = Q_old[i-1]**2 / A_old[i-1] + self.g * A_old[i-1]**2 / (2.0 * self.b)
            F_ip1 = Q_old[i+1]**2 / A_old[i+1] + self.g * A_old[i+1]**2 / (2.0 * self.b)

            # 源项 S = gA(S₀ - Sf)
            Sf_i = self.compute_friction_slope(Q_old[i], A_old[i])
            S_i = self.g * A_old[i] * (self.S0 - Sf_i)

            # 动量方程
            Q_new[i] = (Q_old[i-1] + Q_old[i+1]) / 2.0 \
                     - (self.dt / (2.0 * self.dx)) * (F_ip1 - F_im1) \
                     + self.dt * S_i

        # 边界条件
        if self.bc_upstream is not None:
            h_bc, Q_bc = self.bc_upstream(self.t + self.dt)
            A_new[0] = self.b * h_bc
            Q_new[0] = Q_bc
        else:
            # 默认：外推
            A_new[0] = 2 * A_new[1] - A_new[2]
            Q_new[0] = 2 * Q_new[1] - Q_new[2]

        if self.bc_downstream is not None:
            h_bc, Q_bc = self.bc_downstream(self.t + self.dt)
            A_new[-1] = self.b * h_bc
            Q_new[-1] = Q_bc
        else:
            # 默认：外推
            A_new[-1] = 2 * A_new[-2] - A_new[-3]
            Q_new[-1] = 2 * Q_new[-2] - Q_new[-3]

        # 更新状态
        self.A = A_new
        self.Q = Q_new
        self.h = self.A / self.b

        # 防止负值
        self.h = np.maximum(self.h, 0.01)
        self.A = self.b * self.h

        # 计算流速
        self.v = self.Q / self.A

        # 更新时间
        self.t += self.dt
        self.time_step += 1

    def run(self, t_end: float, dt_output: float = None,
            verbose: bool = False) -> Dict:
        """运行模拟

        Args:
            t_end: 结束时间 (s)
            dt_output: 输出时间间隔 (s)，None表示只输出最终结果
            verbose: 是否打印进度信息

        Returns:
            results: 包含时间序列结果的字典
        """
        if self.h is None:
            raise ValueError("必须先设置初始条件")

        if self.bc_upstream is None or self.bc_downstream is None:
            raise ValueError("必须先设置边界条件")

        # 初始化结果存储
        if dt_output is None:
            dt_output = t_end

        n_outputs = int(t_end / dt_output) + 1
        output_times = np.linspace(0, t_end, n_outputs)

        results = {
            'times': [],
            'h': [],
            'Q': [],
            'v': [],
            'x': self.x.copy()
        }

        # 保存初始状态
        results['times'].append(self.t)
        results['h'].append(self.h.copy())
        results['Q'].append(self.Q.copy())
        results['v'].append(self.v.copy())

        next_output_idx = 1

        # 时间推进
        while self.t < t_end:
            # 推进一步
            self.advance_lax()

            # 检查CFL条件
            if self.auto_dt:
                c_max, _ = self.compute_wave_speed()
                courant = (np.max(np.abs(self.v)) + c_max) * self.dt / self.dx
                if courant > 1.0:
                    warnings.warn(f"CFL条件违背: Courant = {courant:.3f} > 1.0")

            # 输出
            if next_output_idx < len(output_times):
                if self.t >= output_times[next_output_idx]:
                    results['times'].append(self.t)
                    results['h'].append(self.h.copy())
                    results['Q'].append(self.Q.copy())
                    results['v'].append(self.v.copy())
                    next_output_idx += 1

                    if verbose:
                        print(f"t = {self.t:8.1f} s, "
                              f"Q_up = {self.Q[0]:8.2f} m³/s, "
                              f"h_max = {np.max(self.h):6.3f} m, "
                              f"dt = {self.dt:6.3f} s")

        # 确保最终时刻被包含
        if self.t > results['times'][-1]:
            results['times'].append(self.t)
            results['h'].append(self.h.copy())
            results['Q'].append(self.Q.copy())
            results['v'].append(self.v.copy())

        # 转换为numpy数组
        results['times'] = np.array(results['times'])
        results['h'] = np.array(results['h'])
        results['Q'] = np.array(results['Q'])
        results['v'] = np.array(results['v'])

        return results

    def compute_froude_number(self) -> np.ndarray:
        """计算Froude数"""
        Fr = self.v / np.sqrt(self.g * self.h)
        return Fr

    def get_state(self) -> Dict:
        """获取当前状态"""
        return {
            't': self.t,
            'x': self.x.copy(),
            'h': self.h.copy(),
            'Q': self.Q.copy(),
            'v': self.v.copy(),
            'A': self.A.copy(),
            'Fr': self.compute_froude_number()
        }

    def __repr__(self):
        return (f"SaintVenantSolver(L={self.L}m, b={self.b}m, "
                f"nx={self.nx}, dx={self.dx}m)")
