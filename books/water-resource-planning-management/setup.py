"""
水资源规划与管理教材 - 安装配置文件
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="water-resource-planning-management",
    version="1.0.0",
    author="教材编写组",
    author_email="contact@example.com",  # 待填
    description="水资源规划与管理教材 - 案例驱动的现代化教学资源",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/water-resource-planning-management",  # 待填
    packages=find_packages(where="code"),
    package_dir={"": "code"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Hydrology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "scikit-learn>=1.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "optimization": ["pulp>=2.5.0", "pyomo>=6.2.0", "cvxpy>=1.2.0", "deap>=1.3.0"],
        "ml": ["xgboost>=1.5.0", "lightgbm>=3.3.0"],
        "dl": ["torch>=1.10.0", "torchvision>=0.11.0"],
        "rl": ["gym>=0.21.0", "stable-baselines3>=1.4.0"],
        "gis": ["geopandas>=0.10.0", "shapely>=1.8.0", "rasterio>=1.2.0"],
        "web": ["flask>=2.0.0", "fastapi>=0.75.0", "uvicorn>=0.17.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "pylint>=2.12.0",
            "mypy>=0.931",
            "jupyter>=1.0.0",
        ],
        "all": [
            "pulp>=2.5.0",
            "pyomo>=6.2.0",
            "cvxpy>=1.2.0",
            "deap>=1.3.0",
            "xgboost>=1.5.0",
            "torch>=1.10.0",
            "gym>=0.21.0",
            "geopandas>=0.10.0",
            "flask>=2.0.0",
            "pytest>=7.0.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wrpm=core.cli:main",  # 命令行工具（待实现）
        ],
    },
)
