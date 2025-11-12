# 安装指南

**《水利工程Python编程实战》环境配置**

---

## 🚀 方式一：使用Anaconda（推荐）

### 1. 安装Anaconda

访问 [https://www.anaconda.com/download](https://www.anaconda.com/download)

- Windows: 下载并运行安装程序
- Mac: 下载.pkg文件并安装
- Linux: 下载.sh文件并运行

### 2. 创建虚拟环境

```bash
# 创建名为hydraulics的环境
conda create -n hydraulics python=3.9

# 激活环境
conda activate hydraulics

# 安装依赖包
conda install numpy scipy matplotlib pandas sympy jupyter
```

### 3. 验证安装

```bash
python tests/test_basic.py
```

---

## 📦 方式二：使用pip

### 1. 确保Python已安装

```bash
# 检查Python版本（需要3.8+）
python --version

# 或
python3 --version
```

### 2. 升级pip

```bash
python -m pip install --upgrade pip
```

### 3. 安装依赖

```bash
# 进入项目目录
cd python-practice

# 安装所有依赖
pip install -r requirements.txt
```

### 4. 验证安装

```bash
python tests/test_basic.py
```

---

## 🐧 Linux/Mac特殊说明

### Ubuntu/Debian

```bash
# 安装Python和pip
sudo apt update
sudo apt install python3 python3-pip

# 安装依赖
pip3 install -r requirements.txt
```

### CentOS/RHEL

```bash
# 安装Python和pip
sudo yum install python3 python3-pip

# 安装依赖
pip3 install -r requirements.txt
```

### macOS

```bash
# 使用Homebrew安装Python
brew install python3

# 安装依赖
pip3 install -r requirements.txt
```

---

## 🪟 Windows特殊说明

### 使用命令提示符

```cmd
# 检查Python
python --version

# 安装依赖
pip install -r requirements.txt
```

### 可能遇到的问题

**问题1**: pip不是内部或外部命令

**解决**: 将Python添加到PATH环境变量

**问题2**: Microsoft Visual C++ 14.0 is required

**解决**: 安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

---

## ✅ 验证清单

运行测试脚本后，应该看到：

```
╔══════════════════════════════════════════════════════════╗
║               Python环境测试                ║
╚══════════════════════════════════════════════════════════╝

============================================================
测试Python版本
============================================================
Python版本: 3.9.x
✅ Python版本符合要求 (3.8+)

============================================================
测试核心库导入
============================================================
✅ NumPy        1.20.x       导入成功
✅ Matplotlib   3.4.x        导入成功
✅ Pandas       1.3.x        导入成功
✅ SciPy        1.7.x        导入成功
✅ SymPy        1.9          导入成功

... (其他测试)

============================================================
测试总结
============================================================
Python版本   ✅ 通过
核心库导入   ✅ 通过
基础计算     ✅ 通过
绘图功能     ✅ 通过
数据处理     ✅ 通过

总计: 5/5 通过

🎉 所有测试通过！环境配置正确！
```

---

## 🛠️ 常见问题

### Q: 如何检查已安装的包？

```bash
pip list
# 或
conda list
```

### Q: 如何升级某个包？

```bash
pip install --upgrade numpy
# 或
conda update numpy
```

### Q: 如何卸载某个包？

```bash
pip uninstall numpy
# 或
conda remove numpy
```

### Q: 虚拟环境有什么用？

- 隔离不同项目的依赖
- 避免版本冲突
- 便于管理和部署

### Q: Jupyter Notebook如何使用？

```bash
# 启动Jupyter
jupyter notebook

# 会自动打开浏览器
# 访问 http://localhost:8888
```

---

## 📚 推荐配置

### IDE推荐

1. **PyCharm** (专业/社区版)
2. **VS Code** + Python扩展
3. **Spyder** (Anaconda自带)
4. **Jupyter Lab**

### 代码编辑器

1. **Sublime Text** + Python插件
2. **Atom** + Python插件
3. **Vim** + Python配置

---

## 🎓 学习资源

### 官方文档

- Python: https://docs.python.org
- NumPy: https://numpy.org/doc
- Matplotlib: https://matplotlib.org
- Pandas: https://pandas.pydata.org
- SciPy: https://scipy.org
- SymPy: https://sympy.org

### 中文资源

- Python中文文档
- NumPy中文网
- Matplotlib中文网

---

## 💡 提示

1. **使用虚拟环境**: 强烈推荐
2. **保持更新**: 定期更新包
3. **查看文档**: 遇到问题先查官方文档
4. **搜索解决**: Google/百度搜索错误信息

---

**安装完成后，开始学习**: 查看 `QUICK_START.md`

---

*安装指南版本: v1.0*  
*更新时间: 2025-11-12*
