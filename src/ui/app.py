"""
Streamlit 前端界面 - 重构版
模块化设计，主文件只负责路由和布局
"""

import streamlit as st
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.ui.utils.api_client import check_api_connection, load_job_history
from src.ui.components.sidebar import render_sidebar, render_delete_confirmation_dialog
from src.ui.views.exam_maker import show_exam_maker_page
from src.ui.views.new_job import show_new_job_page
from src.ui.views.job_status import show_job_status_page
from src.ui.views.results import show_results_page
from src.ui.views.adjustment import show_adjustment_page


def main():
    """主界面"""
    st.set_page_config(
        page_title="AI智能评分系统",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🎓 AI智能评分系统")

    render_delete_confirmation_dialog()

    api_status, api_message = check_api_connection()

    if not api_status:
        st.error(api_message)
        st.info("💡 请先运行后端API服务：`uv run python run_api.py`")
        st.stop()

    with st.expander("🔌 系统状态", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("后端服务", "运行中 ✅")
        with col2:
            st.metric("API地址", f"{config.API_HOST}:{config.API_PORT}")
        with col3:
            if st.button("🔄 刷新状态", key="refresh_api_status"):
                st.cache_data.clear()
                st.rerun()

    if "app_jobs" not in st.session_state:
        st.session_state.app_jobs = load_job_history()

    if "config_max_history_items" not in st.session_state:
        st.session_state.config_max_history_items = 5

    render_sidebar()
    render_navigation()

    st.markdown("---")

    render_active_page()


def render_navigation():
    """渲染页面导航栏"""
    tab_options = {
        "📝 试卷制作": "exam_maker",
        "📤 新建评分任务": "new_job",
        "📊 任务状态": "status",
        "📋 评分结果": "results",
        "✏️ 人工微调": "adjust",
    }

    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "exam_maker"

    nav_cols = st.columns(5)
    for idx, (display_name, page_id) in enumerate(tab_options.items()):
        with nav_cols[idx]:
            button_type = (
                "primary" if page_id == st.session_state.active_tab else "secondary"
            )
            if st.button(
                display_name,
                key=f"nav_{page_id}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state.active_tab = page_id
                st.rerun()


def render_active_page():
    """根据当前标签渲染对应页面"""
    active_tab = st.session_state.get("active_tab", "exam_maker")

    if active_tab == "exam_maker":
        show_exam_maker_page()
    elif active_tab == "new_job":
        show_new_job_page()
    elif active_tab == "status":
        show_job_status_page()
    elif active_tab == "results":
        show_results_page()
    elif active_tab == "adjust":
        show_adjustment_page()
    else:
        show_exam_maker_page()


if __name__ == "__main__":
    main()
