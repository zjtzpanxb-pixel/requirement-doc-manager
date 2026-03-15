"""
文档生成模块 - 模板填充生成 PRD 文档
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DocumentGenerator:
    """文档生成器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
    
    async def generate(
        self, 
        data: Dict[str, Any], 
        template: str = "standard",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        生成 PRD 文档
        
        Args:
            data: 需求数据
            template: 模板类型（standard/lite）
            context: 上下文信息（项目名/优先级等）
        
        Returns:
            PRD 文档数据
        """
        logger.info(f"生成文档，模板：{template}")
        
        # 生成版本号
        version = self._generate_version()
        
        # 选择模板
        template_file = self._get_template_file(template)
        
        # 填充模板
        content = await self._fill_template(template_file, data, context)
        
        # 构建 PRD 文档
        prd = {
            "title": context.get("project_name", "需求文档") if context else "需求文档",
            "version": version,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "background": self._extract_background(data),
            "user_stories": data.get("user_stories", []),
            "functional_requirements": data.get("functional_requirements", []),
            "business_rules": data.get("business_rules", []),
            "acceptance_criteria": data.get("acceptance_criteria", []),
            "risks": data.get("risks", []),
            "content": content,
        }
        
        return prd
    
    def _generate_version(self) -> str:
        """生成版本号 vYYYYMMDD-序号"""
        date_str = time.strftime("%Y%m%d")
        # 序号用时间戳后 4 位简化实现
        seq = time.strftime("%H%M")
        return f"v{date_str}-{seq}"
    
    def _get_template_file(self, template: str) -> Path:
        """获取模板文件路径"""
        template_name = f"prd_{template}.md.j2"
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            logger.warning(f"模板不存在：{template_path}，使用默认模板")
            return self.template_dir / "prd_standard.md.j2"
        
        return template_path
    
    async def _fill_template(
        self, 
        template_path: Path, 
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """填充模板（简化实现，实际用 Jinja2）"""
        # TODO: 实际使用 Jinja2 渲染
        
        # 简单模板填充演示
        content = f"""# {context.get('project_name', '需求文档') if context else '需求文档'}

**版本**: {self._generate_version()}  
**创建时间**: {time.strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. 背景

{self._extract_background(data)}

## 2. 用户故事

"""
        for i, story in enumerate(data.get("user_stories", []), 1):
            content += f"""
### {i}. {story.get('role', '用户')}
- **作为** {story.get('role', '')}
- **我想要** {story.get('need', '')}
- **以便** {story.get('benefit', '')}
"""
        
        content += """
## 3. 功能需求

"""
        for req in data.get("functional_requirements", []):
            content += f"""
### {req.get('id', 'FR-XXX')}. {req.get('title', '功能')}
{req.get('description', '')}
"""
        
        content += """
## 4. 业务规则

"""
        for rule in data.get("business_rules", []):
            content += f"- {rule}\n"
        
        content += """
## 5. 验收标准

"""
        for criteria in data.get("acceptance_criteria", []):
            content += f"- [ ] {criteria}\n"
        
        content += """
## 6. 风险

"""
        for risk in data.get("risks", []):
            level = risk.get('level', 'medium')
            content += f"- **{level.upper()}**: {risk.get('description', '')}\n"
        
        return content
    
    def _extract_background(self, data: Dict[str, Any]) -> str:
        """提取背景描述"""
        # 从功能需求中生成简单背景
        reqs = data.get("functional_requirements", [])
        if reqs:
            return f"本项目旨在实现以下功能：{reqs[0].get('title', '核心功能')}"
        return "需求背景待补充"
