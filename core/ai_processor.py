import asyncio
import json
from typing import Dict, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from utils.api_balance_checker import check_api_balance, check_kimi_balance
from utils.config import config
from utils.logger import logger


class ProcessedContent(BaseModel):
    """AI 处理后的结构化内容。"""

    title: str = Field(description="标题")
    corrected_text: str = Field(description="润色后的正文")
    core_points: list[str] = Field(description="核心要点列表")
    golden_sentences: list[str] = Field(description="金句列表")
    tags: list[str] = Field(description="标签列表")
    summary: str = Field(description="摘要")
    video_type: str = Field(description="视频类型")


class AIProcessor:
    """负责 AI 润色、结构化抽取与 Markdown 生成。"""

    KIMI_MODEL_SHORT = "moonshot-v1-8k"
    KIMI_MODEL_LONG = "moonshot-v1-32k"
    TEXT_LENGTH_THRESHOLD = 2000

    AI_MODEL_TAG_PREFIX = "AI润色模型:"
    AI_POLISH_FAILED_TAG = "未进行AI润色标签"

    @staticmethod
    def _has_openai_provider() -> bool:
        return bool(config.OPENAI_API_KEY and config.OPENAI_MODEL and config.OPENAI_BASE_URL)

    @staticmethod
    def _has_gemini_provider() -> bool:
        return bool(config.GEMINI_API_KEY and config.GEMINI_MODEL)

    @staticmethod
    def _has_kimi_provider() -> bool:
        return bool(config.KIMI_API_KEY)

    def _resolve_provider(self, requested_provider: Optional[str]) -> str:
        provider = (requested_provider or config.AI_PROVIDER or "").strip().lower()
        provider_order = ["openai", "gemini", "kimi"]
        availability = {
            "openai": self._has_openai_provider(),
            "gemini": self._has_gemini_provider(),
            "kimi": self._has_kimi_provider(),
        }

        if provider in availability and availability[provider]:
            return provider

        if provider and provider in availability and not availability[provider]:
            logger.warning(f"AI provider '{provider}' configuration is incomplete, switching by priority")

        for candidate in provider_order:
            if availability[candidate]:
                if candidate != provider:
                    logger.info(f"AI provider auto-selected: {candidate}")
                return candidate

        return provider or "openai"

    def __init__(self, provider: Optional[str] = None):
        """初始化 AI 处理器。"""

        self.provider = self._resolve_provider(provider)
        self.enable_polish = config.ENABLE_AI_POLISH
        self.timeout = config.AI_TIMEOUT
        self.max_retries = 3
        self.current_model = None
        self.openai_client = None

        if self.enable_polish:
            if self.provider == "kimi":
                logger.info("Using Kimi (Moonshot AI) API")
                self.llm = None
            elif self.provider == "gemini":
                logger.info("Using Google Gemini API")
                self.llm = ChatGoogleGenerativeAI(
                    model=config.GEMINI_MODEL,
                    google_api_key=config.GEMINI_API_KEY,
                    temperature=0.3,
                )
                self.current_model = config.GEMINI_MODEL
            else:
                logger.info("Using OpenAI API")
                openai_kwargs = {"api_key": config.OPENAI_API_KEY}
                if config.OPENAI_BASE_URL:
                    openai_kwargs["base_url"] = config.OPENAI_BASE_URL
                    logger.info(f"Using OpenAI relay API: {config.OPENAI_BASE_URL}")

                self.openai_client = AsyncOpenAI(**openai_kwargs)
                self.llm = None
                self.current_model = config.OPENAI_MODEL

            self.parser = PydanticOutputParser(pydantic_object=ProcessedContent)
        else:
            logger.info("AI polish disabled; using basic processing")
            self.llm = None
            self.parser = None

    def _get_kimi_model_for_text(self, text_length: int) -> str:
        """根据文本长度选择 Kimi 模型。"""

        if text_length >= self.TEXT_LENGTH_THRESHOLD:
            model = self.KIMI_MODEL_LONG
            logger.info(
                f"Text length {text_length} >= {self.TEXT_LENGTH_THRESHOLD}, using Kimi long model: {model}"
            )
        else:
            model = self.KIMI_MODEL_SHORT
            logger.info(
                f"Text length {text_length} < {self.TEXT_LENGTH_THRESHOLD}, using Kimi short model: {model}"
            )
        return model

    def _create_kimi_llm(self, model: str) -> ChatOpenAI:
        """创建 Kimi 的 LangChain LLM 实例。"""

        return ChatOpenAI(
            model=model,
            api_key=config.KIMI_API_KEY,
            base_url=config.KIMI_BASE_URL,
            temperature=0.3,
            streaming=False,
        )

    def _parse_processed_content(self, content: str) -> ProcessedContent:
        """把模型输出解析为 ProcessedContent。"""

        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        if "properties" in data and isinstance(data["properties"], dict):
            logger.warning("Found wrapped properties payload; flattening response")
            data = data["properties"]

        required_fields = [
            "title",
            "corrected_text",
            "core_points",
            "golden_sentences",
            "tags",
            "summary",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        data.setdefault("video_type", "未知")
        return ProcessedContent(**data)

    async def _process_with_openai_responses(self, raw_text: str, metadata: Dict) -> ProcessedContent:
        """通过 OpenAI Responses API 调用中转站。"""

        tags = metadata.get("tags", [])
        tags_str = ", ".join(tags) if tags else "none"
        prompt = (
            "You clean ASR transcript text and return structured JSON only. "
            "Correct obvious transcription issues without inventing facts. "
            "Keep the original meaning and style. "
            "Return JSON with keys: title, corrected_text, core_points, "
            "golden_sentences, tags, summary, video_type.\n\n"
            f"Title: {metadata.get('title', 'Untitled')}\n"
            f"Author: {metadata.get('author', 'Unknown')}\n"
            f"Tags: {tags_str}\n\n"
            f"Raw transcript:\n{raw_text}\n\n"
            "Return valid JSON only."
        )

        response = await self.openai_client.responses.create(
            model=config.OPENAI_MODEL,
            store=False,
            input=[
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                }
            ],
        )

        content = getattr(response, "output_text", "") or ""
        if not content and hasattr(response, "model_dump"):
            data = response.model_dump()
            texts: list[str] = []
            for item in data.get("output", []):
                for part in item.get("content", []):
                    text = part.get("text") or part.get("output_text")
                    if text:
                        texts.append(text)
            content = "\n".join(texts)

        logger.debug(f"OpenAI responses output: {content[:500]}...")
        return self._parse_processed_content(content)

    async def _process_with_timeout(self, raw_text: str, metadata: Dict) -> ProcessedContent:
        """根据 provider 执行一次 AI 处理。"""

        if self.provider == "openai":
            return await self._process_with_openai_responses(raw_text, metadata)

        if self.provider == "kimi":
            model = self._get_kimi_model_for_text(len(raw_text))
            self.current_model = model
            llm = self._create_kimi_llm(model)
        else:
            llm = self.llm

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an assistant that cleans ASR transcript text and returns structured JSON.

Requirements:
1. Correct obvious transcription issues without inventing facts.
2. Keep the original meaning and style.
3. Extract title, corrected_text, core_points, golden_sentences, tags, summary, and video_type.
4. Return valid JSON only.""",
                ),
                (
                    "user",
                    """Title: {title}
Author: {author}
Tags: {tags}

Raw transcript:
{raw_text}

Return JSON only.""",
                ),
            ]
        )

        chain = prompt | llm
        tags = metadata.get("tags", [])
        tags_str = ", ".join(tags) if tags else "none"
        response = await chain.ainvoke(
            {
                "title": metadata.get("title", "Untitled"),
                "author": metadata.get("author", "Unknown"),
                "tags": tags_str,
                "raw_text": raw_text,
            }
        )

        content = response.content if hasattr(response, "content") else str(response)
        if isinstance(content, list):
            content = "\n".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )

        logger.debug(f"AI output preview: {content[:500]}...")
        return self._parse_processed_content(content)

    def build_upload_tags(self, base_tags: list[str], ai_polish_succeeded: bool) -> list[str]:
        """为飞书标签补充 AI 模型或失败标记。"""

        tags = list(base_tags or [])

        if ai_polish_succeeded:
            model_name = self.current_model or config.OPENAI_MODEL or config.GEMINI_MODEL or self.KIMI_MODEL_SHORT
            tags.append(f"{self.AI_MODEL_TAG_PREFIX}{model_name}")
        else:
            tags.append(self.AI_POLISH_FAILED_TAG)

        deduped_tags: list[str] = []
        for tag in tags:
            if tag and tag not in deduped_tags:
                deduped_tags.append(tag)
        return deduped_tags

    async def process(self, raw_text: str, metadata: Dict, progress_callback=None) -> ProcessedContent:
        """带重试和超时的 AI 处理入口。"""

        try:
            if not self.enable_polish:
                if progress_callback:
                    progress_callback("AI 润色已关闭，使用基础处理")
                logger.info("AI polish disabled; falling back to basic content")
                return self._create_basic_content(raw_text, metadata)

            logger.info(
                f"Starting AI processing with provider={self.provider}, timeout={self.timeout}s, retries={self.max_retries}"
            )

            if self.provider == "kimi":
                expected_model = self._get_kimi_model_for_text(len(raw_text))
                logger.info(f"Predicted Kimi model for current text: {expected_model}")

            for attempt in range(1, self.max_retries + 1):
                try:
                    if progress_callback:
                        if attempt == 1:
                            progress_callback(f"开始使用 {self.provider} 进行 AI 润色...")
                        else:
                            progress_callback(f"AI 润色重试中 {attempt}/{self.max_retries}...")

                    logger.info(f"AI processing attempt {attempt}/{self.max_retries}")
                    result = await asyncio.wait_for(
                        self._process_with_timeout(raw_text, metadata),
                        timeout=self.timeout,
                    )
                    logger.info(f"AI processing succeeded on attempt {attempt}/{self.max_retries}")

                    if progress_callback:
                        progress_callback("AI 润色完成")
                    return result

                except asyncio.TimeoutError:
                    logger.warning(
                        f"AI processing timed out on attempt {attempt}/{self.max_retries} after {self.timeout}s"
                    )
                    if attempt < self.max_retries:
                        if progress_callback:
                            progress_callback("AI 润色超时，正在重试...")
                        logger.info("Retrying AI processing after timeout")
                        await asyncio.sleep(2)
                    else:
                        logger.error(f"AI processing timed out after {self.max_retries} attempts")
                        if progress_callback:
                            progress_callback("AI 润色超时，转为基础处理")
                        raise Exception(
                            f"AI processing timed out ({self.timeout}s x {self.max_retries} attempts)"
                        )

                except Exception as error:
                    logger.error(
                        f"AI processing failed on attempt {attempt}/{self.max_retries}: {str(error)}"
                    )
                    if attempt < self.max_retries:
                        if progress_callback:
                            progress_callback("AI 润色失败，正在重试...")
                        logger.info("Retrying AI processing after failure")
                        await asyncio.sleep(2)
                    else:
                        logger.error(f"AI processing failed after {self.max_retries} attempts")
                        if progress_callback:
                            progress_callback("AI 润色失败，转为基础处理")
                        raise

            raise Exception("AI processing failed: unknown error")

        except Exception as error:
            logger.error(f"AI processing failed: {str(error)}")

            if self.provider == "kimi" and config.KIMI_API_KEY:
                logger.info("Checking Kimi balance...")
                try:
                    balance_result = check_kimi_balance(config.KIMI_API_KEY)
                    if balance_result and balance_result["success"]:
                        logger.info(f"Kimi balance: {balance_result['message']}")
                        if progress_callback:
                            progress_callback(balance_result["message"])
                    else:
                        logger.warning("Failed to query Kimi balance")
                except Exception as balance_error:
                    logger.warning(f"Kimi balance check failed: {str(balance_error)}")

            elif self.provider == "openai" and config.OPENAI_BASE_URL and config.OPENAI_API_KEY:
                logger.info("Checking OpenAI relay balance...")
                try:
                    balance_result = check_api_balance(
                        api_key=config.OPENAI_API_KEY,
                        base_url=config.OPENAI_BASE_URL,
                    )
                    if balance_result and balance_result["success"]:
                        logger.info(f"Relay balance: {balance_result['message']}")
                        if progress_callback:
                            progress_callback(balance_result["message"])
                    else:
                        logger.warning("Failed to query relay balance")
                except Exception as balance_error:
                    logger.warning(f"Relay balance check failed: {str(balance_error)}")

            raise

    def _create_basic_content(self, raw_text: str, metadata: Dict) -> ProcessedContent:
        """在 AI 不可用时生成基础内容。"""

        cleaned_text = raw_text.strip()
        sentences = [sentence.strip() for sentence in cleaned_text.split("。") if sentence.strip()]
        if not sentences:
            sentences = [sentence.strip() for sentence in cleaned_text.split(".") if sentence.strip()]

        core_points = sentences[: min(3, len(sentences))]
        golden_sentences = [sentence for sentence in sentences if len(sentence) > 20][:3]
        title = metadata.get("title", "Untitled")
        tags = ["transcript", "fallback"]

        return ProcessedContent(
            title=title,
            corrected_text=cleaned_text,
            core_points=core_points if core_points else ["No core points extracted"],
            golden_sentences=golden_sentences if golden_sentences else [],
            tags=tags,
            summary=sentences[0] if sentences else "No summary available",
            video_type="transcript",
        )

    def generate_markdown(self, content: ProcessedContent, metadata: Dict) -> str:
        """生成 Markdown 输出。"""

        ai_note = "AI polished" if self.enable_polish else "Basic processing only"
        provider_note = f" via {self.provider.upper()}" if self.enable_polish else ""
        joined_tags = " ".join([f"`{tag}`" for tag in content.tags])

        md = f"""# {content.title}

> Author: {metadata.get('author', 'Unknown')}  
> URL: {metadata.get('url', '')}  
> Upload Date: {metadata.get('upload_date', '')}

## Summary

{content.summary}

## Core Points

"""
        for index, point in enumerate(content.core_points, 1):
            md += f"{index}. {point}\n"

        md += f"""
## Corrected Text

{content.corrected_text}
"""

        if content.golden_sentences:
            md += """
## Golden Sentences

"""
            for sentence in content.golden_sentences:
                md += f"> {sentence}\n\n"

        md += f"""
## Tags

{joined_tags}

---

*Generated by pipeline{provider_note}; {ai_note}*
"""
        return md
