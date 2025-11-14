#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量运行案例生成可视化图片
========================================

扫描所有案例，运行包含图片生成代码的案例，
自动生成可视化图片以提升案例质量。

作者: CHS-Books项目
日期: 2025-01-14
"""

import os
import sys
import subprocess
from pathlib import Path
import json
import time
from typing import List, Dict, Tuple

# 书籍目录配置
BOOKS = {
    'ecohydraulics': '生态水力学',
    'water-environment-simulation': '水环境数值模拟',
    'open-channel-hydraulics': '明渠水力学',
    'intelligent-water-network-design': '智能水网设计',
    'photovoltaic-system-modeling': '光伏系统建模与控制',
    'wind-power-system-modeling': '风电系统建模与控制',
    'distributed-hydrological-model': '分布式水文模型',
    'canal-pipeline-control': '渠道与管道控制',
}


class ImageGenerator:
    """图片生成器"""

    def __init__(self, base_path: str = '/home/user/CHS-Books/books'):
        self.base_path = Path(base_path)
        self.results = []

    def has_image_generation_code(self, main_py_path: Path) -> bool:
        """检查main.py是否包含图片生成代码"""
        if not main_py_path.exists():
            return False

        try:
            content = main_py_path.read_text(encoding='utf-8')
            # 查找常见的图片保存函数
            keywords = [
                'plt.savefig',
                'fig.savefig',
                'pyplot.savefig',
                '.save(',  # PIL Image.save
                'imsave',
                'imwrite',
            ]
            return any(keyword in content for keyword in keywords)
        except Exception as e:
            print(f"  ⚠ 读取文件错误: {e}")
            return False

    def run_case(self, case_path: Path, timeout: int = 60) -> Tuple[bool, str]:
        """运行案例生成图片

        Args:
            case_path: 案例路径
            timeout: 超时时间（秒）

        Returns:
            (成功标志, 错误信息)
        """
        main_py = case_path / 'main.py'
        if not main_py.exists():
            return False, "main.py不存在"

        try:
            # 切换到案例目录运行
            result = subprocess.run(
                [sys.executable, 'main.py'],
                cwd=str(case_path),
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, 'MPLBACKEND': 'Agg'}  # 使用非交互式后端
            )

            if result.returncode == 0:
                return True, ""
            else:
                error_msg = result.stderr[:200] if result.stderr else result.stdout[:200]
                return False, f"退出码{result.returncode}: {error_msg}"

        except subprocess.TimeoutExpired:
            return False, f"超时（>{timeout}秒）"
        except Exception as e:
            return False, str(e)

    def count_images(self, case_path: Path) -> int:
        """统计案例中的图片数量"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.svg', '.pdf'}
        count = 0
        for file in case_path.iterdir():
            if file.is_file() and file.suffix.lower() in image_extensions:
                count += 1
        return count

    def discover_and_generate(self) -> Dict:
        """发现并生成图片"""
        print("\n" + "=" * 70)
        print("批量图片生成工具")
        print("=" * 70)

        total_cases = 0
        has_code = 0
        success = 0
        failed = 0
        images_before = 0
        images_after = 0

        for book_id, book_name in BOOKS.items():
            book_path = self.base_path / book_id / 'code' / 'examples'

            if not book_path.exists():
                print(f"\n✗ {book_name}: 目录不存在")
                continue

            print(f"\n{'=' * 70}")
            print(f"处理书籍: {book_name} ({book_id})")
            print(f"{'=' * 70}")

            # 发现所有案例
            cases = sorted([d for d in book_path.iterdir() if d.is_dir() and d.name.startswith('case_')])
            print(f"发现 {len(cases)} 个案例")

            for case_dir in cases:
                total_cases += 1
                case_name = case_dir.name
                main_py = case_dir / 'main.py'

                # 检查是否有图片生成代码
                if not self.has_image_generation_code(main_py):
                    print(f"  ⊝ {case_name}: 无图片生成代码")
                    continue

                has_code += 1

                # 统计运行前的图片数量
                before_count = self.count_images(case_dir)
                images_before += before_count

                # 运行案例
                print(f"  ▶ {case_name}: 运行中...", end='', flush=True)
                ok, error = self.run_case(case_dir, timeout=30)

                # 统计运行后的图片数量
                after_count = self.count_images(case_dir)
                images_after += after_count
                new_images = after_count - before_count

                if ok:
                    success += 1
                    if new_images > 0:
                        print(f"\r  ✓ {case_name}: 成功生成 {new_images} 张图片 (总计{after_count}张)")
                    else:
                        print(f"\r  ✓ {case_name}: 运行成功 (已有{after_count}张图片)")

                    self.results.append({
                        'book': book_name,
                        'case': case_name,
                        'status': 'success',
                        'images_before': before_count,
                        'images_after': after_count,
                        'images_new': new_images
                    })
                else:
                    failed += 1
                    print(f"\r  ✗ {case_name}: 失败 - {error}")

                    self.results.append({
                        'book': book_name,
                        'case': case_name,
                        'status': 'failed',
                        'error': error,
                        'images_before': before_count,
                        'images_after': after_count,
                    })

        # 汇总统计
        summary = {
            'total_cases': total_cases,
            'has_code': has_code,
            'success': success,
            'failed': failed,
            'images_before': images_before,
            'images_after': images_after,
            'images_generated': images_after - images_before,
            'results': self.results
        }

        return summary

    def print_summary(self, summary: Dict):
        """打印统计摘要"""
        print("\n" + "=" * 70)
        print("生成统计摘要")
        print("=" * 70)
        print(f"总案例数: {summary['total_cases']}")
        print(f"包含图片生成代码: {summary['has_code']}")
        print(f"✓ 运行成功: {summary['success']}")
        print(f"✗ 运行失败: {summary['failed']}")
        print(f"成功率: {summary['success']/summary['has_code']*100:.1f}%" if summary['has_code'] > 0 else "N/A")
        print(f"\n图片统计:")
        print(f"  运行前: {summary['images_before']} 张")
        print(f"  运行后: {summary['images_after']} 张")
        print(f"  新生成: {summary['images_generated']} 张")
        print("=" * 70)


def main():
    """主函数"""
    generator = ImageGenerator()

    # 发现并生成图片
    summary = generator.discover_and_generate()

    # 打印摘要
    generator.print_summary(summary)

    # 保存结果
    report_path = Path('/home/user/CHS-Books/IMAGE_GENERATION_REPORT.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n详细报告已保存: {report_path}")

    return summary


if __name__ == '__main__':
    main()
