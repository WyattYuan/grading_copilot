"""
学生详情组件
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ui.utils.api_client import get_student_detail


def show_student_detail(job_id: str, student_id: str):
    """显示学生详情 - 优化版"""
    with st.spinner("📊 正在加载学生详情..."):
        data = get_student_detail(job_id, student_id)

    if not data:
        return

    # 学生信息卡片
    with st.container(border=True):
        st.markdown("### 👤 学生信息")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("姓名", data.get("student_name", "未知"))
        with col2:
            st.metric("学号", student_id)
        with col3:
            st.metric("性别", data.get("student_gender", "未知"))
        with col4:
            st.metric("总分", f"{data['total_score']:.2f}")

    st.markdown("---")
    st.markdown("### 📝 答题详情")

    # 逐题展示
    for idx, q in enumerate(data["questions"], 1):
        score_color = (
            "🟢"
            if q["final_score"] >= q["max_score"] * 0.8
            else "🟡" if q["final_score"] >= q["max_score"] * 0.6 else "🔴"
        )

        with st.expander(
            f"{score_color} 题目 {idx}: {q['question_id']} - {q['final_score']:.1f}/{q['max_score']:.1f}分",
            expanded=(idx == 1),
        ):
            # 题目信息
            st.markdown(f"**📋 题目描述:**")
            st.info(q["question_description"])

            # 评分信息（顶部）
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("AI评分", f"{q['ai_score']:.1f}分")
            with col2:
                st.metric("当前得分", f"{q['final_score']:.1f}分")
            with col3:
                score_rate = (
                    (q["final_score"] / q["max_score"] * 100)
                    if q["max_score"] > 0
                    else 0
                )
                st.metric("得分率", f"{score_rate:.1f}%")

            st.markdown("---")

            # 田字格布局：左列（学生作答+参考答案）| 右列（评分标准+AI评分依据）
            left_col, right_col = st.columns(2)

            with left_col:
                # 左上：学生答案
                st.markdown("**✍️ 学生答案**")
                with st.container(border=True, height=250):
                    st.write(
                        q["student_answer"] if q["student_answer"] else "_（未作答）_"
                    )

                # 左下：参考答案
                st.markdown("**📖 参考答案**")
                with st.container(border=True, height=250):
                    st.write(q.get("reference_answer", "_（暂无参考答案）_"))

            with right_col:
                # 右上：评分标准
                st.markdown("**📊 评分标准**")
                with st.container(border=True, height=250):
                    scoring_criteria = q.get("scoring_criteria", "")
                    if scoring_criteria:
                        st.write(scoring_criteria)
                    else:
                        st.write("_（暂无评分标准）_")

                # 右下：AI评分依据
                st.markdown("**🤖 AI评分依据**")
                with st.container(border=True, height=250):
                    st.write(q["ai_rationale"])

            # 人工调整说明（如果有）
            if q["human_override_rationale"]:
                st.markdown("---")
                st.markdown("**👨‍🏫 人工调整说明**")
                st.warning(q["human_override_rationale"])
                st.caption(f"修改者: {q['last_modified_by']}")
