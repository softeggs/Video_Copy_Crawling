import streamlit as st
import asyncio
from pathlib import Path
from core.pipeline import ProcessingPipeline
from utils.config import config

# 页面配置
st.set_page_config(
    page_title="短视频内容情报提取系统",
    page_icon="🎬",
    layout="wide"
)

# 初始化
if 'processing' not in st.session_state:
    st.session_state.processing = False

# 标题
st.title("🎬 短视频内容情报提取系统")
st.markdown("支持抖音、B站、小红书等平台，自动提取视频文案并同步至飞书")

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 系统配置")
    
    st.subheader("AI 设置")
    
    # AI 润色开关
    enable_ai_polish = st.checkbox(
        "启用 AI 润色",
        value=config.ENABLE_AI_POLISH,
        help="关闭后将只进行语音识别，不进行 AI 处理"
    )
    
    # AI 提供商选择
    ai_provider = st.selectbox(
        "AI 提供商",
        ["openai", "gemini"],
        index=0 if config.AI_PROVIDER == "openai" else 1,
        disabled=not enable_ai_polish,
        help="选择使用 OpenAI 或 Google Gemini"
    )
    
    if enable_ai_polish:
        if ai_provider == "openai":
            st.info(f"🤖 模型: {config.OPENAI_MODEL}")
            if not config.OPENAI_API_KEY:
                st.warning("⚠️ 未配置 OpenAI API Key")
        else:
            st.info(f"🤖 模型: {config.GEMINI_MODEL}")
            if not config.GEMINI_API_KEY:
                st.warning("⚠️ 未配置 Gemini API Key")
    else:
        st.info("ℹ️ AI 润色已禁用")
    
    st.divider()
    
    st.subheader("Whisper 模型")
    whisper_model = st.selectbox(
        "语音识别模型",
        ["tiny", "base", "small", "medium", "large"],
        index=["tiny", "base", "small", "medium", "large"].index(config.WHISPER_MODEL) if config.WHISPER_MODEL in ["tiny", "base", "small", "medium", "large"] else 1,
        help="模型越大精度越高，但速度越慢\n\n• tiny: 最快，精度较低\n• base: 平衡（默认）\n• small: 较好精度\n• medium: 高精度\n• large: 最高精度，速度慢"
    )
    
    model_info = {
        "tiny": "~39M 参数，速度最快",
        "base": "~74M 参数，推荐日常使用",
        "small": "~244M 参数，较高精度",
        "medium": "~769M 参数，高精度",
        "large": "~1550M 参数，最高精度"
    }
    st.caption(model_info[whisper_model])
    
    st.divider()
    
    st.subheader("输出路径")
    st.text(f"下载: {config.DOWNLOAD_PATH}")
    st.text(f"输出: {config.OUTPUT_PATH}")
    
    st.divider()
    
    st.subheader("飞书配置")
    feishu_enabled = st.checkbox(
        "启用飞书同步",
        value=bool(config.FEISHU_APP_ID),
        help="需要配置飞书 API 密钥"
    )
    
    st.divider()
    
    st.subheader("Cookies 配置")
    
    # 导入平台检测器
    from utils.platform_detector import PlatformDetector, Platform
    
    # 选择平台
    platform_options = {
        "B站": Platform.BILIBILI,
        "小红书": Platform.XIAOHONGSHU,
        "抖音": Platform.DOUYIN
    }
    
    selected_platform_name = st.selectbox(
        "选择平台",
        list(platform_options.keys()),
        help="为不同平台配置独立的 cookies"
    )
    
    selected_platform = platform_options[selected_platform_name]
    cookies_file = PlatformDetector.get_cookies_file(selected_platform)
    
    # 初始化 session state
    session_key = f'cookies_{selected_platform.value}'
    if session_key not in st.session_state:
        # 尝试从文件加载历史 cookies
        cookies_path = Path(cookies_file)
        if cookies_path.exists():
            try:
                st.session_state[session_key] = cookies_path.read_text(encoding='utf-8')
            except:
                st.session_state[session_key] = ""
        else:
            st.session_state[session_key] = ""
    
    # 显示 cookies 状态
    if st.session_state[session_key]:
        # 统计 cookies 数量
        lines = st.session_state[session_key].split('\n')
        cookie_count = sum(1 for line in lines if line.strip() and not line.startswith('#'))
        st.success(f"✓ {selected_platform_name} Cookies 已配置（{cookie_count} 条）")
    else:
        st.info(f"ℹ️ {selected_platform_name} Cookies 未配置")
    
    # 显示所有平台状态
    with st.expander("📊 所有平台状态"):
        for name, platform in platform_options.items():
            pf_cookies = PlatformDetector.get_cookies_file(platform)
            if Path(pf_cookies).exists():
                st.text(f"✅ {name}")
            else:
                st.text(f"❌ {name}")
    
    # Cookies 输入方式选择
    input_method = st.radio(
        "输入方式",
        ["文本输入", "文件上传"],
        horizontal=True,
        key=f"cookies_input_method_{selected_platform.value}"
    )
    
    if input_method == "文本输入":
        # 文本框输入 cookies
        cookies_input = st.text_area(
            f"粘贴 {selected_platform_name} Cookies 内容",
            value=st.session_state[session_key],
            height=150,
            placeholder="# Netscape HTTP Cookie File\n.bilibili.com\tTRUE\t/\tFALSE\t1735689600\tSESSDATA\tyour_session_data",
            help=f"从浏览器开发者工具或扩展导出的 {selected_platform_name} cookies 内容",
            key=f"cookies_text_input_{selected_platform.value}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💾 保存 {selected_platform_name} Cookies", use_container_width=True, key=f"save_{selected_platform.value}"):
                if cookies_input.strip():
                    # 保存到 session state
                    st.session_state[session_key] = cookies_input
                    # 保存到文件
                    cookies_path = Path(cookies_file)
                    cookies_path.write_text(cookies_input, encoding='utf-8')
                    st.success(f"✓ {selected_platform_name} Cookies 已保存")
                    st.rerun()
                else:
                    st.warning("⚠️ Cookies 内容为空")
        
        with col2:
            if st.button(f"🗑️ 清除 {selected_platform_name} Cookies", use_container_width=True, key=f"clear_{selected_platform.value}"):
                st.session_state[session_key] = ""
                cookies_path = Path(cookies_file)
                if cookies_path.exists():
                    cookies_path.unlink()
                st.success(f"✓ {selected_platform_name} Cookies 已清除")
                st.rerun()
    
    else:  # 文件上传
        uploaded_cookies = st.file_uploader(
            f"上传 {selected_platform_name} cookies.txt",
            type=['txt'],
            help=f"从浏览器导出的 {selected_platform_name} cookies 文件",
            key=f"cookies_file_uploader_{selected_platform.value}"
        )
        
        if uploaded_cookies:
            cookies_content = uploaded_cookies.read().decode('utf-8')
            # 保存到 session state
            st.session_state[session_key] = cookies_content
            # 保存到文件
            cookies_path = Path(cookies_file)
            cookies_path.write_text(cookies_content, encoding='utf-8')
            st.success(f"✓ {selected_platform_name} Cookies 文件已上传")
            st.rerun()
    
    # 使用指南
    with st.expander("📖 如何获取 Cookies？"):
        st.markdown("""
        **方法 1：使用浏览器扩展（推荐）**
        
        Chrome:
        1. 安装 "Get cookies.txt LOCALLY" 扩展
        2. 访问网站（如 bilibili.com）并登录
        3. 点击扩展图标，导出 cookies
        4. 复制内容粘贴到上方文本框
        
        **方法 2：手动从浏览器复制**
        
        1. 打开开发者工具（F12）
        2. 访问网站并登录
        3. Application → Cookies
        4. 复制所有 cookies
        5. 转换为 Netscape 格式后粘贴
        
        **格式示例**：
        ```
        # Netscape HTTP Cookie File
        .bilibili.com	TRUE	/	FALSE	1735689600	SESSDATA	xxx
        .bilibili.com	TRUE	/	FALSE	1735689600	bili_jct	xxx
        ```
        
        **提示**：
        - Cookies 会自动保存，下次启动自动加载
        - Cookies 过期后需要重新获取
        - 建议使用测试账号
        """)
    
    if st.button("🔄 重新加载配置"):
        st.rerun()

# 主界面
tab1, tab2, tab3 = st.tabs(["📥 单个处理", "📦 批量处理", "📊 历史记录"])

with tab1:
    st.header("单个视频处理")
    
    # URL 清理选项
    col_url1, col_url2 = st.columns([4, 1])
    with col_url2:
        aggressive_clean = st.checkbox(
            "深度清理",
            value=False,
            help="移除追踪参数（可能影响某些视频访问）"
        )
    
    with col_url1:
        url_input = st.text_input(
            "视频链接",
            placeholder="输入抖音/B站/小红书视频链接...",
            disabled=st.session_state.processing,
            key="video_url_input"
        )
    
    # 自动清理 URL
    url = url_input
    if url_input:
        from utils.url_cleaner import URLCleaner
        from utils.platform_detector import PlatformDetector, Platform
        
        # 验证是否是有效的视频 URL
        if not URLCleaner.is_valid_video_url(url_input):
            st.error("⚠️ 输入的不是有效的视频链接，请检查")
            st.info("提示：请输入完整的视频 URL，例如：https://www.bilibili.com/video/...")
            url = None
        else:
            # 检测平台
            platform = PlatformDetector.detect_platform(url_input)
            platform_name = PlatformDetector.get_platform_name(platform)
            
            if platform == Platform.UNKNOWN:
                st.error(f"⚠️ 该平台暂不支持")
                st.info("当前支持的平台：B站、小红书、抖音")
                url = None
            else:
                # 清理 URL（默认保守模式，只移除敏感信息）
                cleaned_url = URLCleaner.clean_url(url_input, platform_name, aggressive=aggressive_clean)
                
                # 如果 URL 被清理了，显示提示
                if cleaned_url != url_input:
                    st.success(f"✨ 已自动清理 URL {'（深度清理）' if aggressive_clean else '（仅移除敏感信息）'}")
                    with st.expander("查看清理详情"):
                        st.text(f"原始 URL:\n{url_input}\n")
                        st.text(f"清理后 URL:\n{cleaned_url}")
                        removed = len(url_input) - len(cleaned_url)
                        st.caption(f"移除了 {removed} 个字符")
                
                url = cleaned_url
                
                st.info(f"🎯 检测到平台: {platform_name}")
                
                # 提取视频 ID
                video_id = URLCleaner.extract_video_id(url, platform_name)
                if video_id:
                    st.caption(f"视频 ID: {video_id}")
                
                # 检查是否有对应平台的 cookies
                if not PlatformDetector.check_cookies_exists(platform):
                    st.warning(f"⚠️ 未配置 {platform_name} Cookies，可能影响下载")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        process_btn = st.button(
            "🚀 开始处理",
            disabled=st.session_state.processing or not url,
            type="primary"
        )
    
    if process_btn and url:
        # 再次检查平台
        from utils.platform_detector import PlatformDetector, Platform
        platform = PlatformDetector.detect_platform(url)
        
        if platform == Platform.UNKNOWN:
            st.error("❌ 该平台暂不支持，无法处理")
            st.info("当前支持的平台：B站、小红书、抖音")
        else:
            st.session_state.processing = True
            
            # 进度显示
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(message: str):
                status_text.text(message)
            
            # 创建处理流水线（使用当前配置）
            pipeline = ProcessingPipeline(
                ai_provider=ai_provider,
                enable_ai_polish=enable_ai_polish,
                whisper_model=whisper_model
            )
            
            # 执行处理
            try:
                result = asyncio.run(
                    pipeline.process(url, update_progress)
                )
                
                progress_bar.progress(100)
                
                if result['success']:
                    st.success("✅ 处理完成！")
                    
                    # 显示结果
                    with st.expander("📋 视频信息", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**标题**: {result['metadata']['title']}")
                            st.write(f"**作者**: {result['metadata']['author']}")
                        with col2:
                            st.write(f"**日期**: {result['metadata']['upload_date']}")
                            st.write(f"**飞书同步**: {'✅' if result['feishu_synced'] else '❌'}")
                    
                    with st.expander("📝 处理结果", expanded=True):
                        content = result['processed_content']
                        st.subheader(content['title'])
                        st.info(content['summary'])
                        
                        st.write("**核心观点**:")
                        for i, point in enumerate(content['core_points'], 1):
                            st.write(f"{i}. {point}")
                        
                        st.write("**详细内容**:")
                        st.write(content['detailed_content'])
                        
                        st.write("**金句**:")
                        for sentence in content['golden_sentences']:
                            st.markdown(f"> {sentence}")
                        
                        st.write("**标签**:", " ".join([f"`{tag}`" for tag in content['tags']]))
                    
                    # 下载按钮
                    markdown_path = Path(result['markdown_path'])
                    if markdown_path.exists():
                        st.download_button(
                            "📥 下载 Markdown",
                            markdown_path.read_text(encoding='utf-8'),
                            file_name=markdown_path.name,
                            mime="text/markdown"
                        )
                else:
                    error_msg = result.get('error', '未知错误')
                    st.error(f"❌ 处理失败: {error_msg}")
                    
                    # 抖音特殊错误提示
                    if platform == Platform.DOUYIN and ('Fresh cookies' in error_msg or 'Douyin' in error_msg):
                        st.warning("⚠️ 抖音下载说明")
                        st.markdown("""
                        由于抖音的反爬虫机制极其严格，即使配置了有效的 Cookies，
                        yt-dlp 也可能无法下载抖音视频。
                        
                        **建议使用以下替代方案：**
                        
                        1. **浏览器扩展下载（推荐）**
                           - Video DownloadHelper
                           - 猫抓（CoCoCut）
                        
                        2. **手机 APP 下载**
                           - 使用抖音 APP 下载视频
                           - 传输到电脑后处理
                        
                        3. **等待功能更新**
                           - 关注 yt-dlp 更新
                           - 抖音反爬虫机制可能随时变化
                        
                        详细说明请查看：`Douyin_Download_Solution.md`
                        """)
            
            except Exception as e:
                error_str = str(e)
                st.error(f"❌ 发生错误: {error_str}")
                
                # 抖音特殊错误提示
                if platform == Platform.DOUYIN and ('Fresh cookies' in error_str or 'Douyin' in error_str):
                    st.warning("⚠️ 抖音下载说明")
                    st.markdown("""
                    由于抖音的反爬虫机制极其严格，暂时无法通过程序直接下载。
                    
                    **推荐替代方案：**
                    - 使用浏览器扩展（Video DownloadHelper、猫抓）
                    - 使用手机 APP 下载后传输
                    
                    详细说明：`Douyin_Download_Solution.md`
                    """)
            
            finally:
                st.session_state.processing = False

with tab2:
    st.header("批量处理")
    
    urls_text = st.text_area(
        "视频链接（每行一个）",
        height=200,
        placeholder="https://...\nhttps://...",
        disabled=st.session_state.processing
    )
    
    if st.button("🚀 批量处理", disabled=st.session_state.processing):
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        if urls:
            st.session_state.processing = True
            st.info(f"准备处理 {len(urls)} 个视频...")
            
            # 创建处理流水线（使用当前配置）
            pipeline = ProcessingPipeline(
                ai_provider=ai_provider,
                enable_ai_polish=enable_ai_polish,
                whisper_model=whisper_model
            )
            
            try:
                results = asyncio.run(
                    pipeline.process_batch(urls)
                )
                
                success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
                st.success(f"✅ 完成！成功: {success_count}/{len(urls)}")
                
                # 显示结果摘要
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict) and result.get('success'):
                        st.write(f"{i}. ✅ {result['metadata']['title']}")
                    else:
                        error = result if isinstance(result, Exception) else result.get('error', '未知错误')
                        st.write(f"{i}. ❌ 失败: {error}")
            
            except Exception as e:
                st.error(f"❌ 批量处理失败: {str(e)}")
            
            finally:
                st.session_state.processing = False

with tab3:
    st.header("历史记录")
    
    # 列出已处理的文件
    output_files = list(config.OUTPUT_PATH.glob("*.md"))
    
    if output_files:
        st.write(f"共 {len(output_files)} 条记录")
        
        for file in sorted(output_files, key=lambda x: x.stat().st_mtime, reverse=True):
            with st.expander(f"📄 {file.stem}"):
                content = file.read_text(encoding='utf-8')
                st.markdown(content)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.download_button(
                        "下载",
                        content,
                        file_name=file.name,
                        mime="text/markdown",
                        key=f"download_{file.stem}"
                    )
    else:
        st.info("暂无历史记录")

# 页脚
st.markdown("---")
st.markdown("💡 **提示**: 首次使用需配置 `.env` 文件中的 API 密钥")
