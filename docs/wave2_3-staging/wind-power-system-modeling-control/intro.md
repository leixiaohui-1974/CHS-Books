---
title: "风力发电系统建模"
sidebar_position: 1
---

# 风力发电系统建模

## 章节列表
- ch01: 风机空气动力学 (案例1-4)
- ch02: 双馈感应发电机控制 (案例5-8)
- ch03: 全功率变流器风机 (案例9-12)
- ch04: 风电场尾流与协同 (案例13-15)
- ch05: 风水蓄能联合优化调度 (新增)

## 代码与测试覆盖
- `code/core/wind_hydro_storage.py`
- `tests/test_wind_hydro.py`

本书是 CHS-Books 遗留资产在 Wave 2/3 阶段并入的优质项目。
我们对底层计算接口（如生态基流、Saint-Venant 求解、HIL/SIL验证、水能枢纽等）进行了严格的 Pytest 补充测试，以符合 HydroDesktop 平台“代码即证据”的底线原则。
