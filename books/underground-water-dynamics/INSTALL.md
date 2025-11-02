# 安装指南

## 环境要求

- Python >= 3.9
- pip 或 conda

## 方法1：使用 pip 安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/underground-water-dynamics.git
cd underground-water-dynamics
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装gwflow包（开发模式）

```bash
pip install -e .
```

## 方法2：使用 conda 安装

### 1. 创建conda环境

```bash
conda create -n gwflow python=3.9
conda activate gwflow
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或者分别安装核心包：

```bash
conda install numpy scipy matplotlib pandas scikit-learn
conda install -c conda-forge plotly seaborn
pip install cvxpy flopy emcee pysindy filterpy
```

### 3. 安装gwflow包

```bash
pip install -e .
```

## 验证安装

### 运行简单测试

```bash
cd tests
python3 run_simple_tests.py
```

### 运行案例1

```bash
cd code/examples/case_01
python3 case_01_1d_steady.py
```

如果看到输出和生成的图片，说明安装成功！

## 开发环境设置（可选）

如果你想参与开发，还需要安装开发工具：

```bash
pip install -e ".[dev]"
```

这将安装：
- pytest（测试框架）
- pytest-cov（测试覆盖率）
- black（代码格式化）
- flake8（代码检查）

## 常见问题

### Q1: 安装 meshpy 失败

**A**: meshpy 需要编译，可能需要安装编译工具：

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev
```

**Mac:**
```bash
xcode-select --install
```

**Windows:**
需要安装 Visual Studio Build Tools

### Q2: 安装 flopy 失败

**A**: 尝试单独安装：
```bash
pip install flopy --no-deps
```

### Q3: 导入 gwflow 失败

**A**: 确保使用 `-e` 模式安装：
```bash
pip install -e .
```

或者手动添加到 Python 路径：
```python
import sys
sys.path.insert(0, '/path/to/underground-water-dynamics')
```

## 最小安装（仅核心功能）

如果只想运行基础案例（案例1-5），只需安装核心依赖：

```bash
pip install numpy scipy matplotlib
```

## 下一步

安装完成后，建议：

1. 阅读 [START_HERE.md](START_HERE.md)
2. 运行案例1验证安装
3. 选择适合自己的学习路径

Happy coding! 🚀
