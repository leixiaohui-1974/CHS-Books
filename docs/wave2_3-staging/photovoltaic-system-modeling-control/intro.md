---
title: "光伏系统建模与控制"
sidebar_position: 1
---

# 光伏系统建模与控制

## 章节列表
- ch01: 光伏电池与阵列建模 (案例1-5)
- ch02: MPPT最大功率追踪 (案例6-10)
- ch03: 逆变器并网控制 (案例11-15)
- ch04: 微电网孤岛运行 (案例16-20)
- ch05: 水光互补与水面光伏(水能纽带) (新增)

## 代码与测试覆盖
- `code/core/water_energy_nexus.py`
- `tests/test_pv_water.py`

本书是 CHS-Books 遗留资产在 Wave 2/3 阶段并入的优质项目。
我们对底层计算接口（如生态基流、Saint-Venant 求解、HIL/SIL验证、水能枢纽等）进行了严格的 Pytest 补充测试，以符合 HydroDesktop 平台“代码即证据”的底线原则。
