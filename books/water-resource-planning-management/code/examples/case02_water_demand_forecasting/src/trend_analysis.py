"""
趋势分析预测模块
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
from scipy import optimize


class TrendForecaster:
    """
    趋势外推预测器
    
    支持多种趋势模型：线性、指数、对数、多项式
    """
    
    def __init__(self, method: str = "linear"):
        """
        初始化
        
        Parameters
        ----------
        method : str
            趋势类型：'linear', 'exponential', 'logarithmic', 'polynomial'
        """
        self.method = method
        self.params = None
        self.x_train = None
        self.y_train = None
    
    def fit(self, years: np.ndarray, values: np.ndarray):
        """
        拟合趋势模型
        
        Parameters
        ----------
        years : np.ndarray
            年份数组
        values : np.ndarray
            观测值数组
        """
        self.x_train = years
        self.y_train = values
        
        # 标准化x（以第一年为基准）
        x = years - years[0]
        y = values
        
        if self.method == "linear":
            # y = a + b*x
            self.params = np.polyfit(x, y, 1)
        
        elif self.method == "exponential":
            # y = a * exp(b*x)
            # 转换为 ln(y) = ln(a) + b*x
            # 使用非线性最小二乘拟合
            def exp_func(x, a, b):
                return a * np.exp(b * x)
            
            try:
                popt, _ = optimize.curve_fit(exp_func, x, y, p0=[y[0], 0.01])
                self.params = popt
            except:
                # 如果拟合失败，使用线性近似
                self.params = np.polyfit(x, y, 1)
                self.method = "linear"
        
        elif self.method == "logarithmic":
            # y = a + b*ln(x+1)
            log_x = np.log(x + 1)
            self.params = np.polyfit(log_x, y, 1)
        
        elif self.method == "polynomial":
            # y = a + b*x + c*x^2
            self.params = np.polyfit(x, y, 2)
        
        else:
            raise ValueError(f"不支持的趋势类型: {self.method}")
    
    def predict(self, years: np.ndarray) -> np.ndarray:
        """
        预测未来值
        
        Parameters
        ----------
        years : np.ndarray
            要预测的年份
        
        Returns
        -------
        np.ndarray
            预测值
        """
        if self.params is None:
            raise ValueError("模型未训练，请先调用fit()")
        
        # 标准化x
        x = years - self.x_train[0]
        
        if self.method == "linear":
            predictions = np.polyval(self.params, x)
        
        elif self.method == "exponential":
            a, b = self.params
            predictions = a * np.exp(b * x)
        
        elif self.method == "logarithmic":
            log_x = np.log(x + 1)
            predictions = np.polyval(self.params, log_x)
        
        elif self.method == "polynomial":
            predictions = np.polyval(self.params, x)
        
        return predictions
    
    def score(self) -> float:
        """
        计算拟合优度 R²
        
        Returns
        -------
        float
            R² 值
        """
        if self.params is None:
            raise ValueError("模型未训练")
        
        y_pred = self.predict(self.x_train)
        ss_res = np.sum((self.y_train - y_pred) ** 2)
        ss_tot = np.sum((self.y_train - np.mean(self.y_train)) ** 2)
        
        return 1 - (ss_res / ss_tot)
    
    def get_equation(self) -> str:
        """
        获取拟合方程的字符串表示
        
        Returns
        -------
        str
            方程字符串
        """
        if self.params is None:
            return "未训练"
        
        if self.method == "linear":
            a, b = self.params
            return f"y = {a:.2f} + {b:.2f}*x"
        
        elif self.method == "exponential":
            a, b = self.params
            return f"y = {a:.2f} * exp({b:.4f}*x)"
        
        elif self.method == "logarithmic":
            a, b = self.params
            return f"y = {a:.2f} + {b:.2f}*ln(x+1)"
        
        elif self.method == "polynomial":
            a, b, c = self.params
            return f"y = {a:.2f} + {b:.2f}*x + {c:.4f}*x²"
        
        return "Unknown"


def compare_trends(
    years: np.ndarray,
    values: np.ndarray,
    forecast_years: np.ndarray
) -> pd.DataFrame:
    """
    比较不同趋势模型的预测结果
    
    Parameters
    ----------
    years : np.ndarray
        历史年份
    values : np.ndarray
        历史观测值
    forecast_years : np.ndarray
        要预测的年份
    
    Returns
    -------
    pd.DataFrame
        各模型的预测结果
    """
    methods = ["linear", "exponential", "logarithmic", "polynomial"]
    results = {"year": forecast_years}
    scores = {}
    
    for method in methods:
        forecaster = TrendForecaster(method=method)
        try:
            forecaster.fit(years, values)
            predictions = forecaster.predict(forecast_years)
            results[method] = predictions
            scores[method] = forecaster.score()
        except Exception as e:
            print(f"警告：{method} 方法拟合失败: {e}")
            results[method] = np.nan
            scores[method] = np.nan
    
    df = pd.DataFrame(results)
    
    # 打印拟合优度
    print("\n趋势模型拟合优度（R²）：")
    for method, score in scores.items():
        if not np.isnan(score):
            print(f"  {method}: {score:.4f}")
    
    return df
