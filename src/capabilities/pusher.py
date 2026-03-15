"""
推送发布模块 - 创建飞书文档或本地存储

接入飞书开放平台 API
文档：https://open.feishu.cn/document/ukTMukTMukTM/ucjz1UjL5YDM1UjM3ATN
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DocumentPusher:
    """文档推送器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feishu_config = config.get("feishu", {})
        self.storage_folder = self.feishu_config.get("storage_folder", "/需求文档库")
        
        # API 凭证从系统环境变量读取（OpenClaw 已配置）
        self.app_id = os.getenv("FEISHU_APP_ID", "")
        self.app_secret = os.getenv("FEISHU_APP_SECRET", "")
        self.use_mock = not (self.app_id and self.app_secret)
        
        if self.use_mock:
            logger.warning("FEISHU API 未配置，使用本地存储")
        else:
            logger.info("FEISHU API 已配置，使用飞书文档")
        
        # Token 缓存
        self._tenant_token: Optional[str] = None
        self._token_expire_at: float = 0
    
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
        
        # 如果没有飞书配置，直接本地存储
        if self.use_mock:
            return await self._save_local(prd, input_data)
        
        try:
            # 尝试创建飞书文档
            storage_info = await self._push_to_feishu(prd, input_data)
            return storage_info
            
        except Exception as e:
            logger.warning(f"飞书推送失败：{e}，降级到本地存储")
            return await self._save_local(prd, input_data)
    
    async def _get_tenant_token(self) -> str:
        """获取租户访问 Token"""
        # 检查缓存
        if self._tenant_token and time.time() < self._token_expire_at:
            return self._tenant_token
        
        try:
            import httpx
            
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if result.get("code") != 0:
                    raise Exception(f"获取 Token 失败：{result.get('msg')}")
                
                self._tenant_token = result["tenant_access_token"]
                self._token_expire_at = time.time() + result.get("expire", 7200) - 600  # 提前 10 分钟过期
                
                logger.info("获取飞书 Token 成功")
                return self._tenant_token
                
        except ImportError:
            logger.warning("httpx 未安装，使用本地存储")
            self.use_mock = True
            raise Exception("httpx 未安装")
        except Exception as e:
            logger.error(f"获取飞书 Token 失败：{e}")
            raise
    
    async def _push_to_feishu(self, prd: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """推送到飞书文档"""
        logger.info("创建飞书文档")
        
        try:
            import httpx
            
            # 获取 Token
            token = await self._get_tenant_token()
            
            # 1. 创建文档
            create_url = "https://open.feishu.cn/open-apis/docx/v1/documents"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            
            create_payload = {
                "title": f"{prd.get('title', '需求文档')} - {prd.get('version', '')}",
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                # 创建文档
                create_response = await client.post(create_url, headers=headers, json=create_payload)
                create_response.raise_for_status()
                create_result = create_response.json()
                
                if create_result.get("code") != 0:
                    raise Exception(f"创建文档失败：{create_result.get('msg')}")
                
                document_id = create_result["data"]["document_id"]
                document_url = f"https://feishu.cn/docx/{document_id}"
                
                logger.info(f"飞书文档创建成功：{document_url}")
                
                # 2. 更新文档内容
                content = prd.get("content", str(prd))
                await self._update_docx_content(document_id, content, token)
                
                return {
                    "type": "feishu_doc",
                    "url": document_url,
                    "document_id": document_id,
                    "folder": self.storage_folder,
                }
                
        except ImportError:
            logger.warning("httpx 未安装，使用本地存储")
            self.use_mock = True
            return await self._save_local(prd, input_data)
        except Exception as e:
            logger.error(f"飞书 API 调用失败：{e}")
            raise
    
    async def _update_docx_content(self, document_id: str, content: str, token: str) -> None:
        """更新飞书文档内容"""
        try:
            import httpx
            
            # 飞书文档内容更新 API（简化版，实际可能需要分块更新）
            update_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "content": content,
                "content_type": "markdown",
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.put(update_url, headers=headers, json=payload)
                if response.status_code != 200:
                    logger.warning(f"更新文档内容失败：{response.status_code}，但文档已创建")
                    
        except Exception as e:
            logger.warning(f"更新文档内容失败：{e}，但文档已创建")
    
    async def _save_local(self, prd: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """本地存储（降级方案）"""
        import time
        
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
                "fallback": not self.use_mock,  # 如果原本就用模拟模式，不算降级
            }
            
        except Exception as e:
            logger.error(f"本地存储失败：{e}")
            raise
