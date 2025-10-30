"""
案例19单元测试：多闸门渠系动态调度优化

测试内容：
1. 适应度函数计算
2. 遗传算法选择操作
3. 遗传算法交叉操作
4. 遗传算法变异操作
5. PSO速度更新
6. PSO位置更新
7. PSO惯性权重
8. 约束处理（罚函数法）
9. 约束处理（修复法）
10. 性能指标计算

作者：CHS-Books项目
日期：2025-10-30
"""

import sys
import os
import numpy as np
import pytest

# 添加代码库路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../code'))


def compute_fitness(objective_value, method='inverse'):
    """
    计算适应度函数

    Args:
        objective_value: 目标函数值（越小越好）
        method: 'inverse' 或 'exponential'

    Returns:
        fitness: 适应度（越大越好）
    """
    if method == 'inverse':
        fitness = 1.0 / (1.0 + objective_value)
    elif method == 'exponential':
        sigma = 1.0
        fitness = np.exp(-objective_value / sigma)
    else:
        raise ValueError(f"Unknown method: {method}")

    return fitness


def roulette_wheel_selection(fitnesses, n_selected=1):
    """
    轮盘赌选择

    Args:
        fitnesses: 适应度数组
        n_selected: 选择个数

    Returns:
        indices: 被选中的索引
    """
    total_fitness = np.sum(fitnesses)
    probabilities = fitnesses / total_fitness

    # 累积概率
    cum_prob = np.cumsum(probabilities)

    selected = []
    for _ in range(n_selected):
        r = np.random.rand()
        # 找到第一个累积概率 >= r 的索引
        idx = np.searchsorted(cum_prob, r)
        selected.append(idx)

    return np.array(selected)


def single_point_crossover(parent1, parent2):
    """
    单点交叉

    Args:
        parent1: 父代1
        parent2: 父代2

    Returns:
        child1, child2: 子代
    """
    length = len(parent1)
    if length <= 1:
        return parent1.copy(), parent2.copy()

    # 随机选择交叉点
    point = np.random.randint(1, length)

    # 交叉
    child1 = np.concatenate([parent1[:point], parent2[point:]])
    child2 = np.concatenate([parent2[:point], parent1[point:]])

    return child1, child2


def arithmetic_crossover(parent1, parent2, alpha=0.5):
    """
    算术交叉（实数编码）

    Args:
        parent1: 父代1
        parent2: 父代2
        alpha: 交叉系数 (0-1)

    Returns:
        child1, child2: 子代
    """
    child1 = alpha * parent1 + (1 - alpha) * parent2
    child2 = (1 - alpha) * parent1 + alpha * parent2

    return child1, child2


def uniform_mutation(individual, bounds, mutation_rate=0.1):
    """
    均匀变异

    Args:
        individual: 个体
        bounds: 边界 (min, max)
        mutation_rate: 变异幅度

    Returns:
        mutated: 变异后的个体
    """
    mutated = individual.copy()
    a_min, a_max = bounds

    for i in range(len(mutated)):
        if np.random.rand() < 0.1:  # 10%概率变异
            delta = (a_max - a_min) * mutation_rate * (2 * np.random.rand() - 1)
            mutated[i] += delta
            # 边界限制
            mutated[i] = np.clip(mutated[i], a_min, a_max)

    return mutated


def gaussian_mutation(individual, bounds, sigma=0.1):
    """
    高斯变异

    Args:
        individual: 个体
        bounds: 边界 (min, max)
        sigma: 变异标准差

    Returns:
        mutated: 变异后的个体
    """
    mutated = individual.copy()
    a_min, a_max = bounds

    for i in range(len(mutated)):
        if np.random.rand() < 0.1:
            delta = sigma * np.random.randn()
            mutated[i] += delta
            mutated[i] = np.clip(mutated[i], a_min, a_max)

    return mutated


def pso_velocity_update(v, x, p_best, g_best, w=0.7, c1=2.0, c2=2.0):
    """
    PSO速度更新

    Args:
        v: 当前速度
        x: 当前位置
        p_best: 个体最优位置
        g_best: 全局最优位置
        w: 惯性权重
        c1: 个体学习因子
        c2: 社会学习因子

    Returns:
        v_new: 新速度
    """
    r1 = np.random.rand(len(v))
    r2 = np.random.rand(len(v))

    v_new = w * v + c1 * r1 * (p_best - x) + c2 * r2 * (g_best - x)

    return v_new


def pso_position_update(x, v, bounds):
    """
    PSO位置更新

    Args:
        x: 当前位置
        v: 当前速度
        bounds: 边界 (min, max)

    Returns:
        x_new: 新位置
        v_new: 修正后的速度
    """
    x_new = x + v
    v_new = v.copy()

    a_min, a_max = bounds

    # 边界处理
    for i in range(len(x_new)):
        if x_new[i] < a_min:
            x_new[i] = a_min
            v_new[i] = 0.0
        elif x_new[i] > a_max:
            x_new[i] = a_max
            v_new[i] = 0.0

    return x_new, v_new


def linear_inertia_weight(iteration, max_iterations, w_max=0.9, w_min=0.4):
    """
    线性递减惯性权重

    Args:
        iteration: 当前迭代数
        max_iterations: 最大迭代数
        w_max: 最大惯性权重
        w_min: 最小惯性权重

    Returns:
        w: 惯性权重
    """
    if max_iterations == 0:
        return w_max  # 避免除零
    w = w_max - (w_max - w_min) * iteration / max_iterations
    return w


def penalty_function(objective, constraint_violations, penalty_factor=1e6):
    """
    罚函数法

    Args:
        objective: 原始目标函数值
        constraint_violations: 约束违反量数组
        penalty_factor: 罚因子

    Returns:
        penalized_objective: 惩罚后的目标函数值
    """
    penalty = 0.0
    for violation in constraint_violations:
        penalty += penalty_factor * max(0, violation)**2

    return objective + penalty


def repair_bounds(individual, bounds):
    """
    边界修复法

    Args:
        individual: 个体
        bounds: 边界 (min, max)

    Returns:
        repaired: 修复后的个体
    """
    a_min, a_max = bounds
    repaired = np.clip(individual, a_min, a_max)
    return repaired


def compute_rmse(actual, target):
    """
    计算均方根误差

    Args:
        actual: 实际值数组
        target: 目标值数组

    Returns:
        rmse: 均方根误差
    """
    return np.sqrt(np.mean((actual - target)**2))


def compute_mae(actual, target):
    """
    计算平均绝对误差

    Args:
        actual: 实际值数组
        target: 目标值数组

    Returns:
        mae: 平均绝对误差
    """
    return np.mean(np.abs(actual - target))


class TestCase19DynamicScheduling:
    """案例19：多闸门渠系动态调度优化测试"""

    def test_fitness_inverse_method(self):
        """测试1：适应度函数（倒数法）"""
        J = 10.0  # 目标函数值

        fitness = compute_fitness(J, method='inverse')

        # 适应度应为正
        assert fitness > 0

        # 验证公式
        fitness_expected = 1.0 / (1.0 + J)
        assert abs(fitness - fitness_expected) < 1e-10

    def test_fitness_better_solution(self):
        """测试2：适应度随目标函数单调性"""
        J1 = 5.0
        J2 = 10.0  # J2 > J1（更差）

        fitness1 = compute_fitness(J1)
        fitness2 = compute_fitness(J2)

        # 目标函数越小，适应度越大
        assert fitness1 > fitness2

    def test_roulette_wheel_selection(self):
        """测试3：轮盘赌选择"""
        fitnesses = np.array([0.1, 0.2, 0.3, 0.4])
        n_selected = 2

        np.random.seed(42)
        selected = roulette_wheel_selection(fitnesses, n_selected)

        # 应选择n_selected个
        assert len(selected) == n_selected

        # 索引应在有效范围
        assert all(0 <= idx < len(fitnesses) for idx in selected)

    def test_single_point_crossover(self):
        """测试4：单点交叉"""
        parent1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        parent2 = np.array([6.0, 7.0, 8.0, 9.0, 10.0])

        np.random.seed(42)
        child1, child2 = single_point_crossover(parent1, parent2)

        # 子代长度应相同
        assert len(child1) == len(parent1)
        assert len(child2) == len(parent2)

        # 子代应包含父代的基因
        # （至少有一部分来自各自的父代）

    def test_arithmetic_crossover(self):
        """测试5：算术交叉"""
        parent1 = np.array([1.0, 2.0, 3.0])
        parent2 = np.array([4.0, 5.0, 6.0])
        alpha = 0.5

        child1, child2 = arithmetic_crossover(parent1, parent2, alpha)

        # 子代长度应相同
        assert len(child1) == len(parent1)

        # 验证算术交叉公式
        expected_child1 = alpha * parent1 + (1 - alpha) * parent2
        assert np.allclose(child1, expected_child1)

        # 子代应在父代之间
        assert np.all(child1 >= np.minimum(parent1, parent2))
        assert np.all(child1 <= np.maximum(parent1, parent2))

    def test_uniform_mutation(self):
        """测试6：均匀变异"""
        individual = np.array([1.5, 2.0, 2.5])
        bounds = (0.5, 3.0)

        np.random.seed(42)
        mutated = uniform_mutation(individual, bounds, mutation_rate=0.1)

        # 长度不变
        assert len(mutated) == len(individual)

        # 应在边界内
        assert np.all(mutated >= bounds[0])
        assert np.all(mutated <= bounds[1])

    def test_gaussian_mutation(self):
        """测试7：高斯变异"""
        individual = np.array([1.5, 2.0, 2.5])
        bounds = (0.5, 3.0)

        np.random.seed(42)
        mutated = gaussian_mutation(individual, bounds, sigma=0.1)

        # 长度不变
        assert len(mutated) == len(individual)

        # 应在边界内
        assert np.all(mutated >= bounds[0])
        assert np.all(mutated <= bounds[1])

    def test_pso_velocity_update(self):
        """测试8：PSO速度更新"""
        v = np.array([0.1, 0.2, 0.3])
        x = np.array([1.0, 2.0, 3.0])
        p_best = np.array([1.5, 2.5, 3.5])
        g_best = np.array([2.0, 3.0, 4.0])

        w = 0.7
        c1 = 2.0
        c2 = 2.0

        np.random.seed(42)
        v_new = pso_velocity_update(v, x, p_best, g_best, w, c1, c2)

        # 新速度长度应相同
        assert len(v_new) == len(v)

        # 新速度应包含三个分量的贡献
        # （惯性、认知、社会）

    def test_pso_position_update(self):
        """测试9：PSO位置更新"""
        x = np.array([1.0, 2.0, 3.0])
        v = np.array([0.5, 0.3, -0.2])
        bounds = (0.5, 3.5)

        x_new, v_new = pso_position_update(x, v, bounds)

        # 长度不变
        assert len(x_new) == len(x)

        # 应在边界内
        assert np.all(x_new >= bounds[0])
        assert np.all(x_new <= bounds[1])

    def test_pso_boundary_velocity_reset(self):
        """测试10：PSO边界速度重置"""
        x = np.array([0.3, 2.0])  # 第一个元素会超出下界
        v = np.array([-0.5, 0.2])
        bounds = (0.5, 3.0)

        x_new, v_new = pso_position_update(x, v, bounds)

        # 超出边界的位置应被修正
        assert x_new[0] == bounds[0]

        # 对应的速度应置零
        assert v_new[0] == 0.0

    def test_linear_inertia_weight_decrease(self):
        """测试11：惯性权重线性递减"""
        max_iter = 100
        w_max = 0.9
        w_min = 0.4

        # 初始
        w0 = linear_inertia_weight(0, max_iter, w_max, w_min)
        assert abs(w0 - w_max) < 1e-10

        # 中间
        w_mid = linear_inertia_weight(max_iter // 2, max_iter, w_max, w_min)
        w_expected = (w_max + w_min) / 2
        assert abs(w_mid - w_expected) < 0.01

        # 最终
        w_final = linear_inertia_weight(max_iter, max_iter, w_max, w_min)
        assert abs(w_final - w_min) < 1e-10

    def test_penalty_function_no_violation(self):
        """测试12：罚函数法（无违反）"""
        objective = 10.0
        violations = [0.0, 0.0, 0.0]
        penalty_factor = 1e6

        penalized = penalty_function(objective, violations, penalty_factor)

        # 无违反时应等于原目标
        assert abs(penalized - objective) < 1e-6

    def test_penalty_function_with_violation(self):
        """测试13：罚函数法（有违反）"""
        objective = 10.0
        violations = [0.5, 0.0, 0.0]  # 第一个约束违反0.5
        penalty_factor = 1e6

        penalized = penalty_function(objective, violations, penalty_factor)

        # 有违反时应大幅增加
        assert penalized > objective
        assert penalized > 1e5  # 罚项很大

    def test_repair_bounds(self):
        """测试14：边界修复"""
        individual = np.array([0.2, 1.5, 3.5])  # 第一个低于下界，第三个高于上界
        bounds = (0.5, 3.0)

        repaired = repair_bounds(individual, bounds)

        # 应在边界内
        assert np.all(repaired >= bounds[0])
        assert np.all(repaired <= bounds[1])

        # 中间的不变
        assert repaired[1] == individual[1]

        # 超出的被修正
        assert repaired[0] == bounds[0]
        assert repaired[2] == bounds[1]

    def test_rmse_calculation(self):
        """测试15：RMSE计算"""
        actual = np.array([1.0, 2.0, 3.0, 4.0])
        target = np.array([1.1, 2.2, 2.9, 4.1])

        rmse = compute_rmse(actual, target)

        # RMSE应为正
        assert rmse > 0

        # 手动计算验证
        squared_errors = (actual - target)**2
        rmse_expected = np.sqrt(np.mean(squared_errors))
        assert abs(rmse - rmse_expected) < 1e-10

    def test_mae_calculation(self):
        """测试16：MAE计算"""
        actual = np.array([1.0, 2.0, 3.0, 4.0])
        target = np.array([1.1, 2.2, 2.9, 4.1])

        mae = compute_mae(actual, target)

        # MAE应为正
        assert mae > 0

        # MAE应小于最大误差
        max_error = np.max(np.abs(actual - target))
        assert mae <= max_error

    def test_rmse_perfect_match(self):
        """测试17：RMSE完美匹配"""
        actual = np.array([1.0, 2.0, 3.0])
        target = actual.copy()

        rmse = compute_rmse(actual, target)

        # 完美匹配RMSE为0
        assert rmse < 1e-10


class TestAlgorithmProperties:
    """算法特性测试"""

    def test_fitness_range(self):
        """测试适应度范围"""
        # 目标函数从0到无穷
        objectives = [0.0, 1.0, 10.0, 100.0]
        fitnesses = [compute_fitness(J) for J in objectives]

        # 适应度应在(0, 1]范围
        assert all(0 < f <= 1.0 for f in fitnesses)

        # 单调递减
        for i in range(len(fitnesses) - 1):
            assert fitnesses[i] > fitnesses[i + 1]

    def test_crossover_conservation(self):
        """测试交叉算子的守恒性"""
        parent1 = np.array([1.0, 2.0, 3.0])
        parent2 = np.array([4.0, 5.0, 6.0])
        alpha = 0.5

        child1, child2 = arithmetic_crossover(parent1, parent2, alpha)

        # 算术交叉的平均值守恒
        parent_mean = (parent1 + parent2) / 2
        child_mean = (child1 + child2) / 2

        assert np.allclose(parent_mean, child_mean)

    def test_pso_convergence_tendency(self):
        """测试PSO收敛趋势"""
        # 粒子当前位置
        x = np.array([0.0, 0.0, 0.0])

        # 个体最优和全局最优都在同一位置
        p_best = np.array([5.0, 5.0, 5.0])
        g_best = np.array([5.0, 5.0, 5.0])

        # 初始速度为0
        v = np.array([0.0, 0.0, 0.0])

        # 更新速度
        np.random.seed(42)
        v_new = pso_velocity_update(v, x, p_best, g_best, w=0.5, c1=2.0, c2=2.0)

        # 新速度应指向最优位置（正方向）
        assert np.all(v_new > 0)

    def test_inertia_weight_monotonicity(self):
        """测试惯性权重单调递减"""
        max_iter = 100

        weights = [linear_inertia_weight(i, max_iter) for i in range(max_iter + 1)]

        # 应单调递减
        for i in range(len(weights) - 1):
            assert weights[i] >= weights[i + 1]


class TestEdgeCases:
    """边界条件测试"""

    def test_zero_objective(self):
        """测试零目标函数"""
        J = 0.0

        fitness = compute_fitness(J)

        # J=0时fitness=1.0
        assert abs(fitness - 1.0) < 1e-10

    def test_very_large_objective(self):
        """测试极大目标函数"""
        J = 1e10

        fitness = compute_fitness(J)

        # J很大时fitness趋近0
        assert fitness < 1e-9

    def test_single_element_crossover(self):
        """测试单元素交叉"""
        parent1 = np.array([1.0])
        parent2 = np.array([2.0])

        child1, child2 = single_point_crossover(parent1, parent2)

        # 单元素无法交叉，应返回父代
        assert child1[0] == parent1[0]
        assert child2[0] == parent2[0]

    def test_zero_velocity_pso(self):
        """测试零速度PSO"""
        x = np.array([1.0, 2.0])
        v = np.array([0.0, 0.0])
        bounds = (0.0, 5.0)

        x_new, v_new = pso_position_update(x, v, bounds)

        # 零速度下位置不变
        assert np.allclose(x_new, x)

    def test_negative_violations(self):
        """测试负违反量（满足约束）"""
        objective = 10.0
        violations = [-1.0, -0.5, 0.0]  # 负数表示满足

        penalized = penalty_function(objective, violations)

        # 负违反量不应产生惩罚
        assert abs(penalized - objective) < 1e-6

    def test_zero_max_iterations(self):
        """测试零迭代数"""
        w = linear_inertia_weight(0, 0, w_max=0.9, w_min=0.4)

        # max_iterations=0时应返回w_max（避免除零）
        assert abs(w - 0.9) < 1e-10

    def test_rmse_single_point(self):
        """测试单点RMSE"""
        actual = np.array([1.5])
        target = np.array([2.0])

        rmse = compute_rmse(actual, target)

        # 单点RMSE = |差值|
        assert abs(rmse - 0.5) < 1e-10

    def test_repair_already_valid(self):
        """测试修复已满足约束的个体"""
        individual = np.array([1.0, 2.0, 2.5])
        bounds = (0.5, 3.0)

        repaired = repair_bounds(individual, bounds)

        # 已满足约束，应不变
        assert np.allclose(repaired, individual)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
