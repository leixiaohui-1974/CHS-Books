"""
单池明渠系统模型

该模块实现了单池明渠的非线性水动力学模型和线性化模型。
"""

import numpy as np


class SinglePoolCanal:
    """
    单池明渠系统模型

    系统动态方程:
        A * dh/dt = Q_in - Q_out
        Q_out = C_d * W * a * sqrt(2*g*h)

    参数:
        length: 池长 (m)
        width: 池宽 (m)
        Cd: 流量系数 (无量纲)
        g: 重力加速度 (m/s²)
    """

    def __init__(self, length=1000.0, width=10.0, Cd=0.6, g=9.81):
        """
        初始化单池明渠模型

        Args:
            length: 池长 (m)
            width: 池宽 (m)
            Cd: 流量系数
            g: 重力加速度 (m/s²)
        """
        self.length = length
        self.width = width
        self.Cd = Cd
        self.g = g

        # 水面面积
        self.A = length * width

        # 状态变量: 水深 h (m)
        self.h = 2.0  # 初始水深

        # 最大闸门开度
        self.a_max = 2.0  # m

    def compute_outflow(self, h, a):
        """
        计算流出流量（非线性闸门方程）

        Args:
            h: 水深 (m)
            a: 闸门开度 (m)

        Returns:
            Q_out: 流出流量 (m³/s)
        """
        # 防止负数开根号
        h = max(h, 0.01)
        a = np.clip(a, 0, self.a_max)

        Q_out = self.Cd * self.width * a * np.sqrt(2 * self.g * h)
        return Q_out

    def dynamics(self, t, state, Q_in, a):
        """
        系统动态方程 (用于ODE求解器)

        Args:
            t: 时间 (s)
            state: 状态向量 [h]
            Q_in: 流入流量 (m³/s)
            a: 闸门开度 (m)

        Returns:
            dstate: 状态导数 [dh/dt]
        """
        h = state[0]
        Q_out = self.compute_outflow(h, a)

        dh_dt = (Q_in - Q_out) / self.A

        return np.array([dh_dt])

    def update(self, dt, Q_in, a):
        """
        使用欧拉法更新状态（简单仿真）

        Args:
            dt: 时间步长 (s)
            Q_in: 流入流量 (m³/s)
            a: 闸门开度 (m)

        Returns:
            h: 更新后的水深 (m)
        """
        dstate = self.dynamics(0, [self.h], Q_in, a)
        self.h = self.h + dstate[0] * dt

        # 限制水深为正值
        self.h = max(self.h, 0.01)

        return self.h

    def linearize(self, h0, Q0, a0):
        """
        在工作点附近线性化

        Args:
            h0: 工作点水深 (m)
            Q0: 工作点流量 (m³/s)
            a0: 工作点闸门开度 (m)

        Returns:
            K: 闸门增益 ∂Q/∂a (m²/s)
            tau: 时间常数 (s)
        """
        # K = ∂Q_out/∂a |_(h0,a0)
        K = self.Cd * self.width * np.sqrt(2 * self.g * h0)

        # 积分系统，无固有时间常数，但有等效时间常数
        # tau = A / K (近似)
        tau = self.A / K if K > 0 else float('inf')

        return K, tau

    def reset(self, h_init=2.0):
        """
        重置系统状态

        Args:
            h_init: 初始水深 (m)
        """
        self.h = h_init


class LinearizedModel:
    """
    线性化单池模型

    传递函数: G(s) = -K / (A*s)
    状态空间: dh/dt = -K/A * a + 1/A * Q_in
    """

    def __init__(self, A, K):
        """
        Args:
            A: 水面面积 (m²)
            K: 闸门增益 (m²/s)
        """
        self.A = A
        self.K = K
        self.h = 0.0  # 偏差变量

    def update(self, dt, dQ_in, da):
        """
        更新线性化模型

        Args:
            dt: 时间步长 (s)
            dQ_in: 流入流量偏差 (m³/s)
            da: 闸门开度偏差 (m)

        Returns:
            dh: 水深偏差 (m)
        """
        dh_dt = (dQ_in - self.K * da) / self.A
        self.h = self.h + dh_dt * dt
        return self.h

    def reset(self):
        """重置状态"""
        self.h = 0.0


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("单池明渠模型测试")
    print("=" * 60)

    # 创建模型
    canal = SinglePoolCanal(length=1000, width=10)

    print(f"\n系统参数:")
    print(f"  池长: {canal.length} m")
    print(f"  池宽: {canal.width} m")
    print(f"  水面面积: {canal.A} m²")
    print(f"  流量系数: {canal.Cd}")

    # 计算工作点
    h0 = 2.0
    a0 = 0.5
    Q0 = canal.compute_outflow(h0, a0)

    print(f"\n工作点:")
    print(f"  水深 h0 = {h0} m")
    print(f"  闸门开度 a0 = {a0} m")
    print(f"  流出流量 Q0 = {Q0:.3f} m³/s")

    # 线性化
    K, tau = canal.linearize(h0, Q0, a0)
    print(f"\n线性化参数:")
    print(f"  闸门增益 K = {K:.3f} m²/s")
    print(f"  等效时间常数 τ = {tau:.1f} s")

    # 简单仿真测试
    print(f"\n仿真测试: 阶跃响应")
    canal.reset(h_init=2.0)
    dt = 1.0
    Q_in = Q0  # 保持流入流量恒定
    a = 0.3    # 闸门开度减小，水位应上升

    print(f"  控制输入: a = {a} m (从 {a0} m 减小)")
    print(f"  时间   水深")
    print(f"  " + "-" * 30)

    for i in range(10):
        t = i * dt
        h = canal.update(dt, Q_in, a)
        print(f"  {t:5.0f}  {h:.4f} m")

    print("\n测试完成!")
