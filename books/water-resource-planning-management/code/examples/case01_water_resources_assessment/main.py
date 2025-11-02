"""
案例1.1：流域水资源调查与评价 - 主程序

本程序实现流域水资源的全面评价，包括：
1. 统计分析
2. 频率分析
3. 可利用水资源量计算
4. 结果可视化

作者：教材编写组
日期：2025-11-02
"""

import sys
import os

# 添加core模块到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 导入核心模块
from core.utils.data_io import load_csv, load_yaml, save_csv
from core.utils.statistics import (
    calculate_statistics,
    pearson_iii_distribution,
    frequency_analysis,
    calculate_exceedance_probability,
)
from core.utils.visualization import (
    plot_series,
    plot_frequency_curve,
    plot_bar_chart,
)


class WaterResourcesAssessment:
    """
    水资源评价类
    
    完成流域水资源的全面评价
    """
    
    def __init__(self, data_dir: str = "data", results_dir: str = "results"):
        """
        初始化
        
        Parameters
        ----------
        data_dir : str
            数据目录
        results_dir : str
            结果输出目录
        """
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 数据存储
        self.annual_runoff = None
        self.monthly_runoff = None
        self.basin_params = None
        self.statistics = None
        self.frequency_results = None
    
    def load_data(self):
        """
        加载数据
        """
        print("=" * 60)
        print("步骤1: 加载数据")
        print("=" * 60)
        
        # 加载年径流数据
        self.annual_runoff = load_csv(self.data_dir / "runoff_series.csv")
        print(f"\n已加载年径流数据: {len(self.annual_runoff)} 年")
        print(f"数据范围: {self.annual_runoff['year'].min()}-{self.annual_runoff['year'].max()}")
        
        # 加载月径流数据
        self.monthly_runoff = load_csv(self.data_dir / "monthly_runoff.csv")
        print(f"已加载月径流数据: {len(self.monthly_runoff)} 月")
        
        # 加载流域参数
        self.basin_params = load_yaml(self.data_dir / "basin_parameters.yaml")
        print(f"\n流域基本信息:")
        print(f"  流域名称: {self.basin_params['basin_name']}")
        print(f"  流域面积: {self.basin_params['area']} km²")
        print(f"  主河道长度: {self.basin_params['river_length']} km")
    
    def statistical_analysis(self):
        """
        统计分析
        """
        print("\n" + "=" * 60)
        print("步骤2: 统计分析")
        print("=" * 60)
        
        # 计算统计量
        runoff_data = self.annual_runoff['runoff'].values
        self.statistics = calculate_statistics(runoff_data)
        
        print(f"\n基本统计量:")
        print(f"  多年平均径流量: {self.statistics['mean']:.2f} 亿m³")
        print(f"  标准差: {self.statistics['std']:.2f} 亿m³")
        print(f"  变差系数 Cv: {self.statistics['cv']:.3f}")
        print(f"  偏态系数 Cs: {self.statistics['cs']:.3f}")
        print(f"  最大值: {self.statistics['max']:.2f} 亿m³")
        print(f"  最小值: {self.statistics['min']:.2f} 亿m³")
        print(f"  中位数: {self.statistics['median']:.2f} 亿m³")
        
        # 保存统计结果
        stats_df = pd.DataFrame([self.statistics])
        save_csv(stats_df, self.results_dir / "statistics_summary.csv")
    
    def perform_frequency_analysis(self):
        """
        频率分析
        """
        print("\n" + "=" * 60)
        print("步骤3: 频率分析 (Pearson-III型分布)")
        print("=" * 60)
        
        runoff_data = self.annual_runoff['runoff'].values
        
        # Pearson-III分布参数估计
        mean, cv, cs = pearson_iii_distribution(runoff_data)
        print(f"\nPearson-III型分布参数:")
        print(f"  均值: {mean:.2f} 亿m³")
        print(f"  Cv: {cv:.3f}")
        print(f"  Cs: {cs:.3f}")
        
        # 频率计算
        design_probs = self.basin_params['design_frequencies']
        probs, design_values = frequency_analysis(
            runoff_data,
            probabilities=design_probs,
            distribution='pearson3'
        )
        
        print(f"\n不同保证率设计值:")
        for p, q in zip(probs, design_values):
            print(f"  P={p*100:.0f}%: {q:.2f} 亿m³")
        
        # 保存频率分析结果
        freq_df = pd.DataFrame({
            'probability_pct': probs * 100,
            'design_value': design_values
        })
        save_csv(freq_df, self.results_dir / "frequency_analysis.csv")
        
        self.frequency_results = {
            'probs': probs,
            'design_values': design_values
        }
    
    def calculate_available_water(self):
        """
        计算可利用水资源量
        """
        print("\n" + "=" * 60)
        print("步骤4: 可利用水资源量计算")
        print("=" * 60)
        
        ecological_ratio = self.basin_params['ecological_flow_ratio']
        loss_ratio = self.basin_params['loss_ratio']
        
        # 多年平均可利用量
        mean_runoff = self.statistics['mean']
        available_mean = mean_runoff * (1 - ecological_ratio - loss_ratio)
        
        print(f"\n多年平均径流量: {mean_runoff:.2f} 亿m³")
        print(f"扣除生态基流 ({ecological_ratio*100:.0f}%): {mean_runoff * ecological_ratio:.2f} 亿m³")
        print(f"扣除损失 ({loss_ratio*100:.0f}%): {mean_runoff * loss_ratio:.2f} 亿m³")
        print(f"可利用水资源量: {available_mean:.2f} 亿m³")
        
        # 不同保证率的可利用量
        print(f"\n不同保证率可利用水量:")
        available_results = []
        for p, q in zip(self.frequency_results['probs'], 
                       self.frequency_results['design_values']):
            available_q = q * (1 - ecological_ratio - loss_ratio)
            print(f"  P={p*100:.0f}%: {available_q:.2f} 亿m³")
            available_results.append({
                'probability_pct': p * 100,
                'total_runoff': q,
                'available_water': available_q
            })
        
        # 保存可利用量结果
        available_df = pd.DataFrame(available_results)
        save_csv(available_df, self.results_dir / "available_water.csv")
    
    def analyze_temporal_distribution(self):
        """
        分析时间分布特征
        """
        print("\n" + "=" * 60)
        print("步骤5: 时间分布特征分析")
        print("=" * 60)
        
        # 年际变化
        runoff_data = self.annual_runoff['runoff'].values
        max_year_idx = np.argmax(runoff_data)
        min_year_idx = np.argmin(runoff_data)
        
        print(f"\n年际变化:")
        print(f"  最大年份: {self.annual_runoff.iloc[max_year_idx]['year']}, "
              f"径流量: {runoff_data[max_year_idx]:.2f} 亿m³")
        print(f"  最小年份: {self.annual_runoff.iloc[min_year_idx]['year']}, "
              f"径流量: {runoff_data[min_year_idx]:.2f} 亿m³")
        print(f"  最大/最小比值: {runoff_data[max_year_idx] / runoff_data[min_year_idx]:.2f}")
        
        # 年内分配
        monthly_data = self.monthly_runoff['runoff'].values
        flood_season = monthly_data[5:9].sum()  # 6-9月
        dry_season = monthly_data[[0,1,2,3,4,9,10,11]].sum()  # 其他月份
        
        print(f"\n年内分配:")
        print(f"  汛期(6-9月)径流量: {flood_season:.2f} 亿m³ "
              f"({flood_season/monthly_data.sum()*100:.1f}%)")
        print(f"  非汛期径流量: {dry_season:.2f} 亿m³ "
              f"({dry_season/monthly_data.sum()*100:.1f}%)")
        
        # 不均匀系数
        monthly_ratio = self.monthly_runoff['ratio'].values
        unevenness_coef = np.std(monthly_ratio) / np.mean(monthly_ratio)
        print(f"  年内分配不均匀系数: {unevenness_coef:.3f}")
    
    def visualize_results(self):
        """
        结果可视化
        """
        print("\n" + "=" * 60)
        print("步骤6: 结果可视化")
        print("=" * 60)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 径流序列图
        print("\n绘制径流序列图...")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(self.annual_runoff['year'], self.annual_runoff['runoff'], 
                linewidth=1.5, marker='o', markersize=4)
        ax.axhline(y=self.statistics['mean'], color='r', linestyle='--', 
                   label=f'多年平均 ({self.statistics["mean"]:.2f} 亿m³)')
        ax.set_title('年径流序列', fontsize=14, fontweight='bold')
        ax.set_xlabel('年份', fontsize=12)
        ax.set_ylabel('径流量 (亿m³)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/runoff_series.png", dpi=300)
        print(f"  已保存: {self.results_dir}/figures/runoff_series.png")
        plt.close()
        
        # 2. 频率曲线
        print("绘制频率曲线...")
        runoff_data = self.annual_runoff['runoff'].values
        emp_data, emp_probs = calculate_exceedance_probability(runoff_data)
        
        plot_frequency_curve(
            empirical_data=emp_data,
            empirical_probs=emp_probs,
            theoretical_probs=self.frequency_results['probs'],
            theoretical_values=self.frequency_results['design_values'],
            title='年径流频率曲线 (Pearson-III型)',
            ylabel='年径流量 (亿m³)',
            save_path=self.results_dir / "figures/frequency_curve.png"
        )
        
        # 3. 月径流分配图
        print("绘制月径流分配图...")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 柱状图
        months = self.monthly_runoff['month'].values
        monthly_runoff = self.monthly_runoff['runoff'].values
        ax1.bar(months, monthly_runoff, color='steelblue', alpha=0.7)
        ax1.set_title('月径流分配', fontsize=12, fontweight='bold')
        ax1.set_xlabel('月份', fontsize=11)
        ax1.set_ylabel('径流量 (亿m³)', fontsize=11)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 饼图
        season_labels = ['汛期\n(6-9月)', '非汛期']
        flood_season_runoff = monthly_runoff[5:9].sum()
        dry_season_runoff = monthly_runoff[[0,1,2,3,4,9,10,11]].sum()
        season_values = [flood_season_runoff, dry_season_runoff]
        
        ax2.pie(season_values, labels=season_labels, autopct='%1.1f%%',
                startangle=90, colors=['coral', 'lightblue'])
        ax2.set_title('汛期与非汛期分配', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/monthly_distribution.png", dpi=300)
        print(f"  已保存: {self.results_dir}/figures/monthly_distribution.png")
        plt.close()
    
    def generate_report(self):
        """
        生成评价报告
        """
        print("\n" + "=" * 60)
        print("步骤7: 生成评价报告")
        print("=" * 60)
        
        report_path = self.results_dir / "assessment_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write(" " * 20 + "流域水资源评价报告\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"流域名称: {self.basin_params['basin_name']}\n")
            f.write(f"流域面积: {self.basin_params['area']} km²\n")
            f.write(f"评价时间: 2025-11-02\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("一、基本统计量\n")
            f.write("-" * 70 + "\n")
            f.write(f"多年平均径流量: {self.statistics['mean']:.2f} 亿m³\n")
            f.write(f"标准差: {self.statistics['std']:.2f} 亿m³\n")
            f.write(f"变差系数 Cv: {self.statistics['cv']:.3f}\n")
            f.write(f"偏态系数 Cs: {self.statistics['cs']:.3f}\n")
            f.write(f"最大值: {self.statistics['max']:.2f} 亿m³\n")
            f.write(f"最小值: {self.statistics['min']:.2f} 亿m³\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("二、频率分析结果 (Pearson-III型分布)\n")
            f.write("-" * 70 + "\n")
            for p, q in zip(self.frequency_results['probs'], 
                           self.frequency_results['design_values']):
                f.write(f"P={p*100:.0f}%: {q:.2f} 亿m³\n")
            f.write("\n")
            
            f.write("-" * 70 + "\n")
            f.write("三、可利用水资源量\n")
            f.write("-" * 70 + "\n")
            ecological_ratio = self.basin_params['ecological_flow_ratio']
            loss_ratio = self.basin_params['loss_ratio']
            mean_runoff = self.statistics['mean']
            available_mean = mean_runoff * (1 - ecological_ratio - loss_ratio)
            f.write(f"多年平均可利用量: {available_mean:.2f} 亿m³\n")
            for p, q in zip(self.frequency_results['probs'], 
                           self.frequency_results['design_values']):
                available_q = q * (1 - ecological_ratio - loss_ratio)
                f.write(f"P={p*100:.0f}% 可利用量: {available_q:.2f} 亿m³\n")
            f.write("\n")
            
            f.write("-" * 70 + "\n")
            f.write("四、结论与建议\n")
            f.write("-" * 70 + "\n")
            f.write(f"1. 该流域多年平均径流量为{self.statistics['mean']:.2f}亿m³，\n")
            f.write(f"   水资源量处于中等水平。\n\n")
            f.write(f"2. 考虑生态基流和损失后，多年平均可利用水量为{available_mean:.2f}亿m³。\n\n")
            f.write(f"3. 径流的年际变化较{('小' if self.statistics['cv'] < 0.3 else '大')}，\n")
            f.write(f"   Cv={self.statistics['cv']:.3f}。\n\n")
            f.write(f"4. 建议加强水资源调蓄工程建设，提高水资源保障能力。\n\n")
        
        print(f"评价报告已生成: {report_path}")
    
    def run(self):
        """
        运行完整评价流程
        """
        print("\n")
        print("*" * 70)
        print(" " * 15 + "流域水资源调查与评价系统")
        print(" " * 25 + "案例1.1")
        print("*" * 70)
        
        try:
            self.load_data()
            self.statistical_analysis()
            self.perform_frequency_analysis()
            self.calculate_available_water()
            self.analyze_temporal_distribution()
            self.visualize_results()
            self.generate_report()
            
            print("\n" + "=" * 60)
            print("评价完成！")
            print("=" * 60)
            print(f"\n结果文件位置: {self.results_dir.absolute()}")
            print("\n生成的文件:")
            print("  1. statistics_summary.csv - 统计量汇总")
            print("  2. frequency_analysis.csv - 频率分析结果")
            print("  3. available_water.csv - 可利用水量")
            print("  4. assessment_report.txt - 评价报告")
            print("  5. figures/runoff_series.png - 径流序列图")
            print("  6. figures/frequency_curve.png - 频率曲线")
            print("  7. figures/monthly_distribution.png - 月径流分配图")
            print("\n")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """
    主函数
    """
    # 创建评价对象并运行
    assessment = WaterResourcesAssessment(
        data_dir="data",
        results_dir="results"
    )
    assessment.run()


if __name__ == "__main__":
    main()
