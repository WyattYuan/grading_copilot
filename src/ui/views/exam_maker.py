"""
试卷制作页面
"""

import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ui.utils.formatters import calculate_total_score
from src.ui.forms.question_forms import (
    import_exam_config,
    show_add_question_form,
    show_questions_list,
    show_export_section,
)


def show_exam_maker_page():
    """试卷制作页面"""
    st.header("📝 试卷制作工具")

    st.markdown(
        """
    在此页面可以可视化地创建试卷，支持：
    - 📄 **单题**：普通题目
    - 📚 **大题+小题**：一道大题包含多道小题
    - 📥 **导出配置**：生成 exam_config.json
    - 📋 **导出模板**：生成学生作答 Markdown 模板
    """
    )

    st.markdown("---")

    if "exam_title" not in st.session_state:
        st.session_state.exam_title = "期中考试"
    if "questions_data" not in st.session_state:
        st.session_state.questions_data = []

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        exam_title = st.text_input(
            "📋 试卷标题", value=st.session_state.exam_title, key="exam_title_input"
        )
        st.session_state.exam_title = exam_title

    with col2:
        total_score = calculate_total_score(st.session_state.questions_data)
        st.metric("📊 试卷总分", f"{total_score} 分")

    with col3:
        st.metric("📚 题目数量", f"{len(st.session_state.questions_data)} 题")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ 添加单题", use_container_width=True, type="primary"):
            st.session_state.adding_question_type = "single"
            st.rerun()

    with col2:
        if st.button(
            "➕ 添加大题（含小题）", use_container_width=True, type="secondary"
        ):
            st.session_state.adding_question_type = "composite"
            st.session_state.composite_temp = {
                "id": "",
                "type": "text",
                "description": "",
                "sub_questions": [],
            }
            st.rerun()

    with col3:
        uploaded_json = st.file_uploader(
            "📂 导入已有JSON", type=["json"], key="import_json"
        )
        if uploaded_json:
            import_exam_config(uploaded_json)

    if st.session_state.get("adding_question_type"):
        show_add_question_form(st.session_state.adding_question_type)

    st.markdown("---")

    st.subheader(f"📚 题目列表")

    if st.session_state.questions_data:
        show_questions_list()
    else:
        st.info("还没有添加题目，请点击上方按钮添加")

    st.markdown("---")

    # 导出功能
    if st.session_state.questions_data:
        st.subheader("📥 导出")
        show_export_section()
