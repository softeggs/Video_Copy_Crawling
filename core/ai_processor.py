from typing import Dict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils.logger import logger
from utils.config import config
import asyncio

class ProcessedContent(BaseModel):
    """结构化的处理结果"""
    title: str = Field(description="视频标题")
    corrected_text: str = Field(description="纠错后的完整文本")
    core_points: list[str] = Field(description="核心观点列表")
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
        
        # 超时和重试配置
        self.timeout = 60  # 60 秒超时
        self.max_retries = 3  # 最多重试 3 次
        
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
                openai_kwargs = {
                    "model": config.OPENAI_MODEL,
                    "api_key": config.OPENAI_API_KEY,
                    "temperature": 0.3,
                    "streaming": False  # 关闭流式传输（中转 API 建议）
                }
                # 如果配置了 base_url，则使用中转 API
                if config.OPENAI_BASE_URL:
                    openai_kwargs["base_url"] = config.OPENAI_BASE_URL
                    logger.info(f"使用中转 API: {config.OPENAI_BASE_URL}")
                
                self.llm = ChatOpenAI(**openai_kwargs)
            self.parser = PydanticOutputParser(pydantic_object=ProcessedContent)
        else:
            logger.info("AI 纠错已禁用，将使用原始转录文本")
            self.llm = None
            self.parser = None
    
    async def _process_with_timeout(self, raw_text: str, metadata: Dict) -> ProcessedContent:
        """带超时的 AI 处理（单次尝试）"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """# Role
你是一位精通中文语境、短视频口播逻辑和文字校对的资深编辑。你擅长将模糊、含混的语音转文字（ASR）结果修复为逻辑通顺、表达准确的专业文案。

# Task
请对提供的视频 ASR 原始文本进行智能纠错和优化，同时提取结构化信息。

# Guidelines
1. **同音字修正**：根据上下文语境和视频标题/标签，修正拼音相似但字义错误的词（例如：将"视屏"改为"视频"，"具体"改为"锯体"等）
2. **术语校准**：识别并修正特定行业术语、品牌名或专有名词，参考视频标题中的关键词
3. **断句优化**：修正 ASR 产生的错误断句，添加正确的标点符号，使表达符合人类口播的自然停顿
4. **口语去噪**：去除无意义的语气词（如：呃、啊、这个、那个、然后），但保留口播的亲和力和自然感
5. **忠于原意**：严禁改变原作者的核心观点和表达方式，仅做文字层面的修复，保持原文结构和语序不变
6. **结构化提取**：在纠错的基础上，提取核心观点、金句和标签

# Important
- 不要重写或改写内容，只做纠错和优化
- 保持原文的口播风格和语气
- 保持原文的逻辑顺序和段落结构

{format_instructions}"""),
            ("user", """视频标题：{title}
作者：{author}
视频标签：{tags}

原始文案（ASR 识别结果）：
{raw_text}

请对上述文案进行纠错优化，并提取结构化信息。""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        # 提取视频标签（如果有）
        tags = metadata.get('tags', [])
        tags_str = ', '.join(tags) if tags else '无'
        
        result = await chain.ainvoke({
            "title": metadata.get('title', '未知标题'),
            "author": metadata.get('author', '未知作者'),
            "tags": tags_str,
            "raw_text": raw_text,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result
    
    async def process(self, raw_text: str, metadata: Dict, progress_callback=None) -> ProcessedContent:
        """AI 处理与润色（带超时重试机制）"""
        try:
            # 如果禁用 AI 润色，返回基础处理结果
            if not self.enable_polish:
                if progress_callback:
                    progress_callback("跳过 AI 处理，使用原始文本...")
                
                logger.info("AI 纠错已禁用，返回基础处理结果")
                return self._create_basic_content(raw_text, metadata)
            
            logger.info(f"开始 AI 处理（提供商: {self.provider}，超时: {self.timeout}s，最大重试: {self.max_retries}）")
            
            # 重试循环
            for attempt in range(1, self.max_retries + 1):
                try:
                    if progress_callback:
                        if attempt == 1:
                            progress_callback(f"🤖 AI 正在分析内容（{self.provider}）...")
                        else:
                            progress_callback(f"🔄 AI 处理重试 {attempt}/{self.max_retries}...")
                    
                    logger.info(f"AI 处理尝试 {attempt}/{self.max_retries}")
                    
                    # 使用 asyncio.wait_for 添加超时控制
                    result = await asyncio.wait_for(
                        self._process_with_timeout(raw_text, metadata),
                        timeout=self.timeout
                    )
                    
                    logger.info(f"AI 处理成功（尝试 {attempt}/{self.max_retries}）")
                    
                    if progress_callback:
                        progress_callback("✅ AI 处理完成")
                    
                    return result
                
                except asyncio.TimeoutError:
                    logger.warning(f"AI 处理超时（尝试 {attempt}/{self.max_retries}，超时时间: {self.timeout}s）")
                    
                    if attempt < self.max_retries:
                        if progress_callback:
                            progress_callback(f"⏱️ AI 处理超时，准备重试...")
                        logger.info(f"准备重试 AI 处理...")
                        await asyncio.sleep(2)  # 等待 2 秒后重试
                    else:
                        logger.error(f"AI 处理超时，已达到最大重试次数 {self.max_retries}")
                        if progress_callback:
                            progress_callback(f"⚠️ AI 处理超时，跳过 AI 纠错...")
                        raise Exception(f"AI 处理超时（{self.timeout}s × {self.max_retries} 次尝试）")
                
                except Exception as e:
                    logger.error(f"AI 处理失败（尝试 {attempt}/{self.max_retries}）: {str(e)}")
                    
                    if attempt < self.max_retries:
                        if progress_callback:
                            progress_callback(f"⚠️ AI 处理出错，准备重试...")
                        logger.info(f"准备重试 AI 处理...")
                        await asyncio.sleep(2)  # 等待 2 秒后重试
                    else:
                        logger.error(f"AI 处理失败，已达到最大重试次数 {self.max_retries}")
                        if progress_callback:
                            progress_callback(f"❌ AI 处理失败，跳过 AI 纠错...")
                        raise
            
            # 理论上不会到这里，但为了安全起见
            raise Exception("AI 处理失败：未知错误")
            
        except Exception as e:
            logger.error(f"AI 处理最终失败: {str(e)}")
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
            corrected_text=cleaned_text,
            core_points=core_points if core_points else ['内容转录完成'],
            golden_sentences=golden_sentences if golden_sentences else [],
            tags=tags,
            summary=sentences[0] if sentences else '视频内容转录'
        )
    
    def generate_markdown(self, content: ProcessedContent, metadata: Dict) -> str:
        """生成 Markdown 格式笔记"""
        ai_note = "AI 智能纠错" if self.enable_polish else "原始转录（未经 AI 处理）"
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
## 📝 完整内容

{content.corrected_text}
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
