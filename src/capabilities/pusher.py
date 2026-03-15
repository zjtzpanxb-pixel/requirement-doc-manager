"""
推送发布模块 - 本地 Markdown 存储
"""

import time
from typing import Dict, Any
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DocumentPusher:
    """文档推送器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.storage_folder = config.get("storage_folder", "/需求文档库")
    
    async def push(self, prd: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        推送文档
        
        Args:
            prd: PRD 文档数据
            input_data: 原始输入数据
        
        Returns:
            存储信息
        """
        logger.info("推送文档")
        return await self._save_local(prd, input_data)
    
    async def _save_local(self, prd: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """本地存储"""
        # 创建存储目录
        storage_dir = Path(self.storage_folder)
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        filename = f"prd_{prd.get('version', int(time.time()))}.md"
        filepath = storage_dir / filename
        
        try:
            content = prd.get("content", str(prd))
            filepath.write_text(content, encoding="utf-8")
            
            logger.info(f"本地存储成功：{filepath}")
            
            return {
                "type": "markdown",
                "path": str(filepath),
            }
            
        except Exception as e:
            logger.error(f"本地存储失败：{e}")
            raise
