#!/bin/bash
# 批量测试所有Python代码
# 用法: bash run_all_tests.sh

echo "========================================="
echo "《水力学1000题详解》代码批量测试"
echo "========================================="
echo ""

# 统计
total=0
success=0
failed=0

# 测试日志
log_file="test_results_$(date +%Y%m%d_%H%M%S).log"
echo "测试开始时间: $(date)" > "$log_file"
echo "" >> "$log_file"

# 遍历所有Python代码
for file in problem_*.py; do
    if [ -f "$file" ]; then
        total=$((total + 1))
        echo "[$total] 测试: $file"
        echo "----------------------------------------" >> "$log_file"
        echo "[$total] $file" >> "$log_file"
        
        # 运行代码并捕获输出
        if python3 "$file" >> "$log_file" 2>&1; then
            success=$((success + 1))
            echo "  ✅ 通过"
            echo "  状态: ✅ 通过" >> "$log_file"
        else
            failed=$((failed + 1))
            echo "  ❌ 失败"
            echo "  状态: ❌ 失败" >> "$log_file"
        fi
        echo "" >> "$log_file"
    fi
done

# 总结
echo ""
echo "========================================="
echo "测试完成！"
echo "========================================="
echo "总计: $total 个代码"
echo "成功: $success 个 ✅"
echo "失败: $failed 个 ❌"
echo "成功率: $(echo "scale=2; $success * 100 / $total" | bc)%"
echo ""
echo "详细日志已保存到: $log_file"
echo ""

# 写入总结到日志
echo "=========================================" >> "$log_file"
echo "测试总结" >> "$log_file"
echo "=========================================" >> "$log_file"
echo "测试结束时间: $(date)" >> "$log_file"
echo "总计: $total 个代码" >> "$log_file"
echo "成功: $success 个 ✅" >> "$log_file"
echo "失败: $failed 个 ❌" >> "$log_file"
echo "成功率: $(echo "scale=2; $success * 100 / $total" | bc)%" >> "$log_file"

# 退出码
if [ $failed -eq 0 ]; then
    exit 0
else
    exit 1
fi
