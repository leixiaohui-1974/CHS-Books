#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目8: Pandas数据处理
案例：水质监测数据分析
"""
import pandas as pd
import numpy as np

def main():
    print("="*60)
    print("项目8: Pandas数据处理 - 水质监测分析")
    print("="*60)
    
    # 创建数据
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    data = {
        '日期': dates,
        '水温(°C)': np.random.uniform(10, 25, 30),
        'pH值': np.random.uniform(6.5, 8.5, 30),
        '溶解氧(mg/L)': np.random.uniform(5, 10, 30),
        'COD(mg/L)': np.random.uniform(10, 30, 30)
    }
    df = pd.DataFrame(data)
    
    print("\n水质数据（前5行）:")
    print(df.head())
    
    print("\n统计描述:")
    print(df.describe())
    
    print("\n相关性分析:")
    print(df[['水温(°C)', 'pH值', '溶解氧(mg/L)', 'COD(mg/L)']].corr())
    
    # 水质评价
    df['水质等级'] = pd.cut(df['COD(mg/L)'], 
                           bins=[0, 15, 20, 30, 100],
                           labels=['优', '良', '中', '差'])
    
    print("\n水质等级分布:")
    print(df['水质等级'].value_counts())
    
    print("\n✅ 项目8完成！")

if __name__ == "__main__":
    main()
