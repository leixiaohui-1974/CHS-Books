---
title: "渠系与管道控制"
sidebar_position: 1
---

# 渠系与管道控制

## 章节列表
- ch01: 渠系水动力学基础 (案例1-5)
- ch02: 圣维南方程与边界 (案例6-10)
- ch03: 管道水锤与瞬变流 (案例11-15)
- ch04: PID与MPC在渠系中的应用 (案例16-20)
- ch05: 测试与工程验证 (新增)

## 代码与测试覆盖
- `code/core/saint_venant.py`
- `tests/test_canal_control.py`

本书是 CHS-Books 遗留资产在 Wave 2/3 阶段并入的优质项目。
我们对底层计算接口（如生态基流、Saint-Venant 求解、HIL/SIL验证、水能枢纽等）进行了严格的 Pytest 补充测试，以符合 HydroDesktop 平台“代码即证据”的底线原则。
