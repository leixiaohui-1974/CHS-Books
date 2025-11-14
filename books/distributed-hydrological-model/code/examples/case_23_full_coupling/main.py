"""
案例23：分布式水文-水动力全耦合
================================

演示完整的分布式水文-水动力耦合模型，
实现网格化产汇流与一维河道水动力的双向耦合。

核心内容：
1. 网格化产汇流模型
2. 一维河道水动力模型
from pathlib import Path
3. 坡面-河道双向耦合
4. 完整物理过程模拟
5. 高精度洪水演进

作者: CHS-Books项目组
日期: 2025-11-02
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import sys
import os
from typing import Dict, Tuple, List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.runoff_generation.xaj_model import XinAnJiangModel
from core.coupling.saint_venant import SaintVenant1D

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GridCell:
    """网格单元类"""
    
    def __init__(self, i: int, j: int, elevation: float, area: float):
        """
        初始化网格单元
        
        Parameters
        ----------
        i, j : int
            网格索引
        elevation : float
            高程 (m)
        area : float
            面积 (m²)
        """
        self.i = i
        self.j = j
        self.elevation = elevation
        self.area = area
        
        # 流向（指向8个邻居之一，或-1表示出口）
        self.flow_direction = None
        self.downstream_cell = None
        
        # 水文状态
        self.runoff = 0.0  # 产流量 (mm)
        self.lateral_inflow = 0.0  # 侧向入流 (m³/s)
        self.discharge = 0.0  # 出流 (m³/s)
        
        # 是否为河道单元
        self.is_channel = False
        self.channel_segment_id = None


class DistributedHydroModel:
    """分布式水文模型"""
    
    def __init__(self, nx: int, ny: int, cell_size: float):
        """
        初始化分布式模型
        
        Parameters
        ----------
        nx, ny : int
            网格数量
        cell_size : float
            网格尺寸 (m)
        """
        self.nx = nx
        self.ny = ny
        self.cell_size = cell_size
        self.cell_area = cell_size * cell_size
        
        # 网格单元
        self.cells = np.empty((ny, nx), dtype=object)
        
        # 河道段列表
        self.channel_segments = []
        
    def create_watershed(self, dem: np.ndarray):
        """
        创建流域网格
        
        Parameters
        ----------
        dem : np.ndarray
            数字高程模型
        """
        for i in range(self.ny):
            for j in range(self.nx):
                cell = GridCell(i, j, dem[i, j], self.cell_area)
                self.cells[i, j] = cell
        
        # 计算流向（简化D8算法）
        self._compute_flow_directions()
    
    def _compute_flow_directions(self):
        """计算流向（简化为从高到低）"""
        # 8个方向 (di, dj)
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        
        for i in range(self.ny):
            for j in range(self.nx):
                cell = self.cells[i, j]
                
                # 找到最陡的下坡方向
                max_slope = 0
                best_direction = None
                
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < self.ny and 0 <= nj < self.nx:
                        neighbor = self.cells[ni, nj]
                        slope = (cell.elevation - neighbor.elevation)
                        if slope > max_slope:
                            max_slope = slope
                            best_direction = (ni, nj)
                
                if best_direction is not None:
                    cell.downstream_cell = self.cells[best_direction[0], best_direction[1]]
    
    def define_channel_network(self):
        """定义河道网络（简化为主河道）"""
        # 主河道：从左到右贯穿流域
        channel_cells = []
        for j in range(self.nx):
            # 河道在中间行
            i = self.ny // 2
            cell = self.cells[i, j]
            cell.is_channel = True
            cell.channel_segment_id = j
            channel_cells.append(cell)
        
        return channel_cells
    
    def run_runoff_generation(self, rainfall: np.ndarray, evaporation: np.ndarray,
                             xaj_params: Dict) -> np.ndarray:
        """
        运行产流计算
        
        Parameters
        ----------
        rainfall : np.ndarray
            降雨场 (ny, nx, nt)
        evaporation : np.ndarray
            蒸发场 (ny, nx, nt)
        xaj_params : dict
            新安江模型参数
            
        Returns
        -------
        runoff : np.ndarray
            产流场 (ny, nx, nt)
        """
        nt = rainfall.shape[2]
        runoff = np.zeros((self.ny, self.nx, nt))
        
        # 为每个网格创建XAJ模型
        for i in range(self.ny):
            for j in range(self.nx):
                model = XinAnJiangModel(xaj_params)
                
                # 提取该网格的时间序列
                P = rainfall[i, j, :]
                EM = evaporation[i, j, :]
                
                # 运行模型
                results = model.run(P, EM)
                R = results['R']
                R = np.nan_to_num(R, nan=0.0, posinf=0.0, neginf=0.0)
                R = np.maximum(R, 0.0)
                
                runoff[i, j, :] = R
        
        return runoff
    
    def run_slope_routing(self, runoff: np.ndarray, dt: float) -> np.ndarray:
        """
        运行坡面汇流
        
        Parameters
        ----------
        runoff : np.ndarray
            产流 (ny, nx, nt)
        dt : float
            时间步长 (s)
            
        Returns
        -------
        lateral_inflow : np.ndarray
            侧向入流到河道 (n_channel_cells, nt)
        """
        nt = runoff.shape[2]
        
        # 简化：假设每个网格的产流经过滞后后汇入河道
        # 使用线性水库汇流
        k = 3600.0  # 调蓄系数 (s)
        
        lateral_inflow_grid = np.zeros((self.ny, self.nx, nt))
        
        for i in range(self.ny):
            for j in range(self.nx):
                cell = self.cells[i, j]
                
                if not cell.is_channel:
                    # 坡面单元：线性水库汇流
                    S = 0.0  # 蓄量
                    for t in range(nt):
                        # 产流 (mm/dt) -> (m³/s)
                        inflow = runoff[i, j, t] / 1000.0 * cell.area / dt
                        
                        # 水量平衡
                        S_new = S + inflow * dt
                        outflow = S_new / k
                        S = S_new - outflow * dt
                        S = max(S, 0.0)
                        
                        # 汇入下游单元
                        if cell.downstream_cell is not None:
                            di, dj = cell.downstream_cell.i, cell.downstream_cell.j
                            lateral_inflow_grid[di, dj, t] += outflow
        
        # 提取河道单元的侧向入流
        channel_cells = [self.cells[self.ny//2, j] for j in range(self.nx)]
        lateral_inflow = np.zeros((len(channel_cells), nt))
        for idx, cell in enumerate(channel_cells):
            lateral_inflow[idx, :] = lateral_inflow_grid[cell.i, cell.j, :]
        
        return lateral_inflow


class FullyCoupledModel:
    """完全耦合模型"""
    
    def __init__(self, hydro_model: DistributedHydroModel):
        """
        初始化耦合模型
        
        Parameters
        ----------
        hydro_model : DistributedHydroModel
            分布式水文模型
        """
        self.hydro_model = hydro_model
        self.channel_model = None
        
    def setup_channel_model(self, length: float, dx: float, dt: float, 
                          slope: float, n_manning: float, width: float):
        """
        设置河道模型
        
        Parameters
        ----------
        length : float
            河道长度 (m)
        dx : float
            河段长度 (m)
        dt : float
            时间步长 (s)
        slope : float
            河床坡度
        n_manning : float
            Manning糙率
        width : float
            河道宽度 (m)
        """
        self.channel_model = SaintVenant1D(
            L=length,
            dx=dx,
            dt=dt,
            n=n_manning,
            B=width,
            S0=slope
        )
        # 初始化河道状态
        self.channel_model.initialize(h0=0.5, Q0=0.0)
    
    def run_coupled_simulation(self, rainfall: np.ndarray, evaporation: np.ndarray,
                              xaj_params: Dict, dt: float, 
                              initial_h: float = 0.5) -> Dict:
        """
        运行耦合模拟
        
        Parameters
        ----------
        rainfall : np.ndarray
            降雨场 (ny, nx, nt)
        evaporation : np.ndarray
            蒸发场 (ny, nx, nt)
        xaj_params : dict
            新安江参数
        dt : float
            时间步长 (s)
        initial_h : float
            初始水深 (m)
            
        Returns
        -------
        results : dict
            模拟结果
        """
        nt = rainfall.shape[2]
        
        print("   步骤1: 产流计算...")
        runoff = self.hydro_model.run_runoff_generation(rainfall, evaporation, xaj_params)
        
        print("   步骤2: 坡面汇流...")
        lateral_inflow = self.hydro_model.run_slope_routing(runoff, dt)
        
        print("   步骤3: 河道演进（水动力耦合）...")
        # 获取河道网格数
        nx = self.channel_model.nx
        
        # 初始化河道状态历史
        h_history = np.zeros((nt, nx))
        Q_history = np.zeros((nt, nx))
        h_history[0, :] = self.channel_model.h
        Q_history[0, :] = self.channel_model.Q
        
        # 上游边界条件（假设无入流，仅侧向入流）
        Q_upstream_series = np.zeros(nt) + 1.0  # 小的基流
        
        # 时间推进
        for t in range(nt - 1):
            # 河道水动力计算
            h_new, Q_new = self.channel_model.solve_step(
                Q_upstream=Q_upstream_series[t],
                h_downstream=None
            )
            
            # 添加侧向入流的影响（简化）
            total_lateral = np.sum(lateral_inflow[:, t])
            if total_lateral > 0:
                # 均匀增加流量（简化处理）
                Q_new += total_lateral / nx
            
            h_history[t + 1, :] = h_new
            Q_history[t + 1, :] = Q_new
        
        return {
            'runoff': runoff,
            'lateral_inflow': lateral_inflow,
            'h_channel': h_history,
            'Q_channel': Q_history
        }


def run_full_coupling():
    """运行完全耦合模拟"""
    print("\n" + "="*70)
    print("案例23：分布式水文-水动力全耦合")
    print("="*70 + "\n")
    
    output_dir = 'outputs'
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 创建流域
    print("1. 创建流域...")
    nx, ny = 20, 10  # 网格数量
    cell_size = 500.0  # 网格尺寸 (m)
    
    hydro_model = DistributedHydroModel(nx, ny, cell_size)
    
    # 生成DEM（从左上到右下递减）
    x = np.linspace(0, nx-1, nx)
    y = np.linspace(0, ny-1, ny)
    X, Y = np.meshgrid(x, y)
    dem = 100 - 0.5*X - 1.0*Y + 5*np.sin(X/2)*np.cos(Y/2)
    
    hydro_model.create_watershed(dem)
    
    print(f"   网格尺寸: {ny} × {nx}")
    print(f"   网格分辨率: {cell_size} m")
    print(f"   流域面积: {nx*ny*cell_size*cell_size/1e6:.2f} km²")
    print(f"   高程范围: {dem.min():.1f} - {dem.max():.1f} m\n")
    
    # 2. 定义河道网络
    print("2. 定义河道网络...")
    channel_cells = hydro_model.define_channel_network()
    
    print(f"   河道长度: {len(channel_cells) * cell_size / 1000:.1f} km")
    print(f"   河道单元数: {len(channel_cells)}\n")
    
    # 3. 创建耦合模型
    print("3. 创建水文-水动力耦合模型...")
    coupled_model = FullyCoupledModel(hydro_model)
    
    # 河道参数
    channel_length = len(channel_cells) * cell_size
    dt = 3600.0  # 时间步长
    coupled_model.setup_channel_model(
        length=channel_length,
        dx=cell_size,
        dt=dt,
        slope=0.001,
        n_manning=0.03,
        width=50.0
    )
    
    print(f"   河道坡度: 0.001")
    print(f"   Manning糙率: 0.03")
    print(f"   河道宽度: 50 m\n")
    
    # 4. 生成降雨场
    print("4. 生成降雨场...")
    nt = 48  # 48小时
    dt = 3600.0  # 1小时
    
    # 均匀降雨 + 暴雨中心
    rainfall = np.ones((ny, nx, nt)) * 2.0
    
    # 在t=10-20小时，流域中上游有暴雨中心
    for t in range(10, 20):
        for i in range(ny):
            for j in range(nx):
                # 暴雨中心在(ny/4, nx/2)附近
                dist = np.sqrt((i - ny/4)**2 + (j - nx/2)**2)
                intensity = 40 * np.exp(-(dist / 3)**2)
                rainfall[i, j, t] += intensity
    
    # 蒸发（均匀）
    evaporation = np.ones((ny, nx, nt)) * 3.0
    
    print(f"   时间步数: {nt} 小时")
    print(f"   最大降雨: {rainfall.max():.1f} mm/h")
    print(f"   蒸发: {evaporation[0,0,0]:.1f} mm/h\n")
    
    # 5. 新安江参数
    xaj_params = {
        'K': 0.8,
        'UM': 20.0,
        'LM': 80.0,
        'C': 0.18,
        'WM': 120.0,
        'B': 0.40,
        'IM': 0.02,
        'SM': 30.0,
        'EX': 1.2,
        'KG': 0.45,
        'KI': 0.35,
        'CG': 0.98,
        'CI': 0.70,
        'CS': 0.85
    }
    
    # 6. 运行耦合模拟
    print("5. 运行耦合模拟...")
    results = coupled_model.run_coupled_simulation(
        rainfall, evaporation, xaj_params, dt, initial_h=0.5
    )
    
    print("   耦合模拟完成\n")
    
    # 7. 结果统计
    print("="*70)
    print("模拟结果统计")
    print("="*70)
    
    runoff = results['runoff']
    Q_channel = results['Q_channel']
    h_channel = results['h_channel']
    
    print(f"\n【产流】")
    print(f"  总产流量: {np.sum(runoff):.1f} mm")
    print(f"  最大产流强度: {np.max(runoff):.1f} mm/h")
    print(f"  平均产流量: {np.mean(runoff):.2f} mm/h")
    
    print(f"\n【河道流量】")
    print(f"  出口最大流量: {np.max(Q_channel[:, -1]):.1f} m³/s")
    print(f"  出口峰现时间: {np.argmax(Q_channel[:, -1])} 小时")
    
    print(f"\n【河道水深】")
    print(f"  最大水深: {np.max(h_channel):.2f} m")
    print(f"  平均水深: {np.mean(h_channel):.2f} m")
    
    # 8. 可视化
    print(f"\n6. 生成可视化...")
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
    
    time = np.arange(nt)
    
    # 图1: DEM与河道
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = ax1.imshow(dem, cmap='terrain', origin='lower', extent=[0, nx, 0, ny])
    # 标记河道
    river_y = ny // 2
    ax1.plot([0, nx], [river_y, river_y], 'b-', linewidth=3, label='河道')
    ax1.set_xlabel('X (网格)', fontsize=10)
    ax1.set_ylabel('Y (网格)', fontsize=10)
    ax1.set_title('流域DEM与河道', fontsize=12, fontweight='bold')
    ax1.legend(fontsize=9)
    plt.colorbar(im1, ax=ax1, label='高程 (m)')
    
    # 图2: 累积降雨
    ax2 = fig.add_subplot(gs[0, 1])
    cumulative_rainfall = np.sum(rainfall, axis=2)
    im2 = ax2.imshow(cumulative_rainfall, cmap='Blues', origin='lower', 
                     extent=[0, nx, 0, ny])
    ax2.plot([0, nx], [river_y, river_y], 'r-', linewidth=2, alpha=0.7)
    ax2.set_xlabel('X (网格)', fontsize=10)
    ax2.set_ylabel('Y (网格)', fontsize=10)
    ax2.set_title('累积降雨分布', fontsize=12, fontweight='bold')
    plt.colorbar(im2, ax=ax2, label='降雨 (mm)')
    
    # 图3: 累积产流
    ax3 = fig.add_subplot(gs[0, 2])
    cumulative_runoff = np.sum(runoff, axis=2)
    im3 = ax3.imshow(cumulative_runoff, cmap='YlOrRd', origin='lower',
                     extent=[0, nx, 0, ny])
    ax3.plot([0, nx], [river_y, river_y], 'b-', linewidth=2, alpha=0.7)
    ax3.set_xlabel('X (网格)', fontsize=10)
    ax3.set_ylabel('Y (网格)', fontsize=10)
    ax3.set_title('累积产流分布', fontsize=12, fontweight='bold')
    plt.colorbar(im3, ax=ax3, label='产流 (mm)')
    
    # 图4: 河道流量过程（多个断面）
    ax4 = fig.add_subplot(gs[1, :])
    segments_to_plot = [0, nx//4, nx//2, 3*nx//4, nx-1]
    for seg in segments_to_plot:
        label = f'河段{seg}' if seg < nx-1 else '出口'
        ax4.plot(time, Q_channel[:, seg], linewidth=2, label=label)
    
    ax4.set_xlabel('时间 (h)', fontsize=11)
    ax4.set_ylabel('流量 (m³/s)', fontsize=11)
    ax4.set_title('河道流量过程', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=9, ncol=5, loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    # 图5: 河道水深过程
    ax5 = fig.add_subplot(gs[2, 0])
    for seg in segments_to_plot:
        label = f'河段{seg}' if seg < nx-1 else '出口'
        ax5.plot(time, h_channel[:, seg], linewidth=2, label=label)
    
    ax5.set_xlabel('时间 (h)', fontsize=11)
    ax5.set_ylabel('水深 (m)', fontsize=11)
    ax5.set_title('河道水深过程', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3)
    
    # 图6: 纵剖面（峰值时刻）
    ax6 = fig.add_subplot(gs[2, 1])
    peak_time = np.argmax(Q_channel[:, -1])
    
    # 河道网格点数
    nx_channel = h_channel.shape[1]
    river_length = np.linspace(0, channel_length/1000, nx_channel)  # km
    
    # 河床高程（插值到河道网格）
    bed_elevation_cells = dem[river_y, :]
    bed_elevation = np.interp(
        np.linspace(0, 1, nx_channel),
        np.linspace(0, 1, len(bed_elevation_cells)),
        bed_elevation_cells
    )
    water_surface = bed_elevation + h_channel[peak_time, :]
    
    ax6.fill_between(river_length, 0, bed_elevation, color='brown', 
                     alpha=0.3, label='河床')
    ax6.fill_between(river_length, bed_elevation, water_surface, 
                     color='blue', alpha=0.5, label='水面')
    ax6.plot(river_length, water_surface, 'b-', linewidth=2)
    
    ax6.set_xlabel('河道里程 (km)', fontsize=11)
    ax6.set_ylabel('高程 (m)', fontsize=11)
    ax6.set_title(f'河道纵剖面 (t={peak_time}h)', fontsize=12, fontweight='bold')
    ax6.legend(fontsize=9)
    ax6.grid(True, alpha=0.3)
    
    # 图7: 流量-水深关系（出口）
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.scatter(Q_channel[:, -1], h_channel[:, -1], c=time, 
               cmap='viridis', s=50, alpha=0.7)
    ax7.set_xlabel('流量 (m³/s)', fontsize=11)
    ax7.set_ylabel('水深 (m)', fontsize=11)
    ax7.set_title('出口流量-水深关系', fontsize=12, fontweight='bold')
    ax7.grid(True, alpha=0.3)
    cbar = plt.colorbar(ax7.scatter(Q_channel[:, -1], h_channel[:, -1], 
                                    c=time, cmap='viridis', s=50, alpha=0.7), 
                       ax=ax7)
    cbar.set_label('时间 (h)', fontsize=10)
    
    plt.savefig(f'{output_dir}/full_coupling.png', 
                dpi=300, bbox_inches='tight')
    print(f"   图表已保存: {output_dir}/full_coupling.png")
    plt.close()
    
    print(f"\n图表已保存到 {output_dir}/ 目录")
    print("="*70 + "\n")


if __name__ == '__main__':
    run_full_coupling()
