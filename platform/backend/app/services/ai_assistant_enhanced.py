"""
增强版AI助手服务
提供代码讲解、错误诊断、结果洞察等功能
"""

from typing import List, Dict, Any, Optional
from loguru import logger
import json


class AIAssistantService:
    """AI助手服务"""
    
    def __init__(self, model: str = "gpt-4"):
        """
        初始化AI助手
        
        Args:
            model: AI模型名称
        """
        self.model = model
        self.conversation_history: Dict[str, List[Dict]] = {}
    
    async def explain_code(
        self,
        code: str,
        context: Optional[str] = None
    ) -> str:
        """
        讲解代码
        
        Args:
            code: 代码片段
            context: 上下文信息
            
        Returns:
            代码讲解文本
        """
        prompt = f"""
请详细讲解以下Python代码，包括：
1. 代码的主要功能
2. 关键步骤说明
3. 使用的算法或方法
4. 需要注意的地方

代码:
```python
{code}
```

{f'上下文: {context}' if context else ''}

请用中文回答，讲解要清晰易懂。
"""
        
        # 这里应该调用实际的LLM API
        # 为了演示，返回模拟结果
        explanation = f"""
## 代码功能说明

这段代码主要完成以下功能：
- 数据初始化和预处理
- 数值计算和求解
- 结果可视化

## 关键步骤

1. **数据准备**: 设置问题参数和初始条件
2. **数值求解**: 使用有限差分法进行迭代计算
3. **结果处理**: 生成图表和报告

## 技术要点

- 使用NumPy进行高效数组计算
- 采用Matplotlib进行可视化
- 注意数值稳定性条件

(这是演示版本，生产环境应调用实际的AI模型)
"""
        
        logger.info(f"🤖 代码讲解完成")
        return explanation
    
    async def diagnose_error(
        self,
        code: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        诊断代码错误
        
        Args:
            code: 出错的代码
            error_message: 错误信息
            stack_trace: 堆栈跟踪
            
        Returns:
            {
                "diagnosis": str,  # 错误原因分析
                "suggestions": list,  # 修复建议
                "fixed_code": str  # 修复后的代码（可选）
            }
        """
        diagnosis = {
            "diagnosis": f"检测到错误: {error_message}",
            "suggestions": [
                "检查变量名是否正确",
                "检查函数参数类型",
                "检查数组索引范围",
                "检查依赖库是否安装"
            ],
            "fixed_code": None
        }
        
        # 简单的错误模式匹配
        if "NameError" in error_message:
            diagnosis["diagnosis"] = "变量未定义错误"
            diagnosis["suggestions"] = [
                "检查变量名拼写",
                "确保变量在使用前已定义",
                "检查变量作用域"
            ]
        
        elif "IndexError" in error_message:
            diagnosis["diagnosis"] = "数组索引越界"
            diagnosis["suggestions"] = [
                "检查数组长度",
                "确认索引范围正确",
                "使用len()检查边界"
            ]
        
        elif "TypeError" in error_message:
            diagnosis["diagnosis"] = "类型错误"
            diagnosis["suggestions"] = [
                "检查变量类型",
                "使用类型转换函数",
                "查看函数参数要求"
            ]
        
        logger.info(f"🔍 错误诊断完成")
        return diagnosis
    
    async def generate_insights(
        self,
        result_data: Dict[str, Any]
    ) -> List[str]:
        """
        从计算结果生成洞察
        
        Args:
            result_data: 结果数据
            
        Returns:
            洞察列表
        """
        insights = []
        
        # 分析图表数量
        if "plots" in result_data:
            plot_count = len(result_data["plots"])
            if plot_count > 0:
                insights.append(f"✅ 成功生成 {plot_count} 个图表，可视化效果良好")
        
        # 分析数值指标
        if "metrics" in result_data:
            metrics = result_data["metrics"]
            for metric in metrics[:3]:  # 只分析前3个
                name = metric.get("name", "")
                value = metric.get("value", 0)
                
                insights.append(f"📊 {name} = {value:.4f}")
        
        # 分析表格数据
        if "tables" in result_data:
            for table in result_data["tables"][:2]:
                rows = table.get("row_count", 0)
                cols = table.get("col_count", 0)
                insights.append(f"📋 数据表包含 {rows} 行 × {cols} 列")
        
        # 添加通用建议
        insights.append("💡 可以尝试调整参数观察结果变化")
        insights.append("💡 建议与理论解对比验证精度")
        
        logger.info(f"💡 生成 {len(insights)} 条洞察")
        return insights
    
    async def answer_question(
        self,
        session_id: str,
        question: str,
        context: Optional[Dict] = None
    ) -> str:
        """
        回答问题
        
        Args:
            session_id: 会话ID
            question: 用户问题
            context: 上下文（代码、案例信息等）
            
        Returns:
            回答文本
        """
        # 获取对话历史
        history = self.conversation_history.get(session_id, [])
        
        # 添加当前问题到历史
        history.append({
            "role": "user",
            "content": question
        })
        
        # 这里应该调用实际的LLM API
        # 演示版本返回模拟答案
        answer = f"""
感谢您的提问！关于"{question}"，我来为您解答：

这是一个很好的问题。根据相关理论和实践经验：

1. **理论基础**: [这里应该是相关的理论说明]
2. **实际应用**: [这里应该是应用场景]
3. **注意事项**: [这里应该是注意点]

如果您想了解更多细节，可以：
- 查看相关章节的教材内容
- 运行示例代码观察效果
- 尝试调整参数进行实验

(这是演示版本，生产环境会调用实际的AI模型并结合RAG知识库)
"""
        
        # 添加答案到历史
        history.append({
            "role": "assistant",
            "content": answer
        })
        
        # 保存历史（限制长度）
        self.conversation_history[session_id] = history[-20:]  # 只保留最近20条
        
        logger.info(f"💬 回答问题: {question[:50]}...")
        return answer
    
    async def suggest_parameters(
        self,
        case_type: str,
        current_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        推荐参数设置
        
        Args:
            case_type: 案例类型
            current_params: 当前参数
            
        Returns:
            推荐的参数和理由
        """
        suggestions = {
            "recommended_params": current_params.copy(),
            "reasons": [],
            "alternatives": []
        }
        
        # 简单的规则基于推荐
        if "nx" in current_params and current_params["nx"] < 50:
            suggestions["recommended_params"]["nx"] = 100
            suggestions["reasons"].append("建议增加空间网格数以提高精度")
        
        if "nt" in current_params:
            suggestions["alternatives"].append({
                "param": "nt",
                "value": current_params["nt"] * 2,
                "reason": "增加时间步数可以观察更长时间的演化"
            })
        
        logger.info(f"🎯 生成参数建议")
        return suggestions
    
    def clear_conversation(self, session_id: str):
        """清除对话历史"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
            logger.info(f"🗑️  清除对话历史: {session_id}")


# 全局实例
ai_assistant_service = AIAssistantService()
