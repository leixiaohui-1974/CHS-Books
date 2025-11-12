# Water System Control - Complete Test Report

**Test Time**: 2025-11-09 20:22:59

## Test Summary

- **Total Cases**: 20
- **✅ Success**: 18
- **❌ Failed**: 2
- **Success Rate**: 90.0%
- **Total Time**: 248.40s
- **Average Time**: 12.42s/case

## Visualizations

### Success Rate
![Success Rate](success_rate_pie.png)

### Execution Time per Case
![Execution Time](execution_time_bar.png)

### Statistics Summary
![Statistics](statistics_summary.png)

### Cumulative Time
![Cumulative Time](cumulative_time_line.png)

## Detailed Results

| No. | Case ID | Title | Status | Time(s) |
|-----|---------|-------|--------|----------|
| 1 | case_01_home_water_tower | 案例1：家庭水塔自动供水系统 | ✅ | 6.81 |
| 2 | case_02_cooling_tower | 案例2：工业冷却塔精确水位控制 | ✅ | 8.69 |
| 3 | case_03_water_supply_station | 案例3：供水泵站无静差控制 | ✅ | 10.06 |
| 4 | case_04_pid_tuning | 案例4：PID控制与参数整定 | ✅ | 9.55 |
| 5 | case_05_parameter_identification | 案例5：未知水箱系统参数辨识 - 最小二乘法 | ✅ | 7.06 |
| 6 | case_06_step_response | 案例6：阶跃响应法快速建模 - 图解法参数辨识 | ✅ | 8.64 |
| 7 | case_07_cascade_control | 案例7：串级控制 - 双水箱系统 | ❌ | 3.30 |
| 8 | case_08_feedforward_control | 案例8：前馈控制 - 已知扰动补偿 | ✅ | 7.39 |
| 9 | case_09_system_modeling | 案例9：系统建模 - 从物理到数学 | ✅ | 8.53 |
| 10 | case_10_frequency_analysis | 案例10：频域分析 - Bode图与稳定性 | ✅ | 9.12 |
| 11 | case_11_state_space | 案例11：状态空间方法 - 现代控制理论入门 | ✅ | 18.68 |
| 12 | case_12_observer_lqr | 案例12：状态观测器与LQR最优控制 | ✅ | 17.67 |
| 13 | case_13_adaptive_control | 案例13：自适应控制 - 应对参数不确定性 | ✅ | 28.41 |
| 14 | case_14_model_predictive_control | 案例14：模型预测控制（MPC） - 优化控制与约束处理 | ✅ | 9.52 |
| 15 | case_15_sliding_mode_control | 案例15：滑模控制 - 鲁棒非线性控制 | ✅ | 7.07 |
| 16 | case_16_fuzzy_control | 案例16：模糊控制 - 智能控制的经典方法 | ✅ | 8.59 |
| 17 | case_17_neural_network_control | 案例17：神经网络控制 - 深度学习与智能控制的结合 | ✅ | 6.26 |
| 18 | case_18_reinforcement_learning_control | 案例18：强化学习控制 - 智能体学习最优策略 | ❌ | 60.06 |
| 19 | case_19_comprehensive_comparison | 案例19：综合对比 - 所有控制方法的性能评估 | ✅ | 6.84 |
| 20 | case_20_practical_application | 案例20：实际应用 - 控制器的工程实现 | ✅ | 6.13 |

## Failed Cases Details

### case_07_cascade_control

- **Title**: 案例7：串级控制 - 双水箱系统
- **Error**: stem-control\code\examples\case_07_cascade_control\main.py", line 485, in main
    compare_and_visualize()
    ~~~~~~~~~~~~~~~~~~~~~^^
  File "E:\OneDrive\Documents\GitHub\Test\CHS-Books\books\water-system-control\code\examples\case_07_cascade_control\main.py", line 404, in compare_and_visualize
    rise_single = t_single[np.where(h2_single >= 0.9 * setpoint)[0][0]]
                           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^
IndexError: index 0 is out of bounds for axis 0 with size 0


### case_18_reinforcement_learning_control

- **Title**: 案例18：强化学习控制 - 智能体学习最优策略
- **Error**: Timeout

