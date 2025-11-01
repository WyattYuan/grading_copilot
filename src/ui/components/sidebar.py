"""
侧边栏组件 - AI配置和任务历史
"""

import streamlit as st
import time
import os
import requests
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.config import config
from src.ui.utils.api_client import load_job_history, delete_job, API_BASE_URL
from src.ui.utils.formatters import format_job_display_name


def render_sidebar():
    """渲染侧边栏内容"""
    with st.sidebar:
        # AI 配置区域
        render_ai_config()

        st.markdown("---")

        # 任务历史区域
        render_job_history()


def render_ai_config():
    """渲染 AI 配置区域"""
    st.header("AI 配置")

    with st.expander("⚙️ API 设置", expanded=False):
        # 初始化配置
        if "api_key" not in st.session_state:
            st.session_state.api_key = config.OPENAI_API_KEY
        if "model_name" not in st.session_state:
            st.session_state.model_name = config.OPENAI_MODEL

        # API Key 输入
        api_key_input = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="输入您的 OpenAI 或通义千问 API Key",
            help="支持 OpenAI 或阿里云通义千问 API",
            key="api_key_input",
        )

        # 模型选择
        model_options = [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "qwen-plus",
            "qwen-turbo",
            "qwen-max",
        ]

        # 如果当前模型不在列表中，添加到列表
        if st.session_state.model_name not in model_options:
            model_options.insert(0, st.session_state.model_name)

        model_index = (
            model_options.index(st.session_state.model_name)
            if st.session_state.model_name in model_options
            else 0
        )

        model_input = st.selectbox(
            "模型名称",
            options=model_options,
            index=model_index,
            help="选择要使用的 AI 模型",
            key="model_name_select",
        )

        # 自定义模型名称
        use_custom_model = st.checkbox("使用自定义模型名称", value=False)
        if use_custom_model:
            model_input = st.text_input(
                "自定义模型",
                value=model_input,
                placeholder="例如: gpt-4-1106-preview",
                key="custom_model_input",
            )

        # 保存按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 保存配置", type="primary", use_container_width=True):
                # 验证 API Key
                if not api_key_input or api_key_input.strip() == "":
                    st.error("❌ API Key 不能为空")
                else:
                    # 保存到 session_state
                    st.session_state.api_key = api_key_input
                    st.session_state.model_name = model_input

                    # 同时更新 config（用于 API 调用）
                    config.OPENAI_API_KEY = api_key_input
                    config.OPENAI_MODEL = model_input

                    # 保存到环境变量（可选，当前会话有效）
                    os.environ["OPENAI_API_KEY"] = api_key_input
                    os.environ["OPENAI_MODEL"] = model_input

                    # 发送配置到 API 端
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/config/update",
                            json={
                                "api_key": api_key_input,
                                "model_name": model_input,
                            },
                            timeout=5,
                        )
                        if response.status_code == 200:
                            st.success("✅ 配置已保存并同步到 API！")
                        else:
                            st.warning(
                                f"⚠️ 配置已保存，但同步到 API 失败: {response.text}"
                            )
                    except Exception as e:
                        st.warning(f"⚠️ 配置已保存，但无法连接到 API: {str(e)}")

                    time.sleep(1)
                    st.rerun()

        with col2:
            if st.button("🔄 重置", use_container_width=True):
                st.session_state.api_key = config.OPENAI_API_KEY
                st.session_state.model_name = config.OPENAI_MODEL
                st.rerun()

        # 显示当前配置状态
        st.markdown("---")
        st.caption("📊 当前配置")
        has_key = bool(st.session_state.api_key and st.session_state.api_key.strip())
        st.write(f"**API Key:** {'✅ 已配置' if has_key else '❌ 未配置'}")
        st.write(f"**模型:** {st.session_state.model_name}")

        if not has_key:
            st.warning("⚠️ 请先配置 API Key 才能使用评分功能")


def render_job_history():
    """渲染任务历史区域"""
    st.header("📋 任务历史")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🔄 刷新列表", use_container_width=True):
            st.cache_data.clear()  # 清除缓存
            st.session_state.app_jobs = load_job_history()
            st.rerun()
    with col2:
        if st.button("⚙️", help="设置", use_container_width=True):
            st.session_state.show_settings = not st.session_state.get(
                "show_settings", False
            )

    # 设置面板
    if st.session_state.get("show_settings", False):
        with st.container(border=True):
            st.caption("⚙️ 显示设置")
            st.session_state.config_max_history_items = st.slider(
                "历史任务显示数量",
                min_value=3,
                max_value=20,
                value=st.session_state.config_max_history_items,
                key="history_items_slider",
            )

    # 搜索功能
    search_query = st.text_input(
        "🔍 搜索任务", placeholder="输入任务ID或考试名称...", key="job_search"
    )

    if st.session_state.app_jobs:
        # 过滤任务
        filtered_jobs = st.session_state.app_jobs
        if search_query:
            filtered_jobs = [
                job
                for job in st.session_state.app_jobs
                if search_query.lower() in job["job_id"].lower()
                or search_query.lower() in job.get("exam_title", "").lower()
            ]

        if filtered_jobs:
            st.caption(f"显示 {len(filtered_jobs)} 个任务")

            # 显示任务
            max_items = st.session_state.config_max_history_items
            for job in filtered_jobs[:max_items]:
                render_job_card(job)

            if len(filtered_jobs) > max_items:
                st.caption(f"还有 {len(filtered_jobs) - max_items} 个任务未显示")
        else:
            st.warning(f"未找到匹配「{search_query}」的任务")
    else:
        st.info("暂无历史任务")


def render_job_card(job):
    """渲染单个任务卡片"""
    status = job.get("status", "unknown")
    status_emoji = {
        "pending": "⏳",
        "running": "🔄",
        "completed": "✅",
        "failed": "❌",
    }.get(status, "❓")

    # 构建更友好的任务标题
    exam_title = job.get("exam_title", "未命名考试")
    created_time = job.get("created_at", "")[:10] if job.get("created_at") else ""

    # 主标题：考试标题 + 日期
    task_title = f"{status_emoji} {exam_title}"
    if created_time:
        task_title += f" ({created_time})"

    with st.expander(task_title, expanded=False):
        # 显示任务ID（折叠后可见）
        st.caption(f"任务ID: {job['job_id']}")

        # 任务信息
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**状态:** {status}")
            st.write(f"**学生数:** {job.get('student_count', 0)}")
        with col2:
            if job.get("created_at"):
                st.caption(f"创建时间: {job['created_at'][:19]}")
            if status == "completed":
                st.success("✅ 已完成")
            elif status == "running":
                progress = job.get("processed_questions", 0)
                total = job.get("total_questions", 1)
                st.progress(
                    progress / total if total > 0 else 0,
                    text=f"{progress}/{total}",
                )

        # 快捷操作按钮
        st.markdown("---")

        # 主操作按钮 - 查看结果/状态
        if st.button(
            ("📊" if status == "completed" else "📊 查看状态"),
            key=f"view_{job['job_id']}",
            use_container_width=True,
            type=("primary" if status == "completed" else "secondary"),
        ):
            st.session_state.current_job_id = job["job_id"]
            if status == "completed":
                st.session_state.active_tab = "results"
            else:
                st.session_state.active_tab = "status"
            st.rerun()

        # 辅助操作按钮 - 微调和删除
        col1, col2 = st.columns(2)
        with col1:
            if status == "completed":
                if st.button(
                    "✏️",
                    key=f"adjust_{job['job_id']}",
                    use_container_width=True,
                ):
                    st.session_state.current_job_id = job["job_id"]
                    st.session_state.active_tab = "adjust"
                    st.rerun()
            else:
                # 占位，保持布局一致
                st.empty()
        with col2:
            if st.button(
                "🗑️",
                key=f"delete_{job['job_id']}",
                use_container_width=True,
                help="删除此任务",
            ):
                # 弹出确认对话框
                st.session_state.confirm_delete_job_id = job["job_id"]
                st.session_state.confirm_delete_exam_title = exam_title
                st.rerun()


def render_delete_confirmation_dialog():
    """渲染删除确认对话框"""
    if st.session_state.get("confirm_delete_job_id"):

        @st.dialog("确认删除任务")
        def confirm_delete():
            job_id = st.session_state.confirm_delete_job_id
            exam_title = st.session_state.get("confirm_delete_exam_title", "未命名考试")

            st.warning(f"⚠️ 您确定要删除任务吗？")
            st.write(f"**任务名称**: {exam_title}")
            st.write(f"**任务ID**: `{job_id}`")
            st.error("🗑️ 此操作将永久删除以下数据：")
            st.markdown(
                """
            - 上传的学生答卷文件
            - 所有评分报告
            - 任务状态信息
            
            **此操作不可撤销！**
            """
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 确认删除", type="primary", use_container_width=True):
                    success = delete_job(job_id)
                    if success:
                        st.success("✅ 任务已删除")

                        # 清除状态
                        del st.session_state.confirm_delete_job_id
                        if "confirm_delete_exam_title" in st.session_state:
                            del st.session_state.confirm_delete_exam_title

                        # 刷新任务列表
                        st.cache_data.clear()
                        st.session_state.app_jobs = load_job_history()

                        time.sleep(0.5)
                        st.rerun()

            with col2:
                if st.button("❌ 取消", use_container_width=True):
                    del st.session_state.confirm_delete_job_id
                    if "confirm_delete_exam_title" in st.session_state:
                        del st.session_state.confirm_delete_exam_title
                    st.rerun()

        confirm_delete()
