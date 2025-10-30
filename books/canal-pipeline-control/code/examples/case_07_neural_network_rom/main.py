#!/usr/bin/env python3
"""
案例7：神经网络降阶模型
Neural Network Reduced Order Model

实现：
1. Autoencoder降阶模型
2. Physics-Informed Neural Network (PINN)
3. 简化的Neural Operator
4. 与传统方法（POD）的对比

作者：Claude
日期：2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy import integrate
import time
import warnings
warnings.filterwarnings('ignore')

# PyTorch imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    TORCH_AVAILABLE = True
except ImportError:
    print("警告：未安装PyTorch，将使用简化的NumPy实现")
    TORCH_AVAILABLE = False

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ==================== 渠道系统仿真 ====================

class CanalReach:
    """
    渠段模型：Saint-Venant方程求解器
    使用显式有限差分方法
    """
    def __init__(self, L=1000, B=5, i0=0.001, n=0.025, N=51):
        self.L = L      # 渠道长度 (m)
        self.B = B      # 渠道宽度 (m)
        self.i0 = i0    # 底坡
        self.n = n      # 糙率
        self.N = N      # 节点数

        self.dx = L / (N - 1)
        self.x = np.linspace(0, L, N)

        # 初始化状态
        self.h = np.ones(N) * 1.0  # 初始水深1m
        self.Q = np.ones(N) * 5.0  # 初始流量5m³/s

        # 侧向流量
        self.q_lat = np.zeros(N)

        self.g = 9.81

    def set_state(self, h, Q):
        """设置状态"""
        self.h = h.copy()
        self.Q = Q.copy()

    def get_state(self):
        """获取状态"""
        return self.h.copy(), self.Q.copy()

    def manning_flow(self, h):
        """Manning公式计算流量"""
        A = self.B * h
        P = self.B + 2 * h
        R = A / (P + 1e-6)
        Q = (1/self.n) * A * R**(2/3) * np.sqrt(self.i0)
        return Q

    def friction_slope(self, Q, h):
        """计算摩阻坡度"""
        A = self.B * h
        P = self.B + 2 * h
        R = A / (P + 1e-6)
        if R > 1e-6:
            Sf = (self.n * Q / A)*2 / R**(4/3)
        else:
            Sf = self.i0
        return Sf

    def step(self, dt, Q_in=None, Q_out=None):
        """
        时间步进
        dt: 时间步长
        Q_in: 上游入流
        Q_out: 下游出流
        """
        h, Q = self.h.copy(), self.Q.copy()
        h_new, Q_new = h.copy(), Q.copy()

        # 上游边界条件
        if Q_in is not None:
            Q_new[0] = Q_in

        # 内部节点更新
        for i in range(1, self.N-1):
            # 连续性方程
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)
            h_new[i] = h[i] - dt * (dQ_dx / self.B - self.q_lat[i])

            # 确保水位为正
            h_new[i] = np.clip(h_new[i], 0.1, 10.0)

        # 下游边界
        if Q_out is not None:
            Q_new[-1] = Q_out
        else:
            # 自由出流
            Q_new[-1] = self.manning_flow(h_new[-1])

        # 动量方程更新Q
        for i in range(1, self.N-1):
            A_i = self.B * h[i]
            dh_dx = (h[i+1] - h[i-1]) / (2 * self.dx)
            dQ_dx = (Q[i+1] - Q[i-1]) / (2 * self.dx)

            Sf_i = self.friction_slope(Q[i], h[i])
            Sf_i = np.clip(Sf_i, 0.0, 0.1)

            # 简化动量方程
            Q_new[i] = Q[i] - dt * (
                self.g * A_i * (dh_dx + Sf_i - self.i0)
            )

        # 最终检查
        h_new = np.nan_to_num(h_new, nan=1.0, posinf=10.0, neginf=0.1)
        Q_new = np.nan_to_num(Q_new, nan=5.0, posinf=50.0, neginf=0.1)

        self.h = h_new
        self.Q = Q_new

        return h_new, Q_new


class GateModel:
    """闸门模型"""
    def __init__(self, B=5):
        self.B = B
        self.g = 9.81

    def flow(self, h_up, opening):
        """计算闸门出流"""
        if opening < 0.01:
            return 0.0
        Cd = 0.6
        Q = Cd * self.B * opening * np.sqrt(2 * self.g * h_up)
        return Q


# ==================== POD（用于对比）====================

class POD:
    """POD降阶"""
    def __init__(self):
        self.modes = None
        self.S = None
        self.mean = None

    def fit(self, snapshots):
        """
        snapshots: (N, M) 每列是一个快照
        """
        self.mean = np.mean(snapshots, axis=1, keepdims=True)
        X = snapshots - self.mean

        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        self.modes = U
        self.S = S

    def project(self, h, r):
        """投影到低维空间"""
        h_centered = h.reshape(-1, 1) - self.mean
        a = self.modes[:, :r].T @ h_centered
        return a.flatten()

    def reconstruct(self, a):
        """重构"""
        r = len(a)
        h_recon = self.modes[:, :r] @ a.reshape(-1, 1) + self.mean
        return h_recon.flatten()


# ==================== PyTorch神经网络模型 ====================

if TORCH_AVAILABLE:

    class Autoencoder(nn.Module):
        """
        Autoencoder降阶模型
        Encoder: N → 128 → 64 → 32 → r
        Decoder: r → 32 → 64 → 128 → N
        """
        def __init__(self, input_dim, latent_dim):
            super(Autoencoder, self).__init__()

            # Encoder
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, latent_dim)
            )

            # Decoder
            self.decoder = nn.Sequential(
                nn.Linear(latent_dim, 32),
                nn.ReLU(),
                nn.Linear(32, 64),
                nn.ReLU(),
                nn.Linear(64, 128),
                nn.ReLU(),
                nn.Linear(128, input_dim)
            )

        def encode(self, x):
            return self.encoder(x)

        def decode(self, z):
            return self.decoder(z)

        def forward(self, x):
            z = self.encode(x)
            x_recon = self.decode(z)
            return x_recon, z


    class PINN(nn.Module):
        """
        Physics-Informed Neural Network
        输入: (x, t)
        输出: h(x, t)
        """
        def __init__(self):
            super(PINN, self).__init__()

            self.net = nn.Sequential(
                nn.Linear(2, 64),
                nn.Tanh(),
                nn.Linear(64, 64),
                nn.Tanh(),
                nn.Linear(64, 64),
                nn.Tanh(),
                nn.Linear(64, 1)
            )

        def forward(self, x, t):
            """
            x: 空间坐标 (batch, 1)
            t: 时间坐标 (batch, 1)
            """
            inputs = torch.cat([x, t], dim=1)
            h = self.net(inputs)
            return h


    class DeepONet(nn.Module):
        """
        简化的DeepONet
        Branch Net: 编码输入函数
        Trunk Net: 编码查询位置
        """
        def __init__(self, input_func_dim, output_dim=32):
            super(DeepONet, self).__init__()

            # Branch network: 编码输入函数
            self.branch = nn.Sequential(
                nn.Linear(input_func_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Linear(64, output_dim)
            )

            # Trunk network: 编码查询位置和时间
            self.trunk = nn.Sequential(
                nn.Linear(2, 64),  # (x, t)
                nn.Tanh(),
                nn.Linear(64, 64),
                nn.Tanh(),
                nn.Linear(64, output_dim)
            )

            # Bias
            self.bias = nn.Parameter(torch.zeros(1))

        def forward(self, u_func, x, t):
            """
            u_func: 输入函数 (batch, input_func_dim)
            x: 空间坐标 (batch, 1)
            t: 时间坐标 (batch, 1)
            """
            b = self.branch(u_func)  # (batch, output_dim)

            xt = torch.cat([x, t], dim=1)
            tau = self.trunk(xt)  # (batch, output_dim)

            # 内积
            out = torch.sum(b * tau, dim=1, keepdim=True) + self.bias
            return out


# ==================== 训练工具 ====================

def generate_training_data(n_samples=100, T_total=1800, dt=10, N=51):
    """
    生成训练数据
    每个样本：不同的初始条件和输入
    """
    print(f"生成 {n_samples} 个训练样本...")

    canal = CanalReach(N=N)
    gate = GateModel()

    all_snapshots = []
    all_inputs = []
    all_times = []

    for i in range(n_samples):
        # 随机初始条件
        h0 = np.random.uniform(0.8, 1.2, N)
        Q0 = np.random.uniform(4.0, 6.0, N)
        canal.set_state(h0, Q0)

        # 随机目标水位
        h_target = np.random.uniform(1.5, 2.5)

        # 简单PID控制器
        Kp = 0.5
        integral = 0

        snapshots = []
        times = []
        inputs_history = []

        t = 0
        n_steps = int(T_total / dt)

        for step in range(n_steps):
            # 控制器
            error = h_target - canal.h[-5]
            integral += error * dt
            u = Kp * error + 0.01 * integral
            u = np.clip(u, 0.2, 1.0)

            # 计算闸门出流
            Q_out = gate.flow(canal.h[-1], u)

            # 仿真步进
            Q_in = 5.0 + 0.5 * np.sin(2 * np.pi * t / 3600)
            canal.step(dt, Q_in=Q_in, Q_out=Q_out)

            # 每隔几步保存
            if step % 5 == 0:
                snapshots.append(canal.h.copy())
                times.append(t)
                inputs_history.append([Q_in, Q_out, u])

            t += dt

        all_snapshots.append(np.array(snapshots).T)  # (N, time_steps)
        all_inputs.append(np.array(inputs_history))
        all_times.append(np.array(times))

        if (i+1) % 20 == 0:
            print(f"  完成 {i+1}/{n_samples}")

    return all_snapshots, all_inputs, all_times


def normalize_data(data, mean=None, std=None):
    """归一化"""
    if mean is None:
        mean = np.mean(data)
        std = np.std(data)
    data_norm = (data - mean) / (std + 1e-8)
    return data_norm, mean, std


def train_autoencoder(model, data, epochs=200, batch_size=32, lr=0.001):
    """训练Autoencoder"""
    print(f"\n训练Autoencoder...")

    # 准备数据
    data_tensor = torch.FloatTensor(data)
    dataset = torch.utils.data.TensorDataset(data_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    losses = []

    for epoch in range(epochs):
        epoch_loss = 0
        for batch in dataloader:
            x = batch[0]

            optimizer.zero_grad()
            x_recon, z = model(x)
            loss = criterion(x_recon, x)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(dataloader)
        losses.append(avg_loss)

        if (epoch+1) % 50 == 0:
            print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")

    return losses


def train_pinn(model, x_data, t_data, h_data, x_pde, t_pde,
               epochs=1000, lr=0.001, lambda_pde=1.0, lambda_data=10.0):
    """训练PINN"""
    print(f"\n训练PINN...")

    optimizer = optim.Adam(model.parameters(), lr=lr)

    # 转换为tensor
    x_data_t = torch.FloatTensor(x_data).requires_grad_(True)
    t_data_t = torch.FloatTensor(t_data).requires_grad_(True)
    h_data_t = torch.FloatTensor(h_data)

    x_pde_t = torch.FloatTensor(x_pde).requires_grad_(True)
    t_pde_t = torch.FloatTensor(t_pde).requires_grad_(True)

    losses = []

    for epoch in range(epochs):
        optimizer.zero_grad()

        # 数据损失
        h_pred = model(x_data_t, t_data_t)
        loss_data = torch.mean((h_pred - h_data_t)**2)

        # PDE损失（简化的连续性方程）
        h_pde = model(x_pde_t, t_pde_t)

        # 计算导数
        h_t = torch.autograd.grad(h_pde.sum(), t_pde_t, create_graph=True)[0]
        h_x = torch.autograd.grad(h_pde.sum(), x_pde_t, create_graph=True)[0]

        # 简化的PDE残差: ∂h/∂t + c * ∂h/∂x ≈ 0 (c是波速)
        c = 2.0  # 假设波速
        pde_residual = h_t + c * h_x
        loss_pde = torch.mean(pde_residual**2)

        # 总损失
        loss = lambda_data * loss_data + lambda_pde * loss_pde

        loss.backward()
        optimizer.step()

        losses.append(loss.item())

        if (epoch+1) % 200 == 0:
            print(f"  Epoch {epoch+1}/{epochs}, Loss: {loss.item():.6f} "
                  f"(Data: {loss_data.item():.6f}, PDE: {loss_pde.item():.6f})")

    return losses


def train_deeponet(model, u_train, x_train, t_train, y_train,
                   epochs=200, batch_size=32, lr=0.001):
    """训练DeepONet"""
    print(f"\n训练DeepONet...")

    # 准备数据
    u_tensor = torch.FloatTensor(u_train)
    x_tensor = torch.FloatTensor(x_train)
    t_tensor = torch.FloatTensor(t_train)
    y_tensor = torch.FloatTensor(y_train)

    dataset = torch.utils.data.TensorDataset(u_tensor, x_tensor, t_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    losses = []

    for epoch in range(epochs):
        epoch_loss = 0
        for u, x, t, y in dataloader:
            optimizer.zero_grad()

            y_pred = model(u, x, t)
            loss = criterion(y_pred, y)

            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

        avg_loss = epoch_loss / len(dataloader)
        losses.append(avg_loss)

        if (epoch+1) % 50 == 0:
            print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")

    return losses


# ==================== 演示部分 ====================

def part1_autoencoder():
    """Part 1: Autoencoder降阶模型"""
    print("\n" + "="*60)
    print("Part 1: Autoencoder降阶模型")
    print("="*60)

    if not TORCH_AVAILABLE:
        print("需要安装PyTorch才能运行此部分")
        return

    # 生成训练数据
    snapshots_list, _, _ = generate_training_data(n_samples=50, T_total=1800, dt=10, N=51)

    # 合并所有快照
    all_snapshots = np.hstack(snapshots_list)  # (N, total_time_steps)
    print(f"总快照数: {all_snapshots.shape[1]}")

    # 归一化
    data_norm, mean, std = normalize_data(all_snapshots.T)  # (time_steps, N)

    # 训练Autoencoder
    N = all_snapshots.shape[0]
    latent_dim = 10

    model_ae = Autoencoder(input_dim=N, latent_dim=latent_dim)
    losses_ae = train_autoencoder(model_ae, data_norm, epochs=200, batch_size=64, lr=0.001)

    # 训练POD用于对比
    pod = POD()
    pod.fit(all_snapshots)

    # 测试重构
    test_idx = 100
    h_test = all_snapshots[:, test_idx]

    # Autoencoder重构
    h_test_norm = (h_test - mean) / std
    with torch.no_grad():
        h_test_tensor = torch.FloatTensor(h_test_norm).unsqueeze(0)
        h_recon_ae, z_ae = model_ae(h_test_tensor)
        h_recon_ae = h_recon_ae.squeeze().numpy() * std + mean

    # POD重构
    a_pod = pod.project(h_test, latent_dim)
    h_recon_pod = pod.reconstruct(a_pod)

    # 计算误差
    error_ae = np.linalg.norm(h_test - h_recon_ae) / np.linalg.norm(h_test)
    error_pod = np.linalg.norm(h_test - h_recon_pod) / np.linalg.norm(h_test)

    print(f"\n重构误差对比 (降阶维数={latent_dim}):")
    print(f"  Autoencoder: {error_ae:.6f}")
    print(f"  POD:         {error_pod:.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 训练损失
    ax = axes[0, 0]
    ax.plot(losses_ae, 'b-', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title('Autoencoder训练损失')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # 重构对比
    ax = axes[0, 1]
    x = np.linspace(0, 1000, N)
    ax.plot(x, h_test, 'k-', linewidth=2, label='原始')
    ax.plot(x, h_recon_ae, 'b--', linewidth=2, label=f'AE (误差={error_ae:.4f})')
    ax.plot(x, h_recon_pod, 'r:', linewidth=2, label=f'POD (误差={error_pod:.4f})')
    ax.set_xlabel('位置 (m)')
    ax.set_ylabel('水深 (m)')
    ax.set_title('重构对比')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 潜空间可视化（随机选择2个维度）
    ax = axes[1, 0]
    with torch.no_grad():
        data_tensor = torch.FloatTensor(data_norm)
        _, z_all = model_ae(data_tensor)
        z_all = z_all.numpy()

    ax.scatter(z_all[:, 0], z_all[:, 1], c=np.arange(len(z_all)),
               cmap='viridis', alpha=0.5, s=10)
    ax.set_xlabel('潜变量 z₁')
    ax.set_ylabel('潜变量 z₂')
    ax.set_title('潜空间可视化 (前2维)')
    ax.grid(True, alpha=0.3)

    # 误差分布
    ax = axes[1, 1]
    errors_ae_all = []
    errors_pod_all = []

    test_indices = np.random.choice(all_snapshots.shape[1], 100, replace=False)
    for idx in test_indices:
        h_i = all_snapshots[:, idx]

        # AE
        h_i_norm = (h_i - mean) / std
        with torch.no_grad():
            h_i_tensor = torch.FloatTensor(h_i_norm).unsqueeze(0)
            h_recon_i, _ = model_ae(h_i_tensor)
            h_recon_i = h_recon_i.squeeze().numpy() * std + mean
        err_ae = np.linalg.norm(h_i - h_recon_i) / np.linalg.norm(h_i)
        errors_ae_all.append(err_ae)

        # POD
        a_i = pod.project(h_i, latent_dim)
        h_recon_i_pod = pod.reconstruct(a_i)
        err_pod = np.linalg.norm(h_i - h_recon_i_pod) / np.linalg.norm(h_i)
        errors_pod_all.append(err_pod)

    ax.hist(errors_ae_all, bins=20, alpha=0.5, label='Autoencoder', color='blue')
    ax.hist(errors_pod_all, bins=20, alpha=0.5, label='POD', color='red')
    ax.set_xlabel('相对误差')
    ax.set_ylabel('频数')
    ax.set_title('重构误差分布')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('part1_autoencoder.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part1_autoencoder.png")
    plt.close()


def part2_pinn():
    """Part 2: PINN求解Saint-Venant方程"""
    print("\n" + "="*60)
    print("Part 2: PINN求解Saint-Venant方程")
    print("="*60)

    if not TORCH_AVAILABLE:
        print("需要安装PyTorch才能运行此部分")
        return

    # 生成参考解（使用有限差分）
    canal = CanalReach(N=51)
    gate = GateModel()

    h0 = np.ones(51) * 1.0
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    T_total = 600
    dt = 10
    n_steps = int(T_total / dt)

    h_history = []
    times = []

    for step in range(n_steps):
        t = step * dt
        Q_in = 5.0 + 1.0 * np.sin(2 * np.pi * t / 300)
        canal.step(dt, Q_in=Q_in)

        if step % 2 == 0:
            h_history.append(canal.h.copy())
            times.append(t)

    h_history = np.array(h_history)  # (time_steps, N)
    times = np.array(times)

    # 准备PINN训练数据
    x_grid = np.linspace(0, 1000, 51)
    t_grid = times

    # 数据点（稀疏采样）
    n_data = 200
    indices = np.random.choice(len(times), n_data, replace=False)
    x_data_list = []
    t_data_list = []
    h_data_list = []

    for idx in indices:
        x_idx = np.random.choice(51)
        x_data_list.append([x_grid[x_idx] / 1000])  # 归一化到[0,1]
        t_data_list.append([times[idx] / T_total])
        h_data_list.append([h_history[idx, x_idx]])

    x_data = np.array(x_data_list)
    t_data = np.array(t_data_list)
    h_data = np.array(h_data_list)

    # PDE配置点
    n_pde = 1000
    x_pde = np.random.uniform(0, 1, (n_pde, 1))
    t_pde = np.random.uniform(0, 1, (n_pde, 1))

    # 训练PINN
    model_pinn = PINN()
    losses_pinn = train_pinn(model_pinn, x_data, t_data, h_data, x_pde, t_pde,
                            epochs=1000, lr=0.001, lambda_pde=0.1, lambda_data=1.0)

    # 预测
    x_test = np.linspace(0, 1, 51).reshape(-1, 1)
    t_test = np.ones((51, 1)) * 0.5  # t=300s (归一化后0.5)

    with torch.no_grad():
        x_test_t = torch.FloatTensor(x_test)
        t_test_t = torch.FloatTensor(t_test)
        h_pred = model_pinn(x_test_t, t_test_t).numpy().flatten()

    # 参考解
    ref_idx = np.argmin(np.abs(times - T_total * 0.5))
    h_ref = h_history[ref_idx, :]

    error_pinn = np.linalg.norm(h_pred - h_ref) / np.linalg.norm(h_ref)
    print(f"\nPINN预测误差 (t=300s): {error_pinn:.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 训练损失
    ax = axes[0, 0]
    ax.plot(losses_pinn, 'b-', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title('PINN训练损失')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # 预测对比
    ax = axes[0, 1]
    ax.plot(x_grid, h_ref, 'k-', linewidth=2, label='有限差分')
    ax.plot(x_grid, h_pred, 'b--', linewidth=2, label=f'PINN (误差={error_pinn:.4f})')
    ax.scatter(x_data[:, 0] * 1000, h_data[:, 0], c='r', s=20, label='训练数据点', zorder=5)
    ax.set_xlabel('位置 (m)')
    ax.set_ylabel('水深 (m)')
    ax.set_title('PINN预测 (t=300s)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 时空演化
    ax = axes[1, 0]
    X, T = np.meshgrid(x_grid / 1000, times / T_total)
    X_flat = X.flatten().reshape(-1, 1)
    T_flat = T.flatten().reshape(-1, 1)

    with torch.no_grad():
        X_t = torch.FloatTensor(X_flat)
        T_t = torch.FloatTensor(T_flat)
        H_pred = model_pinn(X_t, T_t).numpy().reshape(X.shape)

    c = ax.contourf(X * 1000, T * T_total, H_pred, levels=20, cmap='viridis')
    plt.colorbar(c, ax=ax, label='水深 (m)')
    ax.set_xlabel('位置 (m)')
    ax.set_ylabel('时间 (s)')
    ax.set_title('PINN预测的时空演化')

    # 参考解时空演化
    ax = axes[1, 1]
    c = ax.contourf(X * 1000, T * T_total, h_history, levels=20, cmap='viridis')
    plt.colorbar(c, ax=ax, label='水深 (m)')
    ax.set_xlabel('位置 (m)')
    ax.set_ylabel('时间 (s)')
    ax.set_title('有限差分解的时空演化')

    plt.tight_layout()
    plt.savefig('part2_pinn_solution.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part2_pinn_solution.png")
    plt.close()


def part3_neural_operator():
    """Part 3: Neural Operator快速预测"""
    print("\n" + "="*60)
    print("Part 3: Neural Operator快速预测")
    print("="*60)

    if not TORCH_AVAILABLE:
        print("需要安装PyTorch才能运行此部分")
        return

    print("生成训练数据（不同初始条件）...")

    # 生成多组数据
    canal = CanalReach(N=51)
    gate = GateModel()

    n_samples = 50
    T_predict = 300
    dt = 10
    n_steps = int(T_predict / dt)

    input_funcs = []
    output_states = []

    for i in range(n_samples):
        # 随机初始条件
        h0 = np.random.uniform(0.8, 1.2, 51)
        Q0 = np.ones(51) * 5.0
        canal.set_state(h0, Q0)

        # 仿真
        for step in range(n_steps):
            Q_in = 5.0
            canal.step(dt, Q_in=Q_in)

        # 记录
        input_funcs.append(h0)
        output_states.append(canal.h.copy())

    input_funcs = np.array(input_funcs)
    output_states = np.array(output_states)

    # 归一化
    input_mean, input_std = np.mean(input_funcs), np.std(input_funcs)
    output_mean, output_std = np.mean(output_states), np.std(output_states)

    input_norm = (input_funcs - input_mean) / input_std
    output_norm = (output_states - output_mean) / output_std

    # 准备训练数据
    # 对于每个样本，在多个位置查询
    n_query = 10
    u_train_list = []
    x_train_list = []
    t_train_list = []
    y_train_list = []

    for i in range(n_samples):
        query_indices = np.random.choice(51, n_query, replace=False)
        for idx in query_indices:
            u_train_list.append(input_norm[i])
            x_train_list.append([idx / 50.0])  # 归一化位置
            t_train_list.append([1.0])  # t=T_predict (归一化后为1)
            y_train_list.append([output_norm[i, idx]])

    u_train = np.array(u_train_list)
    x_train = np.array(x_train_list)
    t_train = np.array(t_train_list)
    y_train = np.array(y_train_list)

    # 训练DeepONet
    model_don = DeepONet(input_func_dim=51, output_dim=32)
    losses_don = train_deeponet(model_don, u_train, x_train, t_train, y_train,
                               epochs=200, batch_size=64, lr=0.001)

    # 测试：新的初始条件
    h0_test = np.random.uniform(0.8, 1.2, 51)

    # 使用有限差分求解（参考）
    canal.set_state(h0_test, np.ones(51) * 5.0)
    for step in range(n_steps):
        canal.step(dt, Q_in=5.0)
    h_ref = canal.h.copy()

    # 使用DeepONet预测
    h0_test_norm = (h0_test - input_mean) / input_std
    x_test = np.linspace(0, 1, 51).reshape(-1, 1)
    t_test = np.ones((51, 1))
    u_test = np.tile(h0_test_norm, (51, 1))

    with torch.no_grad():
        u_test_t = torch.FloatTensor(u_test)
        x_test_t = torch.FloatTensor(x_test)
        t_test_t = torch.FloatTensor(t_test)
        h_pred = model_don(u_test_t, x_test_t, t_test_t).numpy().flatten()
        h_pred = h_pred * output_std + output_mean

    error_don = np.linalg.norm(h_pred - h_ref) / np.linalg.norm(h_ref)
    print(f"\nDeepONet预测误差: {error_don:.6f}")

    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 训练损失
    ax = axes[0, 0]
    ax.plot(losses_don, 'b-', linewidth=2)
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Loss')
    ax.set_title('DeepONet训练损失')
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # 预测对比
    ax = axes[0, 1]
    x_grid = np.linspace(0, 1000, 51)
    ax.plot(x_grid, h0_test, 'g-', linewidth=2, label='初始条件', alpha=0.7)
    ax.plot(x_grid, h_ref, 'k-', linewidth=2, label='有限差分')
    ax.plot(x_grid, h_pred, 'b--', linewidth=2, label=f'DeepONet (误差={error_don:.4f})')
    ax.set_xlabel('位置 (m)')
    ax.set_ylabel('水深 (m)')
    ax.set_title(f'Neural Operator预测 (t={T_predict}s)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 训练样本展示
    ax = axes[1, 0]
    for i in range(min(10, n_samples)):
        ax.plot(x_grid, input_funcs[i], 'b-', alpha=0.3, linewidth=1)
    ax.plot(x_grid, input_funcs[0], 'b-', alpha=0.3, linewidth=1, label='初始条件样本')
    ax.set_xlabel('位置 (m)')
    ax.set_ylabel('水深 (m)')
    ax.set_title('训练样本（初始条件）')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 速度对比
    ax = axes[1, 1]

    # 测试推理速度
    times_fd = []
    times_don = []

    for _ in range(10):
        # 有限差分
        t0 = time.time()
        canal.set_state(h0_test, np.ones(51) * 5.0)
        for step in range(n_steps):
            canal.step(dt, Q_in=5.0)
        t_fd = time.time() - t0
        times_fd.append(t_fd)

        # DeepONet
        t0 = time.time()
        with torch.no_grad():
            _ = model_don(u_test_t, x_test_t, t_test_t)
        t_don = time.time() - t0
        times_don.append(t_don)

    avg_fd = np.mean(times_fd) * 1000
    avg_don = np.mean(times_don) * 1000
    speedup = avg_fd / avg_don

    methods = ['有限差分', 'DeepONet']
    times_avg = [avg_fd, avg_don]
    colors = ['red', 'blue']

    bars = ax.bar(methods, times_avg, color=colors, alpha=0.7)
    ax.set_ylabel('计算时间 (ms)')
    ax.set_title(f'推理速度对比 (加速比={speedup:.1f}x)')
    ax.grid(True, alpha=0.3, axis='y')

    # 在柱状图上标注数值
    for bar, t in zip(bars, times_avg):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{t:.2f} ms', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('part3_neural_operator.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part3_neural_operator.png")
    plt.close()


def part4_comparison():
    """Part 4: 方法对比"""
    print("\n" + "="*60)
    print("Part 4: 降阶方法综合对比")
    print("="*60)

    # 生成测试数据
    print("生成测试数据...")
    canal = CanalReach(N=51)
    gate = GateModel()

    h0 = np.ones(51) * 1.0
    Q0 = np.ones(51) * 5.0
    canal.set_state(h0, Q0)

    T_total = 900
    dt = 10
    n_steps = int(T_total / dt)

    h_history = []
    times = []

    Kp = 0.5
    integral = 0
    h_target = 2.0

    for step in range(n_steps):
        t = step * dt

        # 控制器
        error = h_target - canal.h[-5]
        integral += error * dt
        u = Kp * error + 0.01 * integral
        u = np.clip(u, 0.2, 1.0)

        Q_out = gate.flow(canal.h[-1], u)
        Q_in = 5.0

        canal.step(dt, Q_in=Q_in, Q_out=Q_out)
        h_history.append(canal.h.copy())
        times.append(t)

    h_history = np.array(h_history)
    times = np.array(times)

    print(f"测试数据: {h_history.shape[0]} 个时间步")

    # 方法1: POD
    print("\n测试POD...")
    snapshots = h_history[::5].T  # 降采样
    pod = POD()
    pod.fit(snapshots)

    r = 10
    errors_pod = []
    times_pod = []

    for i in range(len(h_history)):
        t0 = time.time()
        a = pod.project(h_history[i], r)
        h_recon = pod.reconstruct(a)
        t_pod = time.time() - t0

        error = np.linalg.norm(h_history[i] - h_recon) / np.linalg.norm(h_history[i])
        errors_pod.append(error)
        times_pod.append(t_pod * 1000)

    avg_error_pod = np.mean(errors_pod)
    avg_time_pod = np.mean(times_pod)

    print(f"POD: 平均误差={avg_error_pod:.6f}, 平均时间={avg_time_pod:.4f}ms")

    # 方法2: Autoencoder (如果可用)
    if TORCH_AVAILABLE:
        print("\n测试Autoencoder...")

        # 简化训练（使用测试数据）
        data_norm, mean, std = normalize_data(h_history)
        model_ae = Autoencoder(input_dim=51, latent_dim=r)
        train_autoencoder(model_ae, data_norm, epochs=100, batch_size=32, lr=0.001)

        errors_ae = []
        times_ae = []

        for i in range(len(h_history)):
            h_norm = (h_history[i] - mean) / std

            t0 = time.time()
            with torch.no_grad():
                h_tensor = torch.FloatTensor(h_norm).unsqueeze(0)
                h_recon, _ = model_ae(h_tensor)
                h_recon = h_recon.squeeze().numpy() * std + mean
            t_ae = time.time() - t0

            error = np.linalg.norm(h_history[i] - h_recon) / np.linalg.norm(h_history[i])
            errors_ae.append(error)
            times_ae.append(t_ae * 1000)

        avg_error_ae = np.mean(errors_ae)
        avg_time_ae = np.mean(times_ae)

        print(f"Autoencoder: 平均误差={avg_error_ae:.6f}, 平均时间={avg_time_ae:.4f}ms")
    else:
        avg_error_ae = 0
        avg_time_ae = 0
        errors_ae = []

    # 可视化对比
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 误差对比
    ax = axes[0, 0]
    ax.plot(times, errors_pod, 'r-', linewidth=2, label='POD', alpha=0.7)
    if TORCH_AVAILABLE:
        ax.plot(times, errors_ae, 'b-', linewidth=2, label='Autoencoder', alpha=0.7)
    ax.set_xlabel('时间 (s)')
    ax.set_ylabel('相对误差')
    ax.set_title('重构误差随时间变化')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')

    # 平均误差对比
    ax = axes[0, 1]
    methods = ['POD']
    errors = [avg_error_pod]
    colors = ['red']

    if TORCH_AVAILABLE:
        methods.append('Autoencoder')
        errors.append(avg_error_ae)
        colors.append('blue')

    bars = ax.bar(methods, errors, color=colors, alpha=0.7)
    ax.set_ylabel('平均相对误差')
    ax.set_title('方法精度对比')
    ax.grid(True, alpha=0.3, axis='y')

    for bar, err in zip(bars, errors):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{err:.6f}', ha='center', va='bottom')

    # 计算时间对比
    ax = axes[1, 0]
    times_comp = [avg_time_pod]
    if TORCH_AVAILABLE:
        times_comp.append(avg_time_ae)

    bars = ax.bar(methods, times_comp, color=colors, alpha=0.7)
    ax.set_ylabel('平均计算时间 (ms)')
    ax.set_title('方法速度对比')
    ax.grid(True, alpha=0.3, axis='y')

    for bar, t in zip(bars, times_comp):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{t:.4f} ms', ha='center', va='bottom')

    # 特性雷达图
    ax = axes[1, 1]

    categories = ['精度', '速度', '可解释性', '数据需求', '泛化能力']
    N_cat = len(categories)

    # 归一化分数 (0-1, 越高越好)
    pod_scores = [0.7, 0.9, 1.0, 0.6, 0.7]
    ae_scores = [0.9, 0.5, 0.3, 0.4, 0.8]

    angles = np.linspace(0, 2 * np.pi, N_cat, endpoint=False).tolist()
    pod_scores += pod_scores[:1]
    ae_scores += ae_scores[:1]
    angles += angles[:1]

    ax = plt.subplot(2, 2, 4, projection='polar')
    ax.plot(angles, pod_scores, 'o-', linewidth=2, label='POD', color='red')
    ax.fill(angles, pod_scores, alpha=0.25, color='red')

    if TORCH_AVAILABLE:
        ax.plot(angles, ae_scores, 'o-', linewidth=2, label='Autoencoder', color='blue')
        ax.fill(angles, ae_scores, alpha=0.25, color='blue')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.set_title('方法特性对比', y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)

    plt.tight_layout()
    plt.savefig('part4_method_comparison.png', dpi=150, bbox_inches='tight')
    print("图表已保存: part4_method_comparison.png")
    plt.close()

    # 打印总结表格
    print("\n" + "="*60)
    print("方法对比总结")
    print("="*60)
    print(f"{'方法':<15} {'平均误差':<15} {'平均时间(ms)':<15}")
    print("-" * 60)
    print(f"{'POD':<15} {avg_error_pod:<15.6f} {avg_time_pod:<15.4f}")
    if TORCH_AVAILABLE:
        print(f"{'Autoencoder':<15} {avg_error_ae:<15.6f} {avg_time_ae:<15.4f}")
    print("="*60)


def main():
    """主函数"""
    print("="*60)
    print("案例7：神经网络降阶模型")
    print("Neural Network Reduced Order Model")
    print("="*60)

    if not TORCH_AVAILABLE:
        print("\n警告：未安装PyTorch")
        print("请安装: pip install torch torchvision")
        print("将仅运行部分演示")

    # 运行所有部分
    part1_autoencoder()
    part2_pinn()
    part3_neural_operator()
    part4_comparison()

    print("\n" + "="*60)
    print("案例7完成！所有图表已保存。")
    print("="*60)

    print("\n关键结论：")
    print("1. Autoencoder提供非线性降阶能力，适合复杂流形")
    print("2. PINN嵌入物理约束，可以少量数据训练")
    print("3. Neural Operator学习算子映射，推理速度快")
    print("4. 神经网络方法是传统方法的补充，各有优势")
    print("5. 实际应用需权衡精度、速度、可解释性")


if __name__ == "__main__":
    main()
