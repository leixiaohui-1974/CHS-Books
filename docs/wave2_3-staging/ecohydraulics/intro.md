---
title: "生态水力学模型"
sidebar_position: 1
---

# 生态水力学模型

## 章节列表
- ch01: 水生态系统建模 (案例1-8)
- ch02: 河道栖息地评估 (案例9-16)
- ch03: 库区生态调度 (案例17-24)
- ch04: 流域级生态协同 (案例25-32)
- ch05: 生态流量计算与测试 (新增)

## 代码与测试覆盖
- `code/core/ecological_dispatch.py`
- `tests/test_eco_dispatch.py`

本书是 CHS-Books 遗留资产在 Wave 2/3 阶段并入的优质项目。
我们对底层计算接口（如生态基流、Saint-Venant 求解、HIL/SIL验证、水能枢纽等）进行了严格的 Pytest 补充测试，以符合 HydroDesktop 平台“代码即证据”的底线原则。
