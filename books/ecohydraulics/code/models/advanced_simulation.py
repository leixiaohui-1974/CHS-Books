"""高级模拟技术模型

本模块包含高级数值模拟技术：
- ShallowWater2D: 2D浅水方程有限体积法
- AgentBasedFish: 鱼类行为智能体模型
- MLFlowPredictor: 机器学习预测生态流量
- CFDFishway: CFD鱼道流场模拟
- RemoteSensingGIS: 遥感GIS集成分析
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class ShallowWater2D:
    """2D浅水方程有限体积法模拟（案例46）
    
    求解二维浅水方程
    """
    
    def __init__(self,
                 nx: int,
                 ny: int,
                 dx: float,
                 dy: float):
        """
        Parameters:
        -----------
        nx, ny : int
            网格数
        dx, dy : float
            网格间距 (m)
        """
        self.nx = nx
        self.ny = ny
        self.dx = dx
        self.dy = dy
        self.g = 9.81
        
        # 初始化网格
        self.h = np.zeros((ny, nx))  # 水深
        self.u = np.zeros((ny, nx))  # x方向流速
        self.v = np.zeros((ny, nx))  # y方向流速
        self.z = np.zeros((ny, nx))  # 底床高程
    
    def set_initial_conditions(self,
                              h0: np.ndarray,
                              u0: np.ndarray = None,
                              v0: np.ndarray = None):
        """设置初始条件"""
        self.h = h0.copy()
        if u0 is not None:
            self.u = u0.copy()
        if v0 is not None:
            self.v = v0.copy()
    
    def set_topography(self, z: np.ndarray):
        """设置地形"""
        self.z = z.copy()
    
    def compute_fluxes(self) -> Tuple[np.ndarray, np.ndarray]:
        """计算通量（简化HLLC）"""
        # x方向通量
        F = np.zeros((self.ny, self.nx, 3))
        F[:, :, 0] = self.h * self.u
        F[:, :, 1] = self.h * self.u**2 + 0.5 * self.g * self.h**2
        F[:, :, 2] = self.h * self.u * self.v
        
        # y方向通量
        G = np.zeros((self.ny, self.nx, 3))
        G[:, :, 0] = self.h * self.v
        G[:, :, 1] = self.h * self.u * self.v
        G[:, :, 2] = self.h * self.v**2 + 0.5 * self.g * self.h**2
        
        return F, G
    
    def time_step(self, dt: float, manning_n: float = 0.03):
        """时间步进（显式欧拉）
        
        Parameters:
        -----------
        dt : float
            时间步长 (s)
        manning_n : float
            曼宁糙率系数
        """
        # 保存旧值
        h_old = self.h.copy()
        u_old = self.u.copy()
        v_old = self.v.copy()
        
        # 计算通量
        F, G = self.compute_fluxes()
        
        # 更新（简化的有限差分）
        for i in range(1, self.ny-1):
            for j in range(1, self.nx-1):
                # 连续方程
                dh_dt = -(F[i, j+1, 0] - F[i, j-1, 0]) / (2*self.dx) - \
                        (G[i+1, j, 0] - G[i-1, j, 0]) / (2*self.dy)
                
                # 动量方程
                if h_old[i, j] > 0.01:
                    # x动量
                    du_dt = -(F[i, j+1, 1] - F[i, j-1, 1]) / (2*self.dx*h_old[i, j]) - \
                            (G[i+1, j, 1] - G[i-1, j, 1]) / (2*self.dy*h_old[i, j]) - \
                            self.g * (self.z[i, j+1] - self.z[i, j-1]) / (2*self.dx)
                    
                    # y动量
                    dv_dt = -(F[i, j+1, 2] - F[i, j-1, 2]) / (2*self.dx*h_old[i, j]) - \
                            (G[i+1, j, 2] - G[i-1, j, 2]) / (2*self.dy*h_old[i, j]) - \
                            self.g * (self.z[i+1, j] - self.z[i-1, j]) / (2*self.dy)
                    
                    # 底部摩擦
                    velocity_mag = np.sqrt(u_old[i, j]**2 + v_old[i, j]**2)
                    if velocity_mag > 0:
                        friction = self.g * manning_n**2 * velocity_mag / h_old[i, j]**(4/3)
                        du_dt -= friction * u_old[i, j]
                        dv_dt -= friction * v_old[i, j]
                    
                    self.u[i, j] = u_old[i, j] + du_dt * dt
                    self.v[i, j] = v_old[i, j] + dv_dt * dt
                
                self.h[i, j] = max(h_old[i, j] + dh_dt * dt, 0)
        
        # 边界条件（简化）
        self.h[0, :] = self.h[1, :]
        self.h[-1, :] = self.h[-2, :]
        self.h[:, 0] = self.h[:, 1]
        self.h[:, -1] = self.h[:, -2]
    
    def simulate(self, 
                total_time: float,
                dt: float = 0.01) -> List[Dict]:
        """运行模拟"""
        results = []
        t = 0
        step = 0
        
        save_interval = max(1, int(total_time / dt / 20))
        
        while t < total_time:
            if step % save_interval == 0:
                results.append({
                    'time': t,
                    'h': self.h.copy(),
                    'u': self.u.copy(),
                    'v': self.v.copy()
                })
            
            self.time_step(dt)
            t += dt
            step += 1
        
        return results


class AgentBasedFish:
    """鱼类行为智能体模型（案例47）
    
    基于个体的鱼类行为模拟
    """
    
    def __init__(self,
                 n_fish: int,
                 domain_size: Tuple[float, float]):
        """
        Parameters:
        -----------
        n_fish : int
            鱼的数量
        domain_size : Tuple[float, float]
            区域大小 (m)
        """
        self.n_fish = n_fish
        self.domain_size = domain_size
        
        # 初始化鱼的位置和速度
        self.positions = np.random.rand(n_fish, 2) * np.array(domain_size)
        self.velocities = (np.random.rand(n_fish, 2) - 0.5) * 0.5
        
        # 鱼的属性
        self.body_length = 0.3  # m
        self.max_speed = 1.5  # m/s
        self.stamina = np.ones(n_fish)
    
    def flow_field(self, x: float, y: float) -> Tuple[float, float]:
        """流场速度（简化）"""
        u = 0.5 + 0.1 * np.sin(x / 10)
        v = 0.1 * np.cos(y / 10)
        return u, v
    
    def compute_behavior(self, 
                        fish_id: int,
                        neighbor_distance: float = 2.0) -> np.ndarray:
        """计算鱼的行为"""
        pos = self.positions[fish_id]
        vel = self.velocities[fish_id]
        
        # 1. 流体曳力
        u_flow, v_flow = self.flow_field(pos[0], pos[1])
        flow_force = np.array([u_flow - vel[0], v_flow - vel[1]]) * 0.3
        
        # 2. 群聚行为（找邻居）
        distances = np.linalg.norm(self.positions - pos, axis=1)
        neighbors = np.where((distances < neighbor_distance) & (distances > 0))[0]
        
        cohesion_force = np.zeros(2)
        alignment_force = np.zeros(2)
        separation_force = np.zeros(2)
        
        if len(neighbors) > 0:
            # 聚合
            center_of_mass = np.mean(self.positions[neighbors], axis=0)
            cohesion_force = (center_of_mass - pos) * 0.1
            
            # 对齐
            avg_velocity = np.mean(self.velocities[neighbors], axis=0)
            alignment_force = (avg_velocity - vel) * 0.2
            
            # 分离
            for neighbor in neighbors:
                diff = pos - self.positions[neighbor]
                dist = np.linalg.norm(diff)
                if dist < 0.5:
                    separation_force += diff / dist * 0.3
        
        # 3. 边界避免
        boundary_force = np.zeros(2)
        margin = 5.0
        if pos[0] < margin:
            boundary_force[0] = 0.5
        elif pos[0] > self.domain_size[0] - margin:
            boundary_force[0] = -0.5
        if pos[1] < margin:
            boundary_force[1] = 0.5
        elif pos[1] > self.domain_size[1] - margin:
            boundary_force[1] = -0.5
        
        # 总力
        total_force = (flow_force + cohesion_force + alignment_force + 
                      separation_force + boundary_force)
        
        return total_force
    
    def update(self, dt: float = 0.1):
        """更新所有鱼的状态"""
        new_velocities = self.velocities.copy()
        
        for i in range(self.n_fish):
            force = self.compute_behavior(i)
            new_velocities[i] += force * dt
            
            # 限制速度
            speed = np.linalg.norm(new_velocities[i])
            if speed > self.max_speed:
                new_velocities[i] = new_velocities[i] / speed * self.max_speed
        
        self.velocities = new_velocities
        self.positions += self.velocities * dt
        
        # 边界条件
        self.positions[:, 0] = np.clip(self.positions[:, 0], 0, self.domain_size[0])
        self.positions[:, 1] = np.clip(self.positions[:, 1], 0, self.domain_size[1])
    
    def simulate(self, duration: float, dt: float = 0.1) -> List[Dict]:
        """运行模拟"""
        results = []
        t = 0
        steps = int(duration / dt)
        save_interval = max(1, steps // 50)
        
        for step in range(steps):
            if step % save_interval == 0:
                results.append({
                    'time': t,
                    'positions': self.positions.copy(),
                    'velocities': self.velocities.copy()
                })
            
            self.update(dt)
            t += dt
        
        return results


class MLFlowPredictor:
    """机器学习预测生态流量（案例48）
    
    使用简化的机器学习模型
    """
    
    def __init__(self):
        """初始化"""
        self.is_trained = False
        self.weights = None
        self.bias = None
        self.feature_mean = None
        self.feature_std = None
    
    def generate_training_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """生成训练数据"""
        # 特征: [流域面积, 降雨量, 蒸发量, 坡度, 植被覆盖度]
        X = np.random.rand(n_samples, 5)
        X[:, 0] = X[:, 0] * 10000  # 流域面积 (km²)
        X[:, 1] = X[:, 1] * 2000  # 降雨量 (mm)
        X[:, 2] = X[:, 2] * 1500  # 蒸发量 (mm)
        X[:, 3] = X[:, 3] * 30  # 坡度 (%)
        X[:, 4] = X[:, 4]  # 植被覆盖度 (0-1)
        
        # 目标: 生态流量 (m³/s)
        # 简化的经验公式
        y = (X[:, 0] * 0.02 * (X[:, 1] - X[:, 2]) / 365 / 86.4 + 
             np.random.randn(n_samples) * 0.5)
        y = np.maximum(y, 0)
        
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray, learning_rate: float = 0.001, epochs: int = 100):
        """训练模型（简化的线性回归）"""
        # 标准化
        self.feature_mean = np.mean(X, axis=0)
        self.feature_std = np.std(X, axis=0) + 1e-8
        X_norm = (X - self.feature_mean) / self.feature_std
        
        # 初始化权重
        self.weights = np.random.randn(X.shape[1]) * 0.01
        self.bias = 0
        
        # 梯度下降
        m = X.shape[0]
        for epoch in range(epochs):
            # 前向传播
            y_pred = np.dot(X_norm, self.weights) + self.bias
            
            # 计算损失
            loss = np.mean((y_pred - y)**2)
            
            # 反向传播
            dy = (y_pred - y) / m
            dw = np.dot(X_norm.T, dy)
            db = np.sum(dy)
            
            # 更新参数
            self.weights -= learning_rate * dw
            self.bias -= learning_rate * db
        
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测"""
        if not self.is_trained:
            raise ValueError("模型未训练")
        
        X_norm = (X - self.feature_mean) / self.feature_std
        y_pred = np.dot(X_norm, self.weights) + self.bias
        return np.maximum(y_pred, 0)
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict:
        """评估模型"""
        y_pred = self.predict(X_test)
        
        mse = np.mean((y_pred - y_test)**2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_pred - y_test))
        r2 = 1 - np.sum((y_pred - y_test)**2) / np.sum((y_test - np.mean(y_test))**2)
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2
        }


class CFDFishway:
    """CFD鱼道流场模拟（案例49）
    
    简化的CFD模拟
    """
    
    def __init__(self,
                 length: float,
                 width: float,
                 nx: int,
                 ny: int):
        """
        Parameters:
        -----------
        length, width : float
            鱼道尺寸 (m)
        nx, ny : int
            网格数
        """
        self.L = length
        self.W = width
        self.nx = nx
        self.ny = ny
        self.dx = length / nx
        self.dy = width / ny
        
        # 流场
        self.u = np.zeros((ny, nx))  # x方向速度
        self.v = np.zeros((ny, nx))  # y方向速度
        self.p = np.zeros((ny, nx))  # 压力
        
        # 障碍物（挡板）
        self.obstacles = np.zeros((ny, nx), dtype=bool)
    
    def add_baffle(self, x_start: float, y_start: float, 
                  x_end: float, y_end: float):
        """添加挡板"""
        i_start = int(y_start / self.dy)
        i_end = int(y_end / self.dy)
        j_start = int(x_start / self.dx)
        j_end = int(x_end / self.dx)
        
        self.obstacles[i_start:i_end+1, j_start:j_end+1] = True
    
    def solve_flow_field(self, inlet_velocity: float, iterations: int = 100):
        """求解流场（简化SIMPLE算法）"""
        # 设置入口条件
        self.u[:, 0] = inlet_velocity
        
        # 迭代求解
        for _ in range(iterations):
            u_old = self.u.copy()
            v_old = self.v.copy()
            
            # 动量方程（简化）
            for i in range(1, self.ny-1):
                for j in range(1, self.nx-1):
                    if not self.obstacles[i, j]:
                        # x动量
                        self.u[i, j] = 0.25 * (u_old[i+1, j] + u_old[i-1, j] + 
                                              u_old[i, j+1] + u_old[i, j-1])
                        
                        # y动量
                        self.v[i, j] = 0.25 * (v_old[i+1, j] + v_old[i-1, j] + 
                                              v_old[i, j+1] + v_old[i, j-1])
            
            # 边界条件
            self.u[:, 0] = inlet_velocity
            self.u[:, -1] = self.u[:, -2]
            self.v[0, :] = 0
            self.v[-1, :] = 0
    
    def compute_turbulence_intensity(self) -> np.ndarray:
        """计算湍流强度"""
        velocity_mag = np.sqrt(self.u**2 + self.v**2)
        
        # 简化的湍流强度估算
        turbulence = np.zeros_like(velocity_mag)
        for i in range(1, self.ny-1):
            for j in range(1, self.nx-1):
                if not self.obstacles[i, j]:
                    # 速度梯度
                    du_dx = (self.u[i, j+1] - self.u[i, j-1]) / (2*self.dx)
                    dv_dy = (self.v[i+1, j] - self.v[i-1, j]) / (2*self.dy)
                    shear = np.sqrt(du_dx**2 + dv_dy**2)
                    turbulence[i, j] = shear * 0.1
        
        return turbulence
    
    def fish_passage_suitability(self) -> np.ndarray:
        """鱼类通过适宜性"""
        velocity_mag = np.sqrt(self.u**2 + self.v**2)
        turbulence = self.compute_turbulence_intensity()
        
        # 适宜性评分（0-1）
        suitability = np.ones_like(velocity_mag)
        
        # 流速适宜性
        v_optimal = 0.8  # m/s
        suitability *= np.exp(-((velocity_mag - v_optimal) / 0.5)**2)
        
        # 湍流适宜性
        suitability *= np.exp(-(turbulence / 0.2)**2)
        
        # 障碍物区域不适宜
        suitability[self.obstacles] = 0
        
        return suitability


class RemoteSensingGIS:
    """遥感GIS集成分析（案例50）
    
    遥感影像分析与GIS空间分析
    """
    
    def __init__(self,
                 image_size: Tuple[int, int],
                 pixel_size: float):
        """
        Parameters:
        -----------
        image_size : Tuple[int, int]
            影像大小(像素)
        pixel_size : float
            像素分辨率 (m)
        """
        self.rows, self.cols = image_size
        self.pixel_size = pixel_size
        
        # 模拟多光谱影像
        self.bands = {
            'blue': np.random.rand(self.rows, self.cols) * 0.3,
            'green': np.random.rand(self.rows, self.cols) * 0.4,
            'red': np.random.rand(self.rows, self.cols) * 0.3,
            'nir': np.random.rand(self.rows, self.cols) * 0.6
        }
    
    def compute_ndvi(self) -> np.ndarray:
        """计算归一化植被指数"""
        nir = self.bands['nir']
        red = self.bands['red']
        ndvi = (nir - red) / (nir + red + 1e-8)
        return ndvi
    
    def compute_ndwi(self) -> np.ndarray:
        """计算归一化水体指数"""
        green = self.bands['green']
        nir = self.bands['nir']
        ndwi = (green - nir) / (green + nir + 1e-8)
        return ndwi
    
    def classify_land_cover(self) -> Dict[str, np.ndarray]:
        """土地覆盖分类"""
        ndvi = self.compute_ndvi()
        ndwi = self.compute_ndwi()
        
        # 简单阈值分类
        water = ndwi > 0.3
        vegetation = (ndvi > 0.3) & (~water)
        bare_land = (ndvi < 0.1) & (~water)
        urban = ~(water | vegetation | bare_land)
        
        return {
            'water': water,
            'vegetation': vegetation,
            'bare_land': bare_land,
            'urban': urban
        }
    
    def compute_area_statistics(self) -> Dict[str, float]:
        """计算面积统计"""
        classification = self.classify_land_cover()
        pixel_area = (self.pixel_size ** 2) / 1e6  # km²
        
        stats = {}
        for class_name, mask in classification.items():
            area = np.sum(mask) * pixel_area
            percentage = np.sum(mask) / mask.size * 100
            stats[class_name] = {
                'area_km2': area,
                'percentage': percentage
            }
        
        return stats
    
    def buffer_analysis(self, 
                       water_mask: np.ndarray,
                       buffer_distance: float) -> np.ndarray:
        """缓冲区分析"""
        buffer_pixels = int(buffer_distance / self.pixel_size)
        
        # 简化的缓冲区（膨胀操作）
        buffer_zone = water_mask.copy()
        for _ in range(buffer_pixels):
            padded = np.pad(buffer_zone, 1, mode='edge')
            buffer_zone = (padded[:-2, 1:-1] | padded[2:, 1:-1] | 
                          padded[1:-1, :-2] | padded[1:-1, 2:] | 
                          buffer_zone)
        
        return buffer_zone
    
    def watershed_delineation(self, dem: np.ndarray) -> np.ndarray:
        """流域划分（简化）"""
        # 计算坡度
        gradient_x = np.gradient(dem, axis=1)
        gradient_y = np.gradient(dem, axis=0)
        slope = np.sqrt(gradient_x**2 + gradient_y**2)
        
        # 简化的汇流累积
        flow_accumulation = np.zeros_like(dem)
        
        for i in range(1, self.rows-1):
            for j in range(1, self.cols-1):
                # 找最陡下降方向
                neighbors = [
                    (i-1, j-1), (i-1, j), (i-1, j+1),
                    (i, j-1), (i, j+1),
                    (i+1, j-1), (i+1, j), (i+1, j+1)
                ]
                
                min_elevation = dem[i, j]
                target = (i, j)
                
                for ni, nj in neighbors:
                    if dem[ni, nj] < min_elevation:
                        min_elevation = dem[ni, nj]
                        target = (ni, nj)
                
                if target != (i, j):
                    flow_accumulation[target] += 1
        
        return flow_accumulation


def simulate_fishway_optimization(length: float,
                                  width: float,
                                  n_baffles: int) -> Dict:
    """优化鱼道设计"""
    fishway = CFDFishway(length, width, 50, 20)
    
    # 添加挡板
    spacing = length / (n_baffles + 1)
    for i in range(n_baffles):
        x = (i + 1) * spacing
        # 交错布置
        if i % 2 == 0:
            fishway.add_baffle(x, width*0.2, x+0.2, width*0.8)
        else:
            fishway.add_baffle(x, 0, x+0.2, width*0.6)
    
    # 求解流场
    fishway.solve_flow_field(2.0, 200)
    
    # 评估
    suitability = fishway.fish_passage_suitability()
    avg_suitability = np.mean(suitability[~fishway.obstacles])
    
    velocity_mag = np.sqrt(fishway.u**2 + fishway.v**2)
    max_velocity = np.max(velocity_mag)
    
    return {
        'average_suitability': avg_suitability,
        'max_velocity': max_velocity,
        'n_baffles': n_baffles,
        'u_field': fishway.u,
        'v_field': fishway.v,
        'suitability': suitability
    }
