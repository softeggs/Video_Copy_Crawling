from typing import Dict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils.logger import logger
from utils.config import config

class ProcessedContent(BaseModel):
    """结构化的处理结果"""
    title: str = Field(description="提炼的标题")
    core_points: list[str] = Field(description="核心观点列表")
    detailed_content: str = Field(description="详细内容（书面语）")
    golden_sentences: list[str] = Field(description="金句提取")
    tags: list[str] = Field(description="内容标签")
    summary: str = Field(description="一句话总结")

class AIProcessor:
    def __init__(self, provider: Optional[str] = None):
        """初始化 AI 处理器
        
        Args:
            provider: AI 提供商 ('openai' 或 'gemini')，默认使用配置文件中的设置
        """
        self.provider = provider or config.AI_PROVIDER
        self.enable_polish = config.ENABLE_AI_POLISH
        
        if self.enable_polish:
            if self.provider == "gemini":
                logger.info("使用 Google Gemini API")
                self.llm = ChatGoogleGenerativeAI(
                    model=config.GEMINI_MODEL,
                    google_api_key=config.GEMINI_API_KEY,
                    temperature=0.3
                )
            else:  # openai
                logger.info("使用 OpenAI API")
                self.llm = ChatOpenAI(
                    model=config.OPENAI_MODEL,
                    api_key=config.OPENAI_API_KEY,
                    temperature=0.3
                )
            self.parser = PydanticOutputParser(pydantic_object=ProcessedContent)
        else:
            logger.info("AI 润色已禁用，将使用原始转录文本")
            self.llm = None
            self.parser = None
    
    async def process(self, raw_text: str, metadata: Dict, progress_callback=None) -> ProcessedContent:
        """AI 处理与润色"""
        try:
            # 如果禁用 AI 润色，返回基础处理结果
            if not self.enable_polish:
                if progress_callback:
                    progress_callback("跳过 AI 处理，使用原始文本...")
                
                logger.info("AI 润色已禁用，返回基础处理结果")
                return self._create_basic_content(raw_text, metadata)
            
            if progress_callback:
                progress_callback(f"AI 正在分析内容（{self.provider}）...")
            
            logger.info(f"开始 AI 处理（提供商: {self.provider}）")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """你是一个专业的内容编辑，擅长将口语化的视频文案转化为结构化的书面笔记。

任务要求：
1. 清洗口癖：去除"呃"、"然后"、"那个"等口语化表达
2. 纠正错别字：修正 ASR 识别的同音错误
3. 结构化：提炼核心观点、详细内容、金句
4. 书面化：将口语转化为流畅的书面语
5. 提取标签：生成 3-5 个内容标签

{format_instructions}"""),
                ("user", """原始标题：{title}
作者：{author}

原始文案（ASR 识别结果）：
{raw_text}

请处理上述内容。""")
            ])
            
            chain = prompt | self.llm | self.parser
            
            result = await chain.ainvoke({
                "title": metadata.get('title', ''),
                "author": metadata.get('author', ''),
                "raw_text": raw_text,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            logger.info("AI 处理完成")
            
            if progress_callback:
                progress_callback("AI 处理完成")
            
            return result
            
        except Exception as e:
            logger.error(f"AI 处理失败: {str(e)}")
            raise
    
    def _create_basic_content(self, raw_text: str, metadata: Dict) -> ProcessedContent:
        """创建基础内容（不使用 AI 润色）"""
        # 简单的文本清理
        cleaned_text = raw_text.strip()
        
        # 按句子分割
        sentences = [s.strip() for s in cleaned_text.split('。') if s.strip()]
        
        # 提取前 3 个句子作为核心观点
        core_points = sentences[:min(3, len(sentences))]
        
        # 提取较长的句子作为金句
        golden_sentences = [s for s in sentences if len(s) > 20][:3]
        
        # 简单的标签提取（基于标题）
        title = metadata.get('title', '未知标题')
        tags = ['视频笔记', '原始转录']
        
        return ProcessedContent(
            title=title,
            core_points=core_points if core_points else ['内容转录完成'],
            detailed_content=cleaned_text,
            golden_sentences=golden_sentences if golden_sentences else [],
            tags=tags,
            summary=sentences[0] if sentences else '视频内容转录'
        )
    
    def generate_markdown(self, content: ProcessedContent, metadata: Dict) -> str:
        """生成 Markdown 格式笔记"""
        ai_note = "AI 自动生成" if self.enable_polish else "原始转录（未经 AI 润色）"
        provider_note = f"（{self.provider.upper()}）" if self.enable_polish else ""
        
        md = f"""# {content.title}

> 📹 来源：{metadata.get('author', '未知')}  
> 🔗 链接：{metadata.get('url', '')}  
> 📅 日期：{metadata.get('upload_date', '')}

## 📌 一句话总结

{content.summary}

## 💡 核心观点

"""
        for i, point in enumerate(content.core_points, 1):
            md += f"{i}. {point}\n"
        
        md += f"""
## 📝 详细内容

{content.detailed_content}
"""
        
        if content.golden_sentences:
            md += """
## ✨ 金句摘录

"""
            for sentence in content.golden_sentences:
                md += f"> {sentence}\n\n"
        
        md += f"""
## 🏷️ 标签

{' '.join([f'`{tag}`' for tag in content.tags])}

---

*本笔记由 {ai_note}{provider_note}*
"""
        return md
