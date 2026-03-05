---
title: "分布式水文模型"
sidebar_position: 1
---

# 分布式水文模型

## 章节列表
- ch01: 分布式水文模型概论 (案例1-2)
- ch02: 流域空间离散化 (案例1-3)
- ch03: 降雨空间插值 (案例2-3)
- ch04: 产流模拟 (案例4-6)
- ch05: 坡面汇流 (案例7)
- ch06: 河道汇流 (案例8,10)
- ch07: 蒸散发模拟 (案例4-6)
- ch08: 参数率定与不确定性 (案例11-12)
- ch09: 在线辨识与同化 (案例13,21)
- ch10: 水文水动力耦合 (案例15,23)
- ch11: 人类活动影响 (案例16,19)
- ch12: 流域智能管理 (案例17-22,25)
- ch13: 综合应用案例 (案例14,23-25)

## 代码与实战参考
- `code/core/interpolation/thiessen.py`
- `code/core/interpolation/idw.py`
- `code/core/interpolation/kriging.py`
- `code/core/runoff_generation/xaj_model.py`
- `code/core/runoff_generation/green_ampt.py`
- `code/core/slope_routing/kinematic_wave.py`
- `code/core/channel_routing/muskingum.py`
- `code/core/calibration/sce_ua.py`
- `code/core/calibration/glue.py`
- `code/core/assimilation/enkf.py`
- `code/core/coupling/saint_venant.py`
- `code/core/reservoir/optimization.py`

本书是 CHS-Books 遗留资产中的优质项目。所有相关源码及工程案例均可用于深入学习与推演。
