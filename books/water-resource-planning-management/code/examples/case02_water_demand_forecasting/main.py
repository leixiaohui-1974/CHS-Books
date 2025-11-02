"""
案例1.2：城市需水预测 - 主程序

综合运用多种预测方法，进行城市需水量预测和情景分析

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

# 添加core模块到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 导入核心模块
from core.utils.data_io import load_csv, load_yaml, save_csv
from core.utils.visualization import plot_series, plot_comparison

# 导入本案例的预测模块
from src.quota_method import QuotaForecaster
from src.trend_analysis import TrendForecaster, compare_trends
from src.grey_model import GreyForecaster


class WaterDemandForecaster:
    """
    城市需水预测系统
    """
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results"):
        """初始化"""
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        self.historical_data = None
        self.params = None
        self.forecast_results = {}
    
    def load_data(self):
        """加载数据"""
        print("=" * 70)
        print("步骤1: 加载数据")
        print("=" * 70)
        
        self.historical_data = load_csv(self.data_dir / "historical_data.csv")
        self.params = load_yaml(self.data_dir / "forecast_parameters.yaml")
        
        print(f"\n已加载历史数据: {len(self.historical_data)} 年")
        print(f"数据范围: {self.historical_data['year'].min()}-{self.historical_data['year'].max()}")
        print(f"\n预测年份: {self.params['forecast_years']}")
    
    def method1_quota(self):
        """方法1：定额法预测"""
        print("\n" + "=" * 70)
        print("步骤2: 定额法预测")
        print("=" * 70)
        
        # 创建预测器
        quota_params = self.params['quota_method']
        forecaster = QuotaForecaster(
            domestic_quota=quota_params['domestic_quota'],
            industrial_quota=quota_params['industrial_quota'],
            service_quota=quota_params['service_quota']
        )
        
        # 基准年数据
        base_year_data = self.historical_data[
            self.historical_data['year'] == self.params['base_year']
        ].iloc[0]
        
        # 预测未来（中等增长情景）
        scenario = self.params['scenarios']['medium_growth']
        forecast_years = self.params['forecast_years']
        n_years = len(forecast_years)
        base_year = self.params['base_year']
        
        # 推算未来人口和经济指标
        population_forecast = []
        industrial_forecast = []
        service_forecast = []
        
        for year in forecast_years:
            years_ahead = year - base_year
            # 人口增长
            pop = base_year_data['population'] * (1 + scenario['population_growth_rate']) ** years_ahead
            population_forecast.append(pop)
            
            # 工业增加值增长
            ind = base_year_data['industrial_output'] * (1 + scenario['gdp_growth_rate']) ** years_ahead
            industrial_forecast.append(ind)
            
            # 服务业增加值（假设与GDP同步）
            gdp = base_year_data['gdp'] * (1 + scenario['gdp_growth_rate']) ** years_ahead
            service = gdp - ind  # 简化假设
            service_forecast.append(service)
        
        # 预测需水量
        results = forecaster.forecast_series(
            years=forecast_years,
            population_series=population_forecast,
            industrial_output_series=industrial_forecast,
            service_output_series=service_forecast,
            water_saving_factor=scenario['water_saving_factor']
        )
        
        self.forecast_results['quota'] = results
        
        print(f"\n定额法预测结果:")
        print(f"  人均生活用水定额: {quota_params['domestic_quota']} L/人·日")
        print(f"  节水系数: {scenario['water_saving_factor']}")
        print(f"\n2025年预测:")
        row_2025 = results[results['year'] == 2025].iloc[0]
        print(f"  生活需水: {row_2025['domestic']:.2f} 万m³/d")
        print(f"  工业需水: {row_2025['industrial']:.2f} 万m³/d")
        print(f"  服务业需水: {row_2025['service']:.2f} 万m³/d")
        print(f"  总需水: {row_2025['total']:.2f} 万m³/d")
    
    def method2_trend(self):
        """方法2：趋势分析法预测"""
        print("\n" + "=" * 70)
        print("步骤3: 趋势分析法预测")
        print("=" * 70)
        
        years = self.historical_data['year'].values
        demand = self.historical_data['water_demand'].values
        forecast_years = np.array(self.params['forecast_years'])
        
        # 线性趋势预测
        forecaster = TrendForecaster(method='linear')
        forecaster.fit(years, demand)
        linear_pred = forecaster.predict(forecast_years)
        r2 = forecaster.score()
        
        print(f"\n线性趋势预测:")
        print(f"  拟合方程: {forecaster.get_equation()}")
        print(f"  R² = {r2:.4f}")
        
        # 保存结果
        self.forecast_results['trend_linear'] = pd.DataFrame({
            'year': forecast_years,
            'total': linear_pred
        })
        
        print(f"\n2025年预测: {linear_pred[0]:.2f} 万m³/d")
    
    def method3_grey(self):
        """方法3：灰色预测GM(1,1)"""
        print("\n" + "=" * 70)
        print("步骤4: 灰色预测GM(1,1)")
        print("=" * 70)
        
        # 使用历史数据
        demand = self.historical_data['water_demand'].values
        
        # 创建模型
        model = GreyForecaster()
        model.fit(demand)
        
        # 预测
        base_year = self.params['base_year']
        forecast_years = self.params['forecast_years']
        steps = forecast_years[-1] - base_year
        
        all_pred = model.predict(steps)
        
        # 提取预测年份的值
        base_year_idx = len(demand) - 1
        forecast_values = []
        for year in forecast_years:
            idx = base_year_idx + (year - base_year)
            if idx < len(all_pred):
                forecast_values.append(all_pred[idx])
        
        # 精度检验
        mre, C, grade = model.accuracy_test()
        params = model.get_params()
        
        print(f"\nGM(1,1)模型:")
        print(f"  {params['equation']}")
        print(f"\n精度检验:")
        print(f"  平均相对误差: {mre:.4f}")
        print(f"  后验差比 C: {C:.4f}")
        print(f"  精度等级: {grade}")
        
        # 保存结果
        self.forecast_results['grey'] = pd.DataFrame({
            'year': forecast_years[:len(forecast_values)],
            'total': forecast_values
        })
        
        if len(forecast_values) > 0:
            print(f"\n2025年预测: {forecast_values[0]:.2f} 万m³/d")
    
    def method4_ensemble(self):
        """方法4：组合预测"""
        print("\n" + "=" * 70)
        print("步骤5: 组合预测")
        print("=" * 70)
        
        # 获取各方法的预测结果
        quota_pred = self.forecast_results['quota']['total'].values
        trend_pred = self.forecast_results['trend_linear']['total'].values
        grey_pred = self.forecast_results['grey']['total'].values
        
        # 简单平均（等权重）
        ensemble_pred = (quota_pred + trend_pred + grey_pred) / 3
        
        # 保存结果
        forecast_years = self.params['forecast_years']
        self.forecast_results['ensemble'] = pd.DataFrame({
            'year': forecast_years,
            'quota': quota_pred,
            'trend': trend_pred,
            'grey': grey_pred,
            'ensemble': ensemble_pred
        })
        
        print(f"\n组合预测方法: 等权重平均")
        print(f"\n2025年预测结果对比:")
        print(f"  定额法: {quota_pred[0]:.2f} 万m³/d")
        print(f"  趋势法: {trend_pred[0]:.2f} 万m³/d")
        print(f"  灰色法: {grey_pred[0]:.2f} 万m³/d")
        print(f"  组合预测: {ensemble_pred[0]:.2f} 万m³/d")
    
    def scenario_analysis(self):
        """情景分析"""
        print("\n" + "=" * 70)
        print("步骤6: 情景分析")
        print("=" * 70)
        
        scenarios = self.params['scenarios']
        base_year_data = self.historical_data[
            self.historical_data['year'] == self.params['base_year']
        ].iloc[0]
        
        quota_params = self.params['quota_method']
        
        scenario_results = {}
        
        for scenario_name, scenario in scenarios.items():
            forecaster = QuotaForecaster(
                domestic_quota=quota_params['domestic_quota'],
                industrial_quota=quota_params['industrial_quota'],
                service_quota=quota_params['service_quota']
            )
            
            forecast_years = self.params['forecast_years']
            base_year = self.params['base_year']
            
            # 推算社会经济指标
            population_forecast = []
            industrial_forecast = []
            service_forecast = []
            
            for year in forecast_years:
                years_ahead = year - base_year
                pop = base_year_data['population'] * (1 + scenario['population_growth_rate']) ** years_ahead
                population_forecast.append(pop)
                
                ind = base_year_data['industrial_output'] * (1 + scenario['gdp_growth_rate']) ** years_ahead
                industrial_forecast.append(ind)
                
                gdp = base_year_data['gdp'] * (1 + scenario['gdp_growth_rate']) ** years_ahead
                service = gdp - ind
                service_forecast.append(service)
            
            # 预测
            results = forecaster.forecast_series(
                years=forecast_years,
                population_series=population_forecast,
                industrial_output_series=industrial_forecast,
                service_output_series=service_forecast,
                water_saving_factor=scenario['water_saving_factor']
            )
            
            scenario_results[scenario_name] = results['total'].values
            
            print(f"\n{scenario['name']}:")
            print(f"  2025年: {results[results['year']==2025]['total'].values[0]:.2f} 万m³/d")
            print(f"  2035年: {results[results['year']==2035]['total'].values[0]:.2f} 万m³/d")
            print(f"  2050年: {results[results['year']==2050]['total'].values[0]:.2f} 万m³/d")
        
        # 保存情景分析结果
        scenario_df = pd.DataFrame({
            'year': forecast_years,
            **scenario_results
        })
        save_csv(scenario_df, self.results_dir / "scenario_analysis.csv")
    
    def visualize(self):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("步骤7: 结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 历史趋势图
        print("\n绘制历史趋势图...")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(self.historical_data['year'], self.historical_data['water_demand'],
                marker='o', linewidth=2, label='历史数据')
        ax.set_title('城市需水量历史趋势', fontsize=14, fontweight='bold')
        ax.set_xlabel('年份', fontsize=12)
        ax.set_ylabel('需水量 (万m³/d)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/historical_trend.png", dpi=300)
        plt.close()
        
        # 2. 方法对比图
        print("绘制预测方法对比图...")
        ensemble_df = self.forecast_results['ensemble']
        
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.plot(self.historical_data['year'], self.historical_data['water_demand'],
                'o-', linewidth=2, label='历史数据', color='black')
        ax.plot(ensemble_df['year'], ensemble_df['quota'], 's-', label='定额法')
        ax.plot(ensemble_df['year'], ensemble_df['trend'], '^-', label='趋势法')
        ax.plot(ensemble_df['year'], ensemble_df['grey'], 'd-', label='灰色法')
        ax.plot(ensemble_df['year'], ensemble_df['ensemble'], 'o-', 
                linewidth=3, label='组合预测', color='red')
        
        ax.set_title('不同预测方法对比', fontsize=14, fontweight='bold')
        ax.set_xlabel('年份', fontsize=12)
        ax.set_ylabel('需水量 (万m³/d)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=10)
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/methods_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: {self.results_dir}/figures/")
    
    def generate_report(self):
        """生成预测报告"""
        print("\n" + "=" * 70)
        print("步骤8: 生成预测报告")
        print("=" * 70)
        
        # 保存预测结果
        ensemble_df = self.forecast_results['ensemble']
        save_csv(ensemble_df, self.results_dir / "forecast_results.csv")
        
        print(f"\n预测结果已保存: {self.results_dir}/forecast_results.csv")
        print(f"情景分析已保存: {self.results_dir}/scenario_analysis.csv")
        print(f"图表已保存: {self.results_dir}/figures/")
    
    def run(self):
        """运行完整预测流程"""
        print("\n" + "*" * 70)
        print(" " * 20 + "城市需水预测系统")
        print(" " * 25 + "案例1.2")
        print("*" * 70)
        
        try:
            self.load_data()
            self.method1_quota()
            self.method2_trend()
            self.method3_grey()
            self.method4_ensemble()
            self.scenario_analysis()
            self.visualize()
            self.generate_report()
            
            print("\n" + "=" * 70)
            print("预测完成！")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    forecaster = WaterDemandForecaster(
        data_dir="data",
        results_dir="results"
    )
    forecaster.run()


if __name__ == "__main__":
    main()
