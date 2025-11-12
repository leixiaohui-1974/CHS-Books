"""
高级分析模块 - 统计报表和趋势分析
"""
import sys
sys.path.insert(0, '.')

from typing import Dict, List, Any
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json

from .knowledge_manager import knowledge_manager
from .cache_manager import cache_manager


class AdvancedAnalytics:
    """高级分析系统"""
    
    def __init__(self):
        self.query_log = []  # 查询日志
        self.access_log = []  # 访问日志
        
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成综合报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'knowledge_base': self._analyze_knowledge_base(),
            'content_quality': self._analyze_content_quality(),
            'coverage': self._analyze_coverage(),
            'system_performance': self._analyze_system_performance(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _analyze_knowledge_base(self) -> Dict[str, Any]:
        """分析知识库统计"""
        stats = knowledge_manager.get_statistics()
        
        # 按分类统计
        category_analysis = {}
        for category, count in stats['by_category'].items():
            if isinstance(count, dict):
                category_analysis[category] = {
                    'count': count['count'],
                    'percentage': count['count'] / stats['total'] * 100,
                    'levels': count.get('levels', {})
                }
            else:
                # 如果是简单的计数
                category_analysis[category] = {
                    'count': count,
                    'percentage': count / stats['total'] * 100,
                    'levels': {}
                }
        
        # 按层级统计
        level_analysis = {}
        for level, count in stats['by_level'].items():
            level_analysis[level] = {
                'count': count,
                'percentage': count / stats['total'] * 100
            }
        
        # 按来源统计
        source_analysis = {}
        for source, count in stats['by_source'].items():
            source_analysis[source] = {
                'count': count,
                'percentage': count / stats['total'] * 100
            }
        
        return {
            'total': stats['total'],
            'categories': len(stats['by_category']),
            'levels': len(stats['by_level']),
            'category_distribution': category_analysis,
            'level_distribution': level_analysis,
            'source_distribution': source_analysis
        }
    
    def _analyze_content_quality(self) -> Dict[str, Any]:
        """分析内容质量"""
        all_knowledge = []
        
        for category_key, items in knowledge_manager.knowledge_data.items():
            all_knowledge.extend(items)
        
        # 内容长度分析
        content_lengths = [len(item.get('content', '')) for item in all_knowledge]
        
        avg_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        min_length = min(content_lengths) if content_lengths else 0
        max_length = max(content_lengths) if content_lengths else 0
        
        # 长度分布
        length_categories = {
            '简短(<200字)': sum(1 for l in content_lengths if l < 200),
            '中等(200-500字)': sum(1 for l in content_lengths if 200 <= l < 500),
            '详细(500-1000字)': sum(1 for l in content_lengths if 500 <= l < 1000),
            '完整(>=1000字)': sum(1 for l in content_lengths if l >= 1000)
        }
        
        # 标题长度分析
        title_lengths = [len(item.get('title', '')) for item in all_knowledge]
        avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
        
        return {
            'content_length': {
                'average': avg_length,
                'min': min_length,
                'max': max_length,
                'distribution': length_categories
            },
            'title_length': {
                'average': avg_title_length,
                'min': min(title_lengths) if title_lengths else 0,
                'max': max(title_lengths) if title_lengths else 0
            },
            'quality_score': self._calculate_quality_score(all_knowledge)
        }
    
    def _calculate_quality_score(self, knowledge_list: List[Dict]) -> Dict[str, Any]:
        """计算知识质量分数"""
        scores = []
        
        for item in knowledge_list:
            score = 0
            
            # 标题质量（0-20分）
            title = item.get('title', '')
            if 5 <= len(title) <= 50:
                score += 20
            elif len(title) > 0:
                score += 10
            
            # 内容质量（0-40分）
            content = item.get('content', '')
            if len(content) >= 500:
                score += 40
            elif len(content) >= 200:
                score += 30
            elif len(content) >= 100:
                score += 20
            elif len(content) > 0:
                score += 10
            
            # 分类信息（0-20分）
            if item.get('category'):
                score += 10
            if item.get('level'):
                score += 10
            
            # 来源信息（0-20分）
            if item.get('source_type'):
                score += 10
            if item.get('source_name'):
                score += 10
            
            scores.append(score)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # 分级
        grade = 'A' if avg_score >= 80 else 'B' if avg_score >= 60 else 'C' if avg_score >= 40 else 'D'
        
        return {
            'average': avg_score,
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
            'grade': grade,
            'distribution': {
                '优秀(>=80)': sum(1 for s in scores if s >= 80),
                '良好(60-79)': sum(1 for s in scores if 60 <= s < 80),
                '及格(40-59)': sum(1 for s in scores if 40 <= s < 60),
                '待改进(<40)': sum(1 for s in scores if s < 40)
            }
        }
    
    def _analyze_coverage(self) -> Dict[str, Any]:
        """分析知识覆盖度"""
        stats = knowledge_manager.get_statistics()
        
        # 预期的分类和层级
        expected_categories = [
            '水力学', '土力学', '工程力学', '工程测量',
            '水工建筑物', '水电工程', '水资源', '施工技术',
            '规范标准', '工程管理'
        ]
        
        expected_levels = ['本科', '硕士', '博士', '通用']
        
        # 计算覆盖率
        actual_categories = set(stats['by_category'].keys())
        category_coverage = len(actual_categories) / len(expected_categories) * 100
        
        actual_levels = set(stats['by_level'].keys())
        level_coverage = len(actual_levels) / len(expected_levels) * 100
        
        # 识别缺失和薄弱环节
        missing_categories = [c for c in expected_categories if c not in actual_categories]
        weak_categories = []
        for c, count_or_info in stats['by_category'].items():
            count = count_or_info['count'] if isinstance(count_or_info, dict) else count_or_info
            if count < 5:
                weak_categories.append(c)
        
        return {
            'category_coverage': category_coverage,
            'level_coverage': level_coverage,
            'missing_categories': missing_categories,
            'weak_categories': weak_categories,
            'strong_categories': [
                c for c, count_or_info in stats['by_category'].items()
                if (count_or_info['count'] if isinstance(count_or_info, dict) else count_or_info) >= 10
            ],
            'balance_score': self._calculate_balance_score(stats)
        }
    
    def _calculate_balance_score(self, stats: Dict) -> float:
        """计算知识分布平衡分数（0-100）"""
        category_counts = []
        for count_or_info in stats['by_category'].values():
            count = count_or_info['count'] if isinstance(count_or_info, dict) else count_or_info
            category_counts.append(count)
        
        if not category_counts:
            return 0
        
        # 计算标准差
        avg_count = sum(category_counts) / len(category_counts)
        variance = sum((c - avg_count) ** 2 for c in category_counts) / len(category_counts)
        std_dev = variance ** 0.5
        
        # 标准差越小，平衡性越好
        # 假设std_dev=0时100分，std_dev>=10时0分
        balance_score = max(0, 100 - (std_dev / avg_count * 100))
        
        return balance_score
    
    def _analyze_system_performance(self) -> Dict[str, Any]:
        """分析系统性能"""
        cache_stats = cache_manager.get_stats()
        
        return {
            'cache': {
                'total_size': cache_stats['total_size'],
                'query_cache_hit_rate': cache_stats['query_cache']['hit_rate'],
                'vector_cache_hit_rate': cache_stats['vector_cache']['hit_rate'],
                'knowledge_cache_hit_rate': cache_stats['knowledge_cache']['hit_rate'],
                'overall_performance': 'excellent' if cache_stats['query_cache']['hit_rate'] > 0.5 else 'good'
            },
            'database': {
                'knowledge_count': knowledge_manager.get_statistics()['total'],
                'status': 'healthy'
            }
        }
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        stats = knowledge_manager.get_statistics()
        coverage = self._analyze_coverage()
        quality = self._analyze_content_quality()
        
        # 知识数量建议
        if stats['total'] < 50:
            recommendations.append("建议：知识库条目较少，建议增加到100条以上")
        elif stats['total'] < 100:
            recommendations.append("建议：继续扩充知识库，目标200条")
        
        # 分类覆盖建议
        if coverage['missing_categories']:
            recommendations.append(f"建议：补充缺失的分类：{', '.join(coverage['missing_categories'][:3])}")
        
        if coverage['weak_categories']:
            recommendations.append(f"建议：加强薄弱分类：{', '.join(coverage['weak_categories'][:3])}")
        
        # 内容质量建议
        avg_quality = quality['quality_score']['average']
        if avg_quality < 60:
            recommendations.append("建议：提升知识内容质量，增加详细说明和案例")
        
        # 平衡性建议
        if coverage['balance_score'] < 60:
            recommendations.append("建议：优化知识分布，使各分类更加均衡")
        
        # 性能建议
        cache_stats = cache_manager.get_stats()
        if cache_stats['query_cache']['hit_rate'] < 0.3:
            recommendations.append("建议：增加缓存容量或优化缓存策略")
        
        if not recommendations:
            recommendations.append("系统运行良好，保持当前状态")
        
        return recommendations
    
    def generate_trend_analysis(self, days: int = 7) -> Dict[str, Any]:
        """
        生成趋势分析（需要历史数据）
        
        Args:
            days: 分析天数
            
        Returns:
            趋势分析报告
        """
        # 模拟趋势数据（实际应从日志中读取）
        return {
            'period': f'最近{days}天',
            'query_trend': {
                'total_queries': len(self.query_log),
                'daily_average': len(self.query_log) / days if days > 0 else 0,
                'trend': 'stable'
            },
            'popular_categories': self._get_popular_categories(),
            'popular_keywords': self._get_popular_keywords(),
            'growth': {
                'knowledge_growth': 0,  # 需要历史数据
                'query_growth': 0
            }
        }
    
    def _get_popular_categories(self) -> List[Dict[str, Any]]:
        """获取热门分类"""
        stats = knowledge_manager.get_statistics()
        
        popular = []
        for category, count_or_info in stats['by_category'].items():
            count = count_or_info['count'] if isinstance(count_or_info, dict) else count_or_info
            popular.append({
                'category': category,
                'count': count,
                'percentage': count / stats['total'] * 100
            })
        
        popular.sort(key=lambda x: x['count'], reverse=True)
        return popular[:5]
    
    def _get_popular_keywords(self) -> List[Dict[str, int]]:
        """获取热门关键词（模拟）"""
        keywords = Counter()
        
        for category_key, items in knowledge_manager.knowledge_data.items():
            for item in items:
                # 简单分词（实际应使用jieba等）
                title = item.get('title', '')
                words = [w for w in title if len(w) > 1]
                keywords.update(words)
        
        return [{'keyword': k, 'count': v} for k, v in keywords.most_common(10)]
    
    def export_report(self, format: str = 'json') -> str:
        """
        导出报告
        
        Args:
            format: 'json' 或 'markdown' 或 'text'
            
        Returns:
            格式化的报告
        """
        report = self.generate_comprehensive_report()
        
        if format == 'json':
            return json.dumps(report, ensure_ascii=False, indent=2)
        
        elif format == 'markdown':
            return self._format_markdown_report(report)
        
        elif format == 'text':
            return self._format_text_report(report)
        
        return ""
    
    def _format_markdown_report(self, report: Dict) -> str:
        """格式化为Markdown报告"""
        md = []
        md.append("# 水利水电水务知识库 - 综合分析报告\n")
        md.append(f"**生成时间**: {report['generated_at']}\n")
        md.append("---\n")
        
        # 知识库统计
        kb = report['knowledge_base']
        md.append("## 📊 知识库统计\n")
        md.append(f"- **总条目**: {kb['total']}条\n")
        md.append(f"- **分类数**: {kb['categories']}个\n")
        md.append(f"- **层级数**: {kb['levels']}个\n\n")
        
        # 分类分布
        md.append("### 分类分布\n")
        for category, info in list(kb['category_distribution'].items())[:5]:
            md.append(f"- **{category}**: {info['count']}条 ({info['percentage']:.1f}%)\n")
        md.append("\n")
        
        # 内容质量
        quality = report['content_quality']
        md.append("## ✨ 内容质量\n")
        md.append(f"- **质量评分**: {quality['quality_score']['average']:.1f}/100\n")
        md.append(f"- **评级**: {quality['quality_score']['grade']}\n")
        md.append(f"- **平均长度**: {quality['content_length']['average']:.0f}字\n\n")
        
        # 覆盖度分析
        coverage = report['coverage']
        md.append("## 📈 覆盖度分析\n")
        md.append(f"- **分类覆盖率**: {coverage['category_coverage']:.1f}%\n")
        md.append(f"- **层级覆盖率**: {coverage['level_coverage']:.1f}%\n")
        md.append(f"- **平衡分数**: {coverage['balance_score']:.1f}/100\n\n")
        
        # 优化建议
        md.append("## 💡 优化建议\n")
        for i, rec in enumerate(report['recommendations'], 1):
            md.append(f"{i}. {rec}\n")
        
        return "".join(md)
    
    def _format_text_report(self, report: Dict) -> str:
        """格式化为文本报告"""
        lines = []
        lines.append("="*60)
        lines.append("水利水电水务知识库 - 综合分析报告")
        lines.append("="*60)
        lines.append(f"生成时间: {report['generated_at']}\n")
        
        kb = report['knowledge_base']
        lines.append("知识库统计:")
        lines.append(f"  总条目: {kb['total']}条")
        lines.append(f"  分类数: {kb['categories']}个")
        lines.append(f"  层级数: {kb['levels']}个\n")
        
        quality = report['content_quality']
        lines.append("内容质量:")
        lines.append(f"  评分: {quality['quality_score']['average']:.1f}/100")
        lines.append(f"  评级: {quality['quality_score']['grade']}\n")
        
        lines.append("优化建议:")
        for i, rec in enumerate(report['recommendations'], 1):
            lines.append(f"  {i}. {rec}")
        
        lines.append("\n" + "="*60)
        
        return "\n".join(lines)


# 全局实例
analytics = AdvancedAnalytics()


if __name__ == "__main__":
    print("=== 高级分析模块测试 ===\n")
    
    # 生成综合报告
    report = analytics.generate_comprehensive_report()
    
    print("📊 知识库统计：")
    kb = report['knowledge_base']
    print(f"  总条目：{kb['total']}")
    print(f"  分类数：{kb['categories']}")
    print(f"  层级数：{kb['levels']}")
    
    print(f"\n✨ 内容质量：")
    quality = report['content_quality']
    print(f"  质量评分：{quality['quality_score']['average']:.1f}/100")
    print(f"  评级：{quality['quality_score']['grade']}")
    print(f"  平均长度：{quality['content_length']['average']:.0f}字")
    
    print(f"\n📈 覆盖度分析：")
    coverage = report['coverage']
    print(f"  分类覆盖率：{coverage['category_coverage']:.1f}%")
    print(f"  层级覆盖率：{coverage['level_coverage']:.1f}%")
    print(f"  平衡分数：{coverage['balance_score']:.1f}/100")
    
    print(f"\n💡 优化建议：")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n\n导出Markdown报告...")
    md_report = analytics.export_report(format='markdown')
    print(md_report[:500] + "...")
