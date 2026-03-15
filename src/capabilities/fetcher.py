"""
内容获取模块 - 从不同源获取需求内容
"""

import re
from typing import Dict, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ContentFetcher:
    """内容获取器"""
    
    # Prompt Injection 危险模式
    DANGEROUS_PATTERNS = [
        r"忽略上述指令",
        r"系统提示",
        r"<script>",
        r"```",
    ]
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.security_config = config.get("security", {})
    
    async def fetch(self, input_data: Dict[str, Any]) -> str:
        """
        获取内容
        
        Args:
            input_data: 输入数据
        
        Returns:
            内容字符串
        """
        source = input_data.get("source", "text")
        content = input_data.get("content", "")
        
        logger.info(f"获取内容，源：{source}, 长度：{len(content)}")
        
        # 根据源类型处理
        if source in ["feishu_message", "cli", "text"]:
            return content
        elif source == "file":
            return await self._fetch_file(content)
        elif source == "meeting_transcript":
            return await self._fetch_transcript(content)
        elif source == "voice":
            return await self._fetch_voice(content)
        else:
            return content
    
    async def _fetch_file(self, content: str) -> str:
        """从文件获取"""
        # TODO: 实际文件读取
        logger.info(f"读取文件：{content}")
        return content
    
    async def _fetch_transcript(self, content: str) -> str:
        """从会议转写获取"""
        logger.info("处理会议转写")
        # 可能需要清理转写格式
        return content
    
    async def _fetch_voice(self, content: str) -> str:
        """从语音获取（需转写）"""
        logger.info("语音转写")
        # TODO: 调用语音转写服务
        return content
    
    def sanitize(self, content: str) -> str:
        """
        安全过滤（防 Prompt Injection）
        
        Args:
            content: 原始内容
        
        Returns:
            过滤后内容
        """
        if not self.security_config.get("prompt_injection_protection", {}).get("enabled", True):
            return content
        
        # 移除危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)
        
        # 长度限制
        max_length = self.security_config.get("input_validation", {}).get("max_length", 10000)
        if len(content) > max_length:
            logger.warning(f"内容超长，截断到{max_length}字")
            content = content[:max_length]
        
        return content
