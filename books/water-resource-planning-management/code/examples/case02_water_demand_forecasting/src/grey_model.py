"""
灰色预测GM(1,1)模块
"""

import numpy as np
from typing import Tuple


class GreyForecaster:
    """
    灰色预测GM(1,1)模型
    
    适用于少数据、不确定性系统的短期预测
    """
    
    def __init__(self):
        """初始化"""
        self.a = None  # 发展系数
        self.u = None  # 灰色作用量
        self.x0 = None  # 原始序列
        self.x1 = None  # 一次累加序列
    
    def fit(self, data: np.ndarray):
        """
        拟合GM(1,1)模型
        
        Parameters
        ----------
        data : np.ndarray
            原始数据序列
        """
        self.x0 = np.array(data)
        n = len(data)
        
        # 1. 一次累加生成
        self.x1 = np.cumsum(self.x0)
        
        # 2. 构造数据矩阵
        z = np.zeros(n - 1)
        for i in range(n - 1):
            z[i] = 0.5 * (self.x1[i] + self.x1[i + 1])
        
        B = np.column_stack([-z, np.ones(n - 1)])
        Y = self.x0[1:].reshape(-1, 1)
        
        # 3. 最小二乘估计参数
        params = np.linalg.inv(B.T @ B) @ B.T @ Y
        self.a = params[0, 0]
        self.u = params[1, 0]
    
    def predict(self, steps: int) -> np.ndarray:
        """
        预测未来值
        
        Parameters
        ----------
        steps : int
            预测步数
        
        Returns
        -------
        np.ndarray
            预测值序列（包含历史拟合值）
        """
        if self.a is None or self.u is None:
            raise ValueError("模型未训练，请先调用fit()")
        
        n = len(self.x0)
        total_steps = n + steps
        
        # 预测累加序列
        x1_pred = np.zeros(total_steps)
        x1_pred[0] = self.x0[0]
        
        for k in range(1, total_steps):
            x1_pred[k] = (self.x0[0] - self.u / self.a) * np.exp(-self.a * k) + self.u / self.a
        
        # 累减还原
        x0_pred = np.zeros(total_steps)
        x0_pred[0] = x1_pred[0]
        for k in range(1, total_steps):
            x0_pred[k] = x1_pred[k] - x1_pred[k - 1]
        
        return x0_pred
    
    def forecast(self, steps: int) -> np.ndarray:
        """
        仅返回未来预测值（不包含历史）
        
        Parameters
        ----------
        steps : int
            预测步数
        
        Returns
        -------
        np.ndarray
            未来预测值
        """
        all_pred = self.predict(steps)
        return all_pred[len(self.x0):]
    
    def accuracy_test(self) -> Tuple[float, float, str]:
        """
        模型精度检验
        
        Returns
        -------
        Tuple[float, float, str]
            (平均相对误差, 后验差比, 精度等级)
        """
        # 预测值（历史期）
        x0_pred = self.predict(0)[:len(self.x0)]
        
        # 平均相对误差
        relative_errors = np.abs((self.x0 - x0_pred) / self.x0)
        mean_relative_error = np.mean(relative_errors)
        
        # 后验差比 C
        residuals = self.x0 - x0_pred
        s1 = np.std(self.x0)  # 原始序列标准差
        s2 = np.std(residuals)  # 残差序列标准差
        C = s2 / s1
        
        # 精度等级判断
        if C < 0.35 and mean_relative_error < 0.01:
            grade = "一级（好）"
        elif C < 0.50 and mean_relative_error < 0.05:
            grade = "二级（合格）"
        elif C < 0.65 and mean_relative_error < 0.10:
            grade = "三级（勉强）"
        else:
            grade = "四级（不合格）"
        
        return mean_relative_error, C, grade
    
    def get_params(self) -> dict:
        """
        获取模型参数
        
        Returns
        -------
        dict
            模型参数字典
        """
        return {
            "a": self.a,
            "u": self.u,
            "equation": f"dx^(1)/dt + {self.a:.4f}*x^(1) = {self.u:.4f}"
        }


def forecast_with_grey(
    historical_data: np.ndarray,
    forecast_steps: int
) -> Tuple[np.ndarray, dict]:
    """
    使用灰色模型进行预测的便捷函数
    
    Parameters
    ----------
    historical_data : np.ndarray
        历史数据
    forecast_steps : int
        预测步数
    
    Returns
    -------
    Tuple[np.ndarray, dict]
        (预测值, 模型信息)
    """
    model = GreyForecaster()
    model.fit(historical_data)
    
    # 预测
    forecast = model.forecast(forecast_steps)
    
    # 精度检验
    mre, C, grade = model.accuracy_test()
    
    # 模型信息
    info = {
        "params": model.get_params(),
        "accuracy": {
            "mean_relative_error": mre,
            "posterior_variance_ratio": C,
            "grade": grade
        }
    }
    
    return forecast, info
