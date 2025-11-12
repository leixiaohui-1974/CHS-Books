"""
文本处理工具 - 简化版（不依赖jieba）
"""
import re
from typing import List


class TextProcessor:
    """文本处理类"""
    
    def __init__(self):
        """初始化"""
        pass
    
    def clean_text(self, text: str) -> str:
        """
        清洗文本
        - 移除特殊字符
        - 标准化空白字符
        """
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除首尾空白
        text = text.strip()
        return text
    
    def split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        分割长文本为多个块
        
        Args:
            text: 原始文本
            chunk_size: 每块的字符数
            overlap: 重叠字符数
            
        Returns:
            文本块列表
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 如果不是最后一块，尝试在句号、换行等位置分割
            if end < len(text):
                # 查找最近的句号、换行等
                for delimiter in ['\n\n', '\n', '。', '！', '？', '.', '!', '?']:
                    pos = text[start:end].rfind(delimiter)
                    if pos != -1:
                        end = start + pos + len(delimiter)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 移动起始位置（考虑重叠）
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取关键词（简化版 - 基于词频）
        
        Args:
            text: 文本
            top_k: 返回前k个关键词
            
        Returns:
            关键词列表
        """
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 分词（简单按空格分割）
        words = text.lower().split()
        
        # 常见停用词
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
            '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这',
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        # 过滤停用词并统计词频
        word_freq = {}
        for word in words:
            word = word.strip()
            if len(word) > 1 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按词频排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, _ in sorted_words[:top_k]]
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        生成摘要（简化版 - 截取前N个字符）
        
        Args:
            text: 原始文本
            max_length: 最大长度
            
        Returns:
            摘要文本
        """
        # 清洗文本
        text = self.clean_text(text)
        
        if len(text) <= max_length:
            return text
        
        # 截取并在句子边界结束
        summary = text[:max_length]
        
        # 尝试在最后一个句号处截断
        for delimiter in ['。', '！', '？', '.', '!', '?']:
            pos = summary.rfind(delimiter)
            if pos != -1:
                return summary[:pos + 1]
        
        return summary + '...'


# 创建全局实例
text_processor = TextProcessor()
