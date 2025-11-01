"""
任务状态监控页面
"""

import streamlit as st
import time
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ui.utils.formatters import format_job_display_name
from src.ui.utils.api_client import get_job_status


def show_job_status_page():
    """查看任务状态页面 - 优化版"""
    st.header("📊 任务状态监控")

    # 选择历史任务
    job_id = st.session_state.get("current_job_id", "")

    if st.session_state.app_jobs:
        # 如果有预设的job_id
        default_index = 0
        if job_id:
            job_ids = [job["job_id"] for job in st.session_state.app_jobs]
            if job_id in job_ids:
                default_index = job_ids.index(job_id) + 1

        job_options_map = {"": "请选择任务..."}
        for job in st.session_state.app_jobs:
            display_name = format_job_display_name(job)
            job_options_map[job["job_id"]] = display_name

        job_options = [""] + [job["job_id"] for job in st.session_state.app_jobs]
        selected_job = st.selectbox(
            "选择任务",
            job_options,
            index=default_index,
            format_func=lambda x: job_options_map.get(x, "请选择任务..."),
            key="status_history_select",
        )
        if selected_job:
            job_id = selected_job
            st.session_state.current_job_id = job_id
    else:
        st.info("💡 暂无历史任务，请先创建评分任务")
        return

    if job_id:
        # 自动刷新控制
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            auto_refresh = st.checkbox(
                "自动刷新", value=False, key="status_auto_refresh"
            )
        with col2:
            if st.button("🔄 手动刷新", key="status_manual_refresh"):
                st.cache_data.clear()
                st.rerun()
        with col3:
            if auto_refresh:
                st.caption("⏱️ 每2秒自动刷新")

        with st.spinner("🔄 正在获取状态..."):
            status_data = get_job_status(job_id)

        if not status_data:
            return

        st.subheader(f"任务 {job_id}")

        # 状态卡片
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = status_data["status"]
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
            }
            status_color = {
                "pending": "🟡",
                "running": "🔵",
                "completed": "🟢",
                "failed": "🔴",
            }
            st.metric(
                "状态",
                f"{status_emoji.get(status, '❓')} {status}",
                delta=status_color.get(status, ""),
            )

        with col2:
            processed = status_data["processed_questions"]
            total = status_data["total_questions"]
            st.metric("进度", f"{processed}/{total}")

        with col3:
            if total > 0:
                progress = processed / total
                st.metric("完成率", f"{progress * 100:.1f}%")
            else:
                st.metric("完成率", "N/A")

        with col4:
            # 估算剩余时间（如果正在运行）
            if status == "running" and processed > 0 and total > processed:
                elapsed = (
                    datetime.now()
                    - datetime.fromisoformat(
                        status_data["created_at"].replace("Z", "+00:00")
                    )
                ).total_seconds()
                avg_time = elapsed / processed
                remaining = (total - processed) * avg_time
                st.metric("预计剩余", f"{int(remaining/60)}分{int(remaining%60)}秒")
            else:
                st.metric("预计剩余", "N/A")

        # 进度条
        if total > 0:
            progress_value = processed / total
            st.progress(progress_value, text=f"已完成 {processed}/{total} 个问题")
        else:
            st.progress(0, text="等待开始...")

        # 时间信息
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**创建时间:** {status_data['created_at']}")
        with col2:
            st.markdown(f"**更新时间:** {status_data['updated_at']}")

        # 如果失败,显示错误信息
        if status == "failed" and status_data.get("error_message"):
            st.error(f"**错误信息:** {status_data['error_message']}")
            with st.expander("🔍 查看详细错误"):
                st.code(status_data.get("error_detail", "无详细信息"))

        # 如果完成,显示跳转按钮
        if status == "completed":
            st.success("🎉 评分完成!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "📊 查看评分结果 →",
                    key="status_view_results_btn",
                    use_container_width=True,
                ):
                    st.session_state.current_job_id = job_id
                    st.session_state.active_tab = "results"
                    st.rerun()
            with col2:
                if st.button(
                    "✏️ 进行人工微调 →",
                    key="status_view_adjust_btn",
                    use_container_width=True,
                ):
                    st.session_state.current_job_id = job_id
                    st.session_state.active_tab = "adjust"
                    st.rerun()

        # 自动刷新逻辑
        if auto_refresh and status in ["pending", "running"]:
            time.sleep(2)
            st.rerun()
