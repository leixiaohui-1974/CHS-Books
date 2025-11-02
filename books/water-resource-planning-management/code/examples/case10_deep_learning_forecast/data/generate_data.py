"""
生成需水量时间序列数据
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def generate_water_demand_data(n_days=365*2, start_date='2022-01-01'):
    """
    生成需水量时间序列数据
    
    包含：
    - 趋势成分
    - 季节成分
    - 周成分
    - 气象影响
    - 随机噪声
    """
    np.random.seed(42)
    
    dates = pd.date_range(start=start_date, periods=n_days, freq='D')
    
    # 基础需水量
    base_demand = 50000  # m³/day
    
    # 趋势成分（每年增长2%）
    t = np.arange(n_days)
    trend = base_demand * (1 + 0.02 * t / 365)
    
    # 季节成分（夏季高，冬季低）
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonal = 5000 * np.sin(2 * np.pi * (day_of_year - 90) / 365)
    
    # 周成分（工作日高，周末低）
    day_of_week = np.array([d.weekday() for d in dates])
    weekly = np.where(day_of_week < 5, 2000, -3000)
    
    # 气象数据
    # 气温（影响需水量）
    temperature = 15 + 10 * np.sin(2 * np.pi * (day_of_year - 90) / 365) + np.random.normal(0, 3, n_days)
    temp_effect = 100 * (temperature - 15)
    
    # 降雨量（负相关）
    rainfall = np.random.gamma(2, 5, n_days)  # 随机降雨
    rainfall[rainfall > 50] = 50  # 限制最大值
    rain_effect = -50 * rainfall
    
    # 节假日（春节、国庆等，需水量降低）
    is_holiday = np.zeros(n_days)
    for year in [2022, 2023]:
        # 春节
        spring_festival = pd.date_range(f'{year}-01-31', periods=7)
        # 国庆
        national_day = pd.date_range(f'{year}-10-01', periods=7)
        
        for holiday in list(spring_festival) + list(national_day):
            if holiday in dates:
                idx = dates.get_loc(holiday)
                is_holiday[idx] = 1
    
    holiday_effect = -5000 * is_holiday
    
    # 随机噪声
    noise = np.random.normal(0, 1000, n_days)
    
    # 总需水量
    demand = trend + seasonal + weekly + temp_effect + rain_effect + holiday_effect + noise
    demand = np.maximum(demand, 10000)  # 确保非负且合理
    
    # 构建DataFrame
    df = pd.DataFrame({
        'date': dates,
        'demand': demand,
        'temperature': temperature,
        'rainfall': rainfall,
        'day_of_week': day_of_week,
        'is_weekend': (day_of_week >= 5).astype(int),
        'month': [d.month for d in dates],
        'is_holiday': is_holiday.astype(int)
    })
    
    return df


if __name__ == '__main__':
    # 生成数据
    df = generate_water_demand_data(n_days=365*2)
    
    # 保存
    df.to_csv('water_demand_data.csv', index=False)
    print(f"数据已生成并保存到 water_demand_data.csv")
    print(f"数据量: {len(df)} 天")
    print(f"需水量范围: {df['demand'].min():.0f} - {df['demand'].max():.0f} m³/day")
