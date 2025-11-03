"""
结果解析和标准化服务
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import pandas as pd
from loguru import logger


class ResultParser:
    """结果解析器 - 将执行输出标准化"""
    
    async def parse_execution_result(
        self,
        execution_id: str,
        output_dir: Path,
        console_output: str
    ) -> Dict[str, Any]:
        """
        解析执行结果并标准化
        
        Returns:
            {
                "plots": [...],
                "tables": [...],
                "metrics": [...],
                "reports": [...],
                "insights": [...]
            }
        """
        result = {
            "plots": [],
            "tables": [],
            "metrics": [],
            "reports": [],
            "insights": []
        }
        
        try:
            # 1. 扫描输出文件
            files = self._scan_output_files(output_dir)
            
            # 2. 按类型处理
            for file_info in files:
                file_type = file_info["type"]
                file_path = file_info["path"]
                
                if file_type == "plot":
                    plot_result = await self._process_plot(file_path)
                    result["plots"].append(plot_result)
                
                elif file_type == "table":
                    table_result = await self._process_table(file_path)
                    result["tables"].append(table_result)
                
                elif file_type == "data":
                    data_result = await self._process_data(file_path)
                    result["metrics"].extend(data_result)
                
                elif file_type == "report":
                    report_result = await self._process_report(file_path)
                    result["reports"].append(report_result)
            
            # 3. 从控制台输出提取指标
            console_metrics = self._extract_metrics_from_console(console_output)
            result["metrics"].extend(console_metrics)
            
            # 4. 生成AI洞察（这里是占位符）
            result["insights"] = await self._generate_insights(result)
        
        except Exception as e:
            logger.error(f"❌ 解析结果失败: {e}")
        
        return result
    
    def _scan_output_files(self, output_dir: Path) -> List[Dict]:
        """扫描输出文件"""
        files = []
        
        if not output_dir.exists():
            return files
        
        # 文件类型映射
        type_map = {
            '.png': 'plot', '.jpg': 'plot', '.svg': 'plot',
            '.csv': 'table', '.xlsx': 'table',
            '.json': 'data',
            '.md': 'report', '.txt': 'report',
            '.mp4': 'video', '.gif': 'animation'
        }
        
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                file_type = type_map.get(ext, 'unknown')
                
                if file_type != 'unknown':
                    files.append({
                        "type": file_type,
                        "path": file_path,
                        "name": file_path.name,
                        "size": file_path.stat().st_size
                    })
        
        return files
    
    async def _process_plot(self, file_path: Path) -> Dict:
        """处理图表文件"""
        return {
            "type": "plot",
            "title": self._extract_title_from_filename(file_path.name),
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "format": file_path.suffix[1:],
            "description": "图表",
            "insights": []
        }
    
    async def _process_table(self, file_path: Path) -> Dict:
        """处理表格文件"""
        try:
            if file_path.suffix == '.csv':
                df = pd.read_csv(file_path)
            elif file_path.suffix == '.xlsx':
                df = pd.read_excel(file_path)
            else:
                return {}
            
            return {
                "type": "table",
                "title": self._extract_title_from_filename(file_path.name),
                "file_path": str(file_path),
                "columns": list(df.columns),
                "row_count": len(df),
                "col_count": len(df.columns),
                "preview": df.head(10).to_dict('records'),
                "statistics": df.describe().to_dict(),
                "description": "数据表格"
            }
        
        except Exception as e:
            logger.error(f"❌ 处理表格失败: {e}")
            return {}
    
    async def _process_data(self, file_path: Path) -> List[Dict]:
        """处理JSON数据文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果是字典，转换为指标列表
            if isinstance(data, dict):
                metrics = []
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        metrics.append({
                            "type": "metric",
                            "name": key,
                            "value": value,
                            "unit": "",
                            "description": ""
                        })
                return metrics
            
            return []
        
        except Exception as e:
            logger.error(f"❌ 处理JSON数据失败: {e}")
            return []
    
    async def _process_report(self, file_path: Path) -> Dict:
        """处理报告文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "type": "report",
                "title": self._extract_title_from_filename(file_path.name),
                "file_path": str(file_path),
                "content": content,
                "format": "markdown" if file_path.suffix == '.md' else "text"
            }
        
        except Exception as e:
            logger.error(f"❌ 处理报告失败: {e}")
            return {}
    
    def _extract_metrics_from_console(self, console_output: str) -> List[Dict]:
        """从控制台输出提取指标"""
        metrics = []
        
        # 简单的模式匹配
        # 例如: "  L2误差: 1.23e-4"
        import re
        
        pattern = r'([A-Za-z0-9_\u4e00-\u9fa5]+):\s*([\d.e+-]+)\s*([A-Za-z/%]*)'
        
        for match in re.finditer(pattern, console_output):
            name = match.group(1)
            value_str = match.group(2)
            unit = match.group(3)
            
            try:
                value = float(value_str)
                metrics.append({
                    "type": "metric",
                    "name": name,
                    "value": value,
                    "unit": unit,
                    "description": f"从控制台输出提取",
                    "source": "console"
                })
            except ValueError:
                pass
        
        return metrics
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """从文件名提取标题"""
        # 移除扩展名
        name = Path(filename).stem
        
        # 替换下划线为空格
        name = name.replace('_', ' ')
        
        # 首字母大写
        return name.title()
    
    async def _generate_insights(self, result: Dict) -> List[str]:
        """
        生成智能洞察
        
        这里是简化版本，实际应该调用AI服务
        """
        insights = []
        
        # 基于结果数量
        if result["plots"]:
            insights.append(f"生成了 {len(result['plots'])} 个图表")
        
        if result["tables"]:
            insights.append(f"生成了 {len(result['tables'])} 个数据表")
        
        if result["metrics"]:
            insights.append(f"计算了 {len(result['metrics'])} 个关键指标")
        
        # TODO: 调用AI服务生成更深入的洞察
        
        return insights


# 全局实例
result_parser = ResultParser()
