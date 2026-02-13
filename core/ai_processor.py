from typing import Dict, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils.logger import logger
from utils.config import config
from utils.api_balance_checker import check_api_balance, check_kimi_balance
import asyncio
import json

class ProcessedContent(BaseModel):
    """结构化的处理结果"""
    title: str = Field(description="视频标题")
    corrected_text: str = Field(description="纠错后的完整文本")
    core_points: list[str] = Field(description="核心观点列表")
    golden_sentences: list[str] = Field(description="金句提取")
    tags: list[str] = Field(description="内容标签")
    summary: str = Field(description="一句话总结")
    video_type: str = Field(description="视频类型分类")

class AIProcessor:
    # Kimi 模型配置：根据文本长度自动选择
    KIMI_MODEL_SHORT = "moonshot-v1-8k"   # 短文本（<2000字符，约5分钟视频）
    KIMI_MODEL_LONG = "moonshot-v1-32k"   # 长文本（>=2000字符）
    TEXT_LENGTH_THRESHOLD = 2000  # 文本长度阈值（字符数）
    
    def __init__(self, provider: Optional[str] = None):
        """初始化 AI 处理器
        
        Args:
            provider: AI 提供商 ('kimi', 'openai' 或 'gemini')，默认使用配置文件中的设置
        """
        self.provider = provider or config.AI_PROVIDER
        self.enable_polish = config.ENABLE_AI_POLISH
        
        # 超时和重试配置
        self.timeout = config.AI_TIMEOUT  # 从配置文件读取超时时间
        self.max_retries = 3  # 最多重试 3 次
        
        # 当前使用的模型（Kimi 会根据文本长度动态调整）
        self.current_model = None
        
        if self.enable_polish:
            if self.provider == "kimi":
                logger.info("使用 Kimi (Moonshot AI) API（将根据文本长度自动选择模型）")
                # Kimi 的 LLM 会在处理时动态创建，根据文本长度选择模型
                self.llm = None  # 延迟初始化
            elif self.provider == "gemini":
                logger.info("使用 Google Gemini API")
                self.llm = ChatGoogleGenerativeAI(
                    model=config.GEMINI_MODEL,
                    google_api_key=config.GEMINI_API_KEY,
                    temperature=0.3
                )
                self.current_model = config.GEMINI_MODEL
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
                self.current_model = config.OPENAI_MODEL
            self.parser = PydanticOutputParser(pydantic_object=ProcessedContent)
        else:
            logger.info("AI 纠错已禁用，将使用原始转录文本")
            self.llm = None
            self.parser = None
    
    def _get_kimi_model_for_text(self, text_length: int) -> str:
        """根据文本长度选择合适的 Kimi 模型
        
        Args:
            text_length: 文本字符数
            
        Returns:
            模型名称
        """
        if text_length >= self.TEXT_LENGTH_THRESHOLD:
            model = self.KIMI_MODEL_LONG
            logger.info(f"文本长度 {text_length} 字符 >= {self.TEXT_LENGTH_THRESHOLD}，使用长文本模型: {model}")
        else:
            model = self.KIMI_MODEL_SHORT
            logger.info(f"文本长度 {text_length} 字符 < {self.TEXT_LENGTH_THRESHOLD}，使用短文本模型: {model}")
        return model
    
    def _create_kimi_llm(self, model: str) -> ChatOpenAI:
        """创建 Kimi LLM 实例
        
        Args:
            model: 模型名称
            
        Returns:
            ChatOpenAI 实例
        """
        return ChatOpenAI(
            model=model,
            api_key=config.KIMI_API_KEY,
            base_url=config.KIMI_BASE_URL,
            temperature=0.3,
            streaming=False
        )
    
    async def _process_with_timeout(self, raw_text: str, metadata: Dict) -> ProcessedContent:
        """带超时的 AI 处理（单次尝试）"""
        
        # 如果是 Kimi，根据文本长度动态选择模型
        if self.provider == "kimi":
            text_length = len(raw_text)
            model = self._get_kimi_model_for_text(text_length)
            self.current_model = model
            llm = self._create_kimi_llm(model)
        else:
            llm = self.llm
        
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
7. **视频类型分类**：根据视频标题、内容和标签，判断视频类型

# Video Type Classification
请根据视频内容将视频分类为以下类型之一：

**工具推荐类**：
- 网站推荐：推荐实用网站、在线工具
- APP推荐：推荐手机应用、软件工具
- 软件推荐：推荐电脑软件、开发工具
- 插件推荐：推荐浏览器插件、编辑器插件

**资讯类**：
- 科技资讯：科技新闻、行业动态
- 产品资讯：新品发布、产品更新
- 行业资讯：行业趋势、市场分析

**教程类**：
- 技术教程：编程、开发、技术讲解
- 使用教程：软件使用、工具教程
- 技巧分享：实用技巧、经验分享

**评测类**：
- 产品评测：数码产品、硬件评测
- 软件评测：应用评测、工具对比
- 服务评测：平台服务、在线服务

**其他类**：
- 开箱视频：产品开箱、首发体验
- 生活分享：日常分享、生活记录
- 观点评论：个人观点、话题讨论
- 其他：无法归类的内容

# Important
- 不要重写或改写内容，只做纠错和优化
- 保持原文的口播风格和语气
- 保持原文的逻辑顺序和段落结构
- 视频类型必须从上述分类中选择一个最合适的

# Output Format
请直接返回 JSON 格式，包含以下字段（不要嵌套在 properties 或其他字段中），示例格式如下（注意：直接返回数据，不要包含示例中的占位文字）：

title: 视频标题
corrected_text: 纠错后的完整文本
core_points: 核心观点列表（数组）
golden_sentences: 金句列表（数组）
tags: 标签列表（数组）
summary: 一句话总结
video_type: 视频类型（从上述分类中选择一个）"""),
            ("user", """视频标题：{title}
作者：{author}
视频标签：{tags}

原始文案（ASR 识别结果）：
{raw_text}

请对上述文案进行纠错优化，并提取结构化信息。直接返回 JSON 格式，不要添加任何额外的说明文字。""")
        ])
        
        chain = prompt | llm
        
        # 提取视频标签（如果有）
        tags = metadata.get('tags', [])
        tags_str = ', '.join(tags) if tags else '无'
        
        response = await chain.ainvoke({
            "title": metadata.get('title', '未知标题'),
            "author": metadata.get('author', '未知作者'),
            "tags": tags_str,
            "raw_text": raw_text
        })
        
        # 提取响应内容
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        
        logger.debug(f"AI 原始响应: {content[:500]}...")
        
        # 尝试解析 JSON
        try:
            # 清理可能的 markdown 代码块标记
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # 解析 JSON
            data = json.loads(content)
            
            # 处理可能的嵌套结构（properties 字段）
            if 'properties' in data and isinstance(data['properties'], dict):
                logger.warning("检测到嵌套的 properties 字段，自动提取")
                data = data['properties']
            
            # 验证必需字段
            required_fields = ['title', 'corrected_text', 'core_points', 'golden_sentences', 'tags', 'summary']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                raise ValueError(f"缺少必需字段: {missing_fields}")
            
            # 创建 ProcessedContent 对象
            result = ProcessedContent(**data)
            logger.info("AI 响应解析成功")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}")
            logger.error(f"原始内容: {content[:1000]}")
            raise ValueError(f"AI 返回的不是有效的 JSON 格式: {str(e)}")
        except Exception as e:
            logger.error(f"数据解析失败: {str(e)}")
            logger.error(f"解析的数据: {data if 'data' in locals() else 'N/A'}")
            raise
    
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
            
            # 对于 Kimi，预先计算文本长度并显示将使用的模型
            if self.provider == "kimi":
                text_length = len(raw_text)
                expected_model = self._get_kimi_model_for_text(text_length)
                logger.info(f"文本长度: {text_length} 字符，预计使用模型: {expected_model}")
            
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
            
            # 在失败时查询 API 余额
            if self.provider == "kimi" and config.KIMI_API_KEY:
                # Kimi 余额查询
                logger.info("正在查询 Kimi API 余额...")
                try:
                    balance_result = check_kimi_balance(config.KIMI_API_KEY)
                    
                    if balance_result and balance_result['success']:
                        logger.info(f"Kimi 余额: {balance_result['message']}")
                        if progress_callback:
                            progress_callback(f"💰 {balance_result['message']}")
                    else:
                        logger.warning("无法查询 Kimi 余额")
                except Exception as balance_error:
                    logger.warning(f"查询 Kimi 余额时出错: {str(balance_error)}")
            
            elif self.provider == "openai" and config.OPENAI_BASE_URL and config.OPENAI_API_KEY:
                # OpenAI 中转 API 余额查询
                logger.info("正在查询 API Key 余额...")
                try:
                    balance_result = check_api_balance(
                        api_key=config.OPENAI_API_KEY,
                        base_url=config.OPENAI_BASE_URL
                    )
                    
                    if balance_result and balance_result['success']:
                        logger.info(f"API 余额: {balance_result['message']}")
                        if progress_callback:
                            progress_callback(f"💰 {balance_result['message']}")
                    else:
                        logger.warning("无法查询 API 余额")
                except Exception as balance_error:
                    logger.warning(f"查询余额时出错: {str(balance_error)}")
            
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
            summary=sentences[0] if sentences else '视频内容转录',
            video_type='其他'  # 未经 AI 分析，默认为"其他"
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
