"""
人工微调页面
"""
import streamlit as st
import time
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ui.utils.formatters import format_job_display_name
from src.ui.utils.api_client import get_job_summary, get_student_detail, update_question_score


def show_adjustment_page():
    """人工微调页面 - 优化版"""
    st.header("✏️ 人工微调")

    st.markdown(
        """
    在此页面,您可以审查AI的评分结果并进行微调。
    修改后的分数会自动同步到总分表。
    """
    )

    # 选择历史任务
    job_id = st.session_state.get("current_job_id", "")

    if st.session_state.app_jobs:
        # 如果有预设的job_id
        default_index = 0
        if job_id:
            job_ids = [job["job_id"] for job in st.session_state.app_jobs]
            if job_id in job_ids:
                default_index = job_ids.index(job_id) + 1

        # 创建任务选项映射（友好显示）
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
            key="adjustment_history_select",
        )
        if selected_job:
            job_id = selected_job
            st.session_state.current_job_id = job_id
    else:
        st.info("💡 暂无历史任务，请先创建评分任务")
        return

    if not job_id:
        st.info("👆 请先选择一个任务")
        return

    # 获取该任务的所有报告
    with st.spinner("📊 正在加载数据..."):
        summary_data = get_job_summary(job_id)
    
    if not summary_data:
        return
    
    student_ids = [item["student_id"] for item in summary_data["data"]]

    if not student_ids:
        st.warning("⚠️ 该任务暂无评分报告")
        return

    # 使用selectbox选择学生
    selected_student = st.selectbox(
        "选择学生",
        student_ids,
        format_func=lambda x: f"学生 {x}",
        key="adjustment_student_select",
    )

    if selected_student:
        st.markdown("---")
        show_student_reports_for_adjustment(job_id, selected_student)


def show_student_reports_for_adjustment(job_id: str, student_id: str):
    """显示单个学生的所有报告,支持逐题微调 - 优化版"""
    
    # 获取学生的所有报告
    with st.spinner("📊 正在加载学生数据..."):
        data = get_student_detail(job_id, student_id)
    
    if not data:
        return

    st.subheader(f"📝 学生评分报告")

    # 显示学生信息卡片
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👤 姓名", data.get("student_name", "未知"))
        with col2:
            st.metric("🆔 学号", student_id)
        with col3:
            st.metric("⚧️ 性别", data.get("student_gender", "未知"))

    # 显示总分
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 当前总分", f"{data['total_score']:.1f}")
    with col2:
        max_total = sum(q["max_score"] for q in data["questions"])
        st.metric("💯 满分", f"{max_total:.1f}")
    with col3:
        score_rate = (data["total_score"] / max_total * 100) if max_total > 0 else 0
        st.metric("📈 得分率", f"{score_rate:.1f}%")

    st.markdown("---")

    # 逐题展示
    for idx, q in enumerate(data["questions"], 1):
        # 根据得分率显示不同颜色
        score_rate = (
            (q["final_score"] / q["max_score"] * 100) if q["max_score"] > 0 else 0
        )
        if score_rate >= 80:
            color_indicator = "🟢"
        elif score_rate >= 60:
            color_indicator = "🟡"
        else:
            color_indicator = "🔴"

        with st.expander(
            f"{color_indicator} 题目 {idx}: {q['question_id']} - {q['final_score']:.1f}/{q['max_score']:.1f}分 ({score_rate:.0f}%)",
            expanded=(idx == 1),  # 默认展开第一题
        ):
            # 题目信息
            st.markdown(f"**📋 题目描述:** {q['question_description']}")

            # AI评分信息（顶部）
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🤖 AI给分", f"{q['ai_score']:.1f}")
            with col2:
                st.metric("✅ 当前生效分数", f"{q['final_score']:.1f}")
            with col3:
                diff = q["final_score"] - q["ai_score"]
                st.metric("📊 调整", f"{diff:+.1f}" if diff != 0 else "0")

            st.markdown("---")

            # 田字格布局：左列（学生作答+参考答案）| 右列（评分标准+AI评分依据）
            left_col, right_col = st.columns(2)

            with left_col:
                # 左上：学生答案
                st.markdown("**✍️ 学生答案**")
                with st.container(border=True, height=250):
                    st.write(
                        q["student_answer"]
                        if q["student_answer"]
                        else "_（未作答）_"
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

            st.markdown("---")

            # 修改按钮
            unique_key = f"edit_{job_id}_{student_id}_{q['question_id']}"

            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button(
                    f"✏️ 修改此题评分",
                    key=f"btn_{unique_key}",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state[f"editing_{unique_key}"] = True
            with col2:
                if st.session_state.get(f"editing_{unique_key}", False):
                    if st.button(
                        "❌ 取消编辑",
                        key=f"cancel_edit_{unique_key}",
                        use_container_width=True,
                    ):
                        st.session_state[f"editing_{unique_key}"] = False
                        st.rerun()

            # 如果点击了修改按钮,显示修改表单
            if st.session_state.get(f"editing_{unique_key}", False):
                st.markdown("#### 📝 修改评分")

                with st.form(key=f"form_{unique_key}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_score = st.number_input(
                            "新分数 *",
                            min_value=0.0,
                            max_value=float(q["max_score"]),
                            value=float(q["final_score"]),
                            step=0.5,
                            key=f"score_{unique_key}",
                            help=f"满分: {q['max_score']}",
                        )

                    with col2:
                        modified_by = st.text_input(
                            "修改者姓名 *",
                            value="Teacher",
                            placeholder="请输入您的姓名",
                            key=f"modifier_{unique_key}",
                        )

                    new_rationale = st.text_area(
                        "调整理由 *",
                        value=q["human_override_rationale"] or "",
                        placeholder="请说明为什么要调整分数...",
                        key=f"rationale_{unique_key}",
                        height=100,
                    )

                    col1, col2 = st.columns([1, 1])

                    with col1:
                        submitted = st.form_submit_button(
                            "💾 提交修改", type="primary", use_container_width=True
                        )

                    with col2:
                        cancelled = st.form_submit_button(
                            "❌ 取消", use_container_width=True
                        )

                    if cancelled:
                        st.session_state[f"editing_{unique_key}"] = False
                        st.rerun()

                    if submitted:
                        # 验证输入
                        if not new_rationale.strip():
                            st.error("❌ 请填写调整理由")
                        elif not modified_by.strip():
                            st.error("❌ 请填写修改者姓名")
                        else:
                            with st.spinner("💾 正在保存..."):
                                success = update_question_score(
                                    job_id, 
                                    student_id, 
                                    q['question_id'],
                                    new_score,
                                    new_rationale,
                                    modified_by
                                )
                            
                            if success:
                                st.success("✅ 修改成功! 总分表已自动同步")

                                # 清除编辑状态和缓存
                                st.session_state[f"editing_{unique_key}"] = False
                                st.cache_data.clear()

                                # 等待一秒后刷新
                                time.sleep(1)
                                st.rerun()
