"""
案例4.2：水质异常智能检测 - 主程序

对比统计方法、孤立森林和自编码器

作者：教材编写组
日期：2025-11-02
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

from core.ml import IsolationForestDetector, AutoencoderDetector


class WaterQualityAnomalyDetector:
    """水质异常检测系统"""
    
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        (self.results_dir / "figures").mkdir(exist_ok=True)
        
        # 生成数据
        self.data, self.labels = self._generate_data()
        
        print(f"水质异常检测系统: {len(self.data)}个样本")
        print(f"  正常样本: {np.sum(self.labels == 1)}")
        print(f"  异常样本: {np.sum(self.labels == -1)}")
    
    def _generate_data(self, n_samples=1000, anomaly_ratio=0.05):
        """
        生成水质监测数据
        
        特征：pH, 浊度, 余氯, 电导率, 温度
        """
        np.random.seed(42)
        
        n_anomalies = int(n_samples * anomaly_ratio)
        n_normal = n_samples - n_anomalies
        
        # 正常数据（多元正态分布）
        mean_normal = [7.5, 0.3, 0.8, 500, 20]  # pH, 浊度, 余氯, 电导率, 温度
        cov_normal = np.diag([0.3, 0.05, 0.2, 50, 3]) ** 2
        
        normal_data = np.random.multivariate_normal(mean_normal, cov_normal, n_normal)
        normal_labels = np.ones(n_normal)
        
        # 异常数据（偏离正常范围）
        anomaly_data = []
        
        for _ in range(n_anomalies):
            anomaly_type = np.random.choice(['point', 'contextual'])
            
            if anomaly_type == 'point':
                # 点异常：某个指标严重偏离
                sample = mean_normal.copy()
                anomaly_idx = np.random.randint(5)
                sample[anomaly_idx] += np.random.choice([-1, 1]) * np.random.uniform(3, 5) * np.sqrt(cov_normal[anomaly_idx, anomaly_idx])
            else:
                # 上下文异常：多个指标轻微偏离
                sample = mean_normal + np.random.randn(5) * 2 * np.sqrt(np.diag(cov_normal))
            
            anomaly_data.append(sample)
        
        anomaly_data = np.array(anomaly_data)
        anomaly_labels = -np.ones(n_anomalies)
        
        # 合并数据
        data = np.vstack([normal_data, anomaly_data])
        labels = np.concatenate([normal_labels, anomaly_labels])
        
        # 打乱顺序
        indices = np.random.permutation(n_samples)
        data = data[indices]
        labels = labels[indices]
        
        return data, labels
    
    def method1_statistical(self):
        """方法1：统计方法（3σ原则）"""
        print("\n" + "=" * 70)
        print("方法1: 统计方法（3σ原则）")
        print("=" * 70)
        
        start_time = time.time()
        
        # 训练集（前80%）
        split_idx = int(len(self.data) * 0.8)
        X_train = self.data[:split_idx]
        y_train = self.labels[:split_idx]
        X_test = self.data[split_idx:]
        y_test = self.labels[split_idx:]
        
        # 计算均值和标准差（使用训练集的正常样本）
        X_normal = X_train[y_train == 1]
        mean = np.mean(X_normal, axis=0)
        std = np.std(X_normal, axis=0)
        
        # 预测（3σ原则）
        def predict_3sigma(X):
            z_scores = np.abs((X - mean) / std)
            # 任一特征超过3σ即判定为异常
            anomaly_mask = np.any(z_scores > 3, axis=1)
            return np.where(anomaly_mask, -1, 1)
        
        y_pred = predict_3sigma(X_test)
        
        elapsed_time = time.time() - start_time
        
        # 评估
        accuracy = np.mean(y_pred == y_test)
        tp = np.sum((y_pred == -1) & (y_test == -1))
        fp = np.sum((y_pred == -1) & (y_test == 1))
        fn = np.sum((y_pred == 1) & (y_test == -1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n准确率: {accuracy*100:.2f}%")
        print(f"精确率: {precision*100:.2f}%")
        print(f"召回率: {recall*100:.2f}%")
        print(f"F1分数: {f1:.4f}")
        print(f"计算时间: {elapsed_time:.4f} 秒")
        
        return {
            'method': '统计方法(3σ)',
            'y_pred': y_pred,
            'y_test': y_test,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'time': elapsed_time
        }
    
    def method2_isolation_forest(self):
        """方法2：孤立森林"""
        print("\n" + "=" * 70)
        print("方法2: 孤立森林")
        print("=" * 70)
        
        start_time = time.time()
        
        # 数据划分
        split_idx = int(len(self.data) * 0.8)
        X_train = self.data[:split_idx]
        y_train = self.labels[:split_idx]
        X_test = self.data[split_idx:]
        y_test = self.labels[split_idx:]
        
        # 训练
        print("\n训练孤立森林...")
        detector = IsolationForestDetector(
            n_trees=100,
            contamination=0.05
        )
        detector.fit(X_train)
        
        # 预测
        y_pred = detector.predict(X_test)
        
        elapsed_time = time.time() - start_time
        
        # 评估
        accuracy = np.mean(y_pred == y_test)
        tp = np.sum((y_pred == -1) & (y_test == -1))
        fp = np.sum((y_pred == -1) & (y_test == 1))
        fn = np.sum((y_pred == 1) & (y_test == -1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n准确率: {accuracy*100:.2f}%")
        print(f"精确率: {precision*100:.2f}%")
        print(f"召回率: {recall*100:.2f}%")
        print(f"F1分数: {f1:.4f}")
        print(f"计算时间: {elapsed_time:.4f} 秒")
        
        return {
            'method': '孤立森林',
            'y_pred': y_pred,
            'y_test': y_test,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'time': elapsed_time
        }
    
    def method3_autoencoder(self):
        """方法3：自编码器"""
        print("\n" + "=" * 70)
        print("方法3: 自编码器")
        print("=" * 70)
        
        start_time = time.time()
        
        # 数据划分
        split_idx = int(len(self.data) * 0.8)
        X_train = self.data[:split_idx]
        y_train = self.labels[:split_idx]
        X_test = self.data[split_idx:]
        y_test = self.labels[split_idx:]
        
        # 训练
        print("\n训练自编码器...")
        detector = AutoencoderDetector(
            encoding_dim=3,
            hidden_dims=[8, 5],
            contamination=0.05,
            learning_rate=0.01
        )
        detector.fit(X_train, epochs=100, batch_size=32, verbose=True)
        
        # 预测
        y_pred = detector.predict(X_test)
        
        elapsed_time = time.time() - start_time
        
        # 评估
        accuracy = np.mean(y_pred == y_test)
        tp = np.sum((y_pred == -1) & (y_test == -1))
        fp = np.sum((y_pred == -1) & (y_test == 1))
        fn = np.sum((y_pred == 1) & (y_test == -1))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"\n准确率: {accuracy*100:.2f}%")
        print(f"精确率: {precision*100:.2f}%")
        print(f"召回率: {recall*100:.2f}%")
        print(f"F1分数: {f1:.4f}")
        print(f"计算时间: {elapsed_time:.4f} 秒")
        
        return {
            'method': '自编码器',
            'y_pred': y_pred,
            'y_test': y_test,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'time': elapsed_time
        }
    
    def visualize(self, results_list):
        """结果可视化"""
        print("\n" + "=" * 70)
        print("结果可视化")
        print("=" * 70)
        
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        methods = [r['method'] for r in results_list]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # 1. 准确率对比
        accuracies = [r['accuracy'] * 100 for r in results_list]
        
        axes[0, 0].bar(methods, accuracies, color=colors, alpha=0.7)
        axes[0, 0].set_ylabel('准确率 (%)', fontsize=11)
        axes[0, 0].set_title('准确率对比', fontsize=12, fontweight='bold')
        axes[0, 0].set_ylim([0, 105])
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        for i, (method, acc) in enumerate(zip(methods, accuracies)):
            axes[0, 0].text(i, acc, f'{acc:.1f}%', 
                          ha='center', va='bottom', fontsize=10)
        
        # 2. F1分数对比
        f1_scores = [r['f1'] for r in results_list]
        
        axes[0, 1].bar(methods, f1_scores, color=colors, alpha=0.7)
        axes[0, 1].set_ylabel('F1分数', fontsize=11)
        axes[0, 1].set_title('F1分数对比', fontsize=12, fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (method, f1) in enumerate(zip(methods, f1_scores)):
            axes[0, 1].text(i, f1, f'{f1:.3f}', 
                          ha='center', va='bottom', fontsize=10)
        
        # 3. 精确率vs召回率
        precisions = [r['precision'] for r in results_list]
        recalls = [r['recall'] for r in results_list]
        
        x = np.arange(len(methods))
        width = 0.35
        
        axes[1, 0].bar(x - width/2, [p*100 for p in precisions], width, 
                      label='精确率', color='#FF6B6B', alpha=0.7)
        axes[1, 0].bar(x + width/2, [r*100 for r in recalls], width,
                      label='召回率', color='#4ECDC4', alpha=0.7)
        
        axes[1, 0].set_ylabel('百分比 (%)', fontsize=11)
        axes[1, 0].set_title('精确率与召回率', fontsize=12, fontweight='bold')
        axes[1, 0].set_xticks(x)
        axes[1, 0].set_xticklabels(methods)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # 4. 计算时间对比
        times = [r['time'] for r in results_list]
        
        axes[1, 1].bar(methods, times, color=colors, alpha=0.7)
        axes[1, 1].set_ylabel('计算时间 (秒)', fontsize=11)
        axes[1, 1].set_title('计算效率对比', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        
        for i, (method, t) in enumerate(zip(methods, times)):
            axes[1, 1].text(i, t, f'{t:.3f}s', 
                          ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / "figures/anomaly_comparison.png", dpi=300)
        plt.close()
        
        print(f"  已保存: figures/anomaly_comparison.png")
    
    def run(self):
        """运行完整检测系统"""
        print("\n" + "*" * 70)
        print(" " * 20 + "水质异常智能检测")
        print(" " * 28 + "案例4.2")
        print("*" * 70)
        
        try:
            stat_result = self.method1_statistical()
            if_result = self.method2_isolation_forest()
            ae_result = self.method3_autoencoder()
            
            results_list = [stat_result, if_result, ae_result]
            
            self.visualize(results_list)
            
            print("\n" + "=" * 70)
            print("检测完成！")
            print("=" * 70)
            
            # 性能总结
            print(f"\n性能总结:")
            for result in results_list:
                print(f"\n  {result['method']}:")
                print(f"    准确率: {result['accuracy']*100:.2f}%")
                print(f"    精确率: {result['precision']*100:.2f}%")
                print(f"    召回率: {result['recall']*100:.2f}%")
                print(f"    F1分数: {result['f1']:.4f}")
            
        except Exception as e:
            print(f"\n错误: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    detector = WaterQualityAnomalyDetector()
    detector.run()


if __name__ == "__main__":
    main()
