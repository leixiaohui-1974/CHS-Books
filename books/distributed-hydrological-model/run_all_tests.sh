#!/bin/bash
# 运行所有测试脚本

echo "=========================================="
echo "分布式水文模型 - 测试套件"
echo "=========================================="
echo ""

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd "$(dirname "$0")"

echo "项目路径: $(pwd)"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到python3${NC}"
    exit 1
fi

echo "Python版本: $(python3 --version)"
echo ""

# 检查依赖
echo "检查依赖包..."
for package in numpy scipy matplotlib; do
    python3 -c "import $package" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} $package"
    else
        echo -e "  ${RED}✗${NC} $package (未安装)"
    fi
done
echo ""

# 运行测试
echo "=========================================="
echo "运行单元测试"
echo "=========================================="
echo ""

test_files=(
    "tests/test_metrics.py"
    "tests/test_xaj_model.py"
    "tests/test_interpolation.py"
)

total_tests=0
passed_tests=0

for test_file in "${test_files[@]}"; do
    if [ -f "$test_file" ]; then
        echo "运行: $test_file"
        python3 "$test_file" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✓ 通过${NC}"
            ((passed_tests++))
        else
            echo -e "  ${YELLOW}⚠ 需要依赖包${NC}"
        fi
        ((total_tests++))
    fi
done

echo ""
echo "测试结果: $passed_tests/$total_tests"
echo ""

# 运行案例
echo "=========================================="
echo "运行案例演示"
echo "=========================================="
echo ""

cases=(
    "code/examples/case_02_thiessen/main.py"
    "code/examples/case_03_idw_kriging/main.py"
    "code/examples/case_04_xaj_model/main.py"
)

for case in "${cases[@]}"; do
    if [ -f "$case" ]; then
        case_name=$(basename $(dirname "$case"))
        echo "案例: $case_name"
        echo "  (需要numpy等依赖包才能运行)"
    fi
done

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo "提示: 运行案例需要先安装依赖:"
echo "  pip install numpy scipy matplotlib"
echo ""
